import os

with open('/dev/input') as fp:
    contents = fp.read()

search_term = os.environ.get('SNAKEBIN_SEARCH')

if search_term in contents:
    document_name = os.environ.get('LOCAL_PATH_INFO').split('/')[-1]
    doc_url = 'http://%(host)s/api/%(acct)s/%(cont)s/%(short_name)s\n'
    doc_url %= dict(host=os.environ.get('HTTP_HOST'), cont='snakebin-api',
                   acct=os.environ.get('PATH_INFO').strip('/'),
                   short_name=document_name)

    with open('/dev/out/search-reducer', 'a') as fp:
        fp.write(doc_url)
