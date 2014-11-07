import os

# Word count:
with open('/dev/input') as fp:
    data = fp.read()

with open('/dev/out/reduce', 'a') as fp:
    path_info = os.environ['LOCAL_PATH_INFO']

    # Split off the swift prefix
    # Just show the container/file
    shorter = '/'.join(path_info.split('/')[2:])
    # Pipe the output to the reducer:
    print >>fp, '%d %s' % (len(data.split()), shorter)
