import os
from xml.sax.saxutils import escape

import snakebin


if __name__ == '__main__':
    with open('/dev/input') as fp:
        contents = fp.read()

    http_accept = os.environ.get('HTTP_ACCEPT', '')
    if 'text/html' in http_accept:
        # Something that looks like a browser is requesting the document:
        with open('/index.html') as fp:
            html_page_template = fp.read()
            html_page = html_page_template.replace('{code}', escape(contents))
        snakebin.http_resp(200, 'OK', content_type='text/html; charset=utf-8',
                           msg=html_page)
    else:
        # Some other type of client is requesting the document:
        snakebin.http_resp(200, 'OK', content_type='text/plain', msg=contents)
