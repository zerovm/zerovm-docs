import base64
import hashlib
import imp
import json
import os
import random
import sqlite3
import string
import StringIO
import sys
import urlparse
import wsgiref.handlers

import falcon


def http_resp(code, reason, content_type='message/http', msg='',
              extra_headers=None):
    if extra_headers is None:
        extra_header_text = ''
    else:
        extra_header_text = '\r\n'.join(
            ['%s: %s' % (k, v) for k, v in extra_headers.items()]
        )
        extra_header_text += '\r\n'

    resp = """\
HTTP/1.1 %(code)s %(reason)s\r
%(extra_headers)sContent-Type: %(content_type)s\r
Content-Length: %(msg_len)s\r
\r
%(msg)s"""
    resp %= dict(code=code, reason=reason, content_type=content_type,
                 msg_len=len(msg), msg=msg, extra_headers=extra_header_text)
    sys.stdout.write(resp)


class Job(object):

    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.devices = [
            {'name': 'python2.7'},
            {'name': 'stdout', 'content_type': 'message/http'},
            {'name': 'image', 'path': 'swift://~/snakebin-app/snakebin.zapp'},
        ]
        self.env = {}

    def add_device(self, name, content_type=None, path=None):
        dev = {'name': name}
        if content_type is not None:
            dev['content_type'] = content_type
        if path is not None:
            dev['path'] = path
        self.devices.append(dev)

    def set_envvar(self, key, value):
        self.env[key] = value

    def to_json(self):
        return json.dumps([self.to_dict()])

    def to_dict(self):
        return {
            'name': self.name,
            'exec': {
                'path': 'file://python2.7:python',
                'args': self.args,
                'env': self.env,
            },
            'devices': self.devices,
        }


def _object_exists(name):
    """Check the local container (mapped to `/dev/input`) to see if it contains
    an object with the given ``name``. /dev/input is expected to be a sqlite
    database.
    """
    conn = sqlite3.connect('/dev/input')
    try:
        cur = conn.cursor()
        sql = 'SELECT ROWID FROM object WHERE name=? AND deleted=0'
        cur.execute(sql, (name, ))
        result = cur.fetchall()
        return len(result) > 0
    finally:
        conn.close()


def random_short_name(seed, length=10):
    rand = random.Random()
    rand.seed(seed)
    name = ''.join(rand.sample(string.ascii_lowercase
                               + string.ascii_uppercase
                               + string.digits, length))
    return name


def _handle_script(req, resp, account, container, script, execute=False):
    # Go get the requested script, or 404 if it doesn't exist.
    if _object_exists(script):
        private_file_path = 'swift://~/snakebin-store/%s' % script

        job = Job('snakebin-get-file', 'get_file.py')
        job.add_device('input', path=private_file_path)
        job.set_envvar('HTTP_ACCEPT', os.environ.get('HTTP_ACCEPT'))
        if execute:
            job.set_envvar('SNAKEBIN_EXECUTE', 'True')
        # Setting this header and content_type will make ZeroCloud
        # intercept the request and spawn a new job, instead of responding
        # directly to the client.
        resp.set_header('X-Zerovm-Execute', '1.0')
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = job.to_json()
    else:
        resp.status = falcon.HTTP_404


def _handle_script_upload(req, resp, account, container, script=None):
    file_data = req.stream.read()
    file_hash = hashlib.sha1(file_data)
    short_name = random_short_name(file_hash.hexdigest())

    snakebin_file_path = 'swift://~/snakebin-store/%s' % short_name
    public_file_path = 'swift://~/snakebin-api/%s' % short_name

    if _object_exists(short_name):
        # This means the file already exists. No problem!
        # Since the short url is derived from the hash of the contents,
        # just return a URL to the file.
        path = '/api/%s/%s/%s' % (account, container, short_name)

        file_url = urlparse.urlunparse((
            'http',
            os.environ.get('HTTP_HOST'),
            path,
            None,
            None,
            None
        )) + '\n'
        resp.status = falcon.HTTP_200
        resp.body = file_url
    else:
        # Go and save the file.
        # We need to spawn another ZeroVM job to write this file.
        job = Job('snakebin-save-file', 'save_file.py')
        job.set_envvar('SNAKEBIN_POST_CONTENTS',
                       base64.b64encode(file_data))
        job.set_envvar('SNAKEBIN_PUBLIC_FILE_PATH', public_file_path)
        job.add_device('output', path=snakebin_file_path,
                       content_type='text/plain')
        # Setting this header and content_type will make ZeroCloud
        # intercept the request and spawn a new job, instead of responding
        # directly to the client.
        resp.set_header('X-Zerovm-Execute', '1.0')
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = job.to_json()


def execute_code(code):
    # Patch stdout, so we can capture output from the submitted code
    old_stdout = sys.stdout
    new_stdout = StringIO.StringIO()
    sys.stdout = new_stdout

    # Create a module with the code
    module = imp.new_module('dontcare')
    module.__name__ = "__main__"

    # Execute the submitted code
    exec code in module.__dict__

    # Read the response from the code
    new_stdout.seek(0)
    output = new_stdout.read()

    # Unpatch stdout
    sys.stdout = old_stdout

    return output


class RootHandler(object):

    def on_get(self, req, resp, account, container):
        """Serve a blank index.html page."""
        with open('index.html') as fp:
            resp.body = fp.read()
        resp.content_type = 'text/html; charset=utf-8'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, account, container):
        """Handle the form post/script upload."""
        _handle_script_upload(req, resp, account, container)


class ScriptHandler(object):

    def on_get(self, req, resp, account, container, script):
        _handle_script(req, resp, account, container, script)

    def on_post(self, req, resp, account, container, script):
        if script == 'execute':
            file_data = req.stream.read()
            resp.content_type = 'text/plain'
            resp.status = falcon.HTTP_200
            resp.body = execute_code(file_data)
        else:
            # Also allow new/modified scripts to be uploaded when the client is
            # on a page like `/snakebin-api/Wg4re8mXbV`.
            _handle_script_upload(req, resp, account, container, script=script)


class ScriptExecuteHandler(object):

    def on_get(self, req, resp, account, container, script):
        _handle_script(req, resp, account, container, script, execute=True)


if __name__ == '__main__':
    app = falcon.API()
    app.add_route('/{account}/{container}', RootHandler())
    # Handles `POST /{account}/{container}/execute` as well
    app.add_route('/{account}/{container}/{script}', ScriptHandler())
    app.add_route('/{account}/{container}/{script}/execute',
                  ScriptExecuteHandler())

    handler = wsgiref.handlers.SimpleHandler(
        sys.stdin,
        sys.stdout,
        sys.stderr,
        environ=dict(os.environ),
        multithread=False,
    )
    handler.run(app)
