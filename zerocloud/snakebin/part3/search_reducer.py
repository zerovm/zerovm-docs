import json
import os

import snakebin

inp_dir = '/dev/in'

results = []
for inp_file in os.listdir(inp_dir):
    with open(os.path.join(inp_dir, inp_file)) as fp:
        result = fp.read().strip()
        if result:
            results.append(result)

snakebin.http_resp(200, 'OK', content_type='application/json',
                   msg=json.dumps(results))
