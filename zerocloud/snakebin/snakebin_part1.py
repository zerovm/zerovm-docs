import base64
import hashlib
import json
import os
import random
import sqlite3
import string
import sys
import urlparse


def http_resp(code, reason, content_type='message/http', msg='',
              extra_headers=None):
    if extra_headers is None:
        extra_header_text = ''
    else:
        extra_header_text = '\n'.join(
            ['%s: %s' % (k, v) for k, v in extra_headers.items()]
        )
        extra_header_text += '\n'

    resp = """\
HTTP/1.1 %(code)s %(reason)s
%(extra_headers)sContent-Type: %(content_type)s
Content-Length: %(msg_len)s

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
        return json.dumps([{
            'name': self.name,
            'exec': {
                'path': 'file://python2.7:python',
                'args': self.args,
                'env': self.env,
            },
            'devices': self.devices,
        }])


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


def post():
    with open('/dev/stdin') as fp:
        file_data = fp.read()

    request_path = os.environ.get('PATH_INFO')
    file_hash = hashlib.sha1(file_data)
    short_name = random_short_name(file_hash.hexdigest())

    snakebin_file_path = 'swift://~/snakebin-store/%s' % short_name
    public_file_path = 'swift://~/snakebin-api/%s' % short_name

    if _object_exists(short_name):
        # This means the file already exists. No problem!
        # Since the short url is derived from the hash of the contents, just
        # return a URL to the file.
        _, acct, container, _rest = (
            request_path + '/').split('/', 4)
        path = '/api/%s/%s/' % (acct, container)

        file_url = urlparse.urlunparse((
            'http',
            os.environ.get('HTTP_HOST'),
            (path + short_name),
            None,
            None,
            None
        )) + '\n'
        http_resp(200, 'OK', msg=file_url)
    else:
        job = Job('snakebin-save-file', 'save_file.py')
        job.set_envvar('SNAKEBIN_POST_CONTENTS', base64.b64encode(file_data))
        job.set_envvar('SNAKEBIN_PUBLIC_FILE_PATH', public_file_path)
        job.add_device('output', path=snakebin_file_path,
                       content_type='text/plain')
        http_resp(200, 'OK', content_type='application/json',
                  msg=job.to_json(), extra_headers={'X-Zerovm-Execute': '1.0'})


def get():
    path_info = os.environ.get('PATH_INFO')
    path_parts = path_info.split('/')

    file_name = None
    if len(path_parts) >= 4:
        _, _account, container, file_name = path_parts
    elif len(path_parts) == 3:
        _, _account, container = path_parts

    if container == 'snakebin-api':
        if not file_name:
            # Get empty form page:
            with open('index.html') as fp:
                index_page = fp.read()
            http_resp(200, 'OK', content_type='text/html; charset=utf-8',
                      msg=index_page)
        elif _object_exists(file_name):
            # The client has requested a real document.
            # Spawn a job to go and retrieve it:
            private_file_path = 'swift://~/snakebin-store/%s' % file_name

            job = Job('snakebin-get-file', 'get_file.py')
            job.add_device('input', path=private_file_path)
            job.set_envvar('HTTP_ACCEPT', os.environ.get('HTTP_ACCEPT'))

            http_resp(200, 'OK', content_type='application/json',
                      msg=job.to_json(),
                      extra_headers={'X-Zerovm-Execute': '1.0'})
        else:
            http_resp(404, 'Not Found')
    else:
        http_resp(404, 'Not Found')


if __name__ == '__main__':
    request_method = os.environ.get('REQUEST_METHOD')

    if request_method == 'POST':
        post()
    elif request_method == 'GET':
        get()
    else:
        http_resp(405, 'Method Not Allowed')
