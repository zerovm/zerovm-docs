import os
import math

inp_dir = '/dev/in'

total = 0
max_count = 0

data = []

for inp_file in os.listdir(inp_dir):
    with open(os.path.join(inp_dir, inp_file)) as fp:
        for line in fp:
            count, filename = line.split()
            count = int(count)
            if count > max_count:
                max_count = count
            data.append((count, filename))
            total += count

fmt = '%%%sd %%s' % (int(math.log10(max_count)) + 2)

for count, filename in data:
    print fmt % (count, filename)
print fmt % (total, 'total')
