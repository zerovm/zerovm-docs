import base64
import os

import snakebin


def save_file(post_contents, public_file_path):
    script_contents = base64.b64decode(post_contents)

    with open('/dev/output', 'a') as fp:
        fp.write(script_contents)

    _rest, container, short_name = public_file_path.rsplit('/', 2)
    file_url = 'http://%(host)s/api/%(acct)s/%(cont)s/%(short_name)s\n'
    file_url %= dict(host=os.environ.get('HTTP_HOST'), cont=container,
                     acct=os.environ.get('PATH_INFO').strip('/'),
                     short_name=short_name)

    snakebin.http_resp(201, 'Created', msg=file_url)


if __name__ == '__main__':
    post_contents = os.environ.get('SNAKEBIN_POST_CONTENTS')
    public_file_path = os.environ.get('SNAKEBIN_PUBLIC_FILE_PATH')

    save_file(post_contents, public_file_path)
