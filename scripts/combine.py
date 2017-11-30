import sys
import codecs

sumf = open(sys.argv[4], "ab")

with open(sys.argv[1]) as f:
        for line in f:
            sumf.write(line)
with open(sys.argv[2]) as f:
        for line in f:
            sumf.write(line)
with open(sys.argv[3]) as f:
        for line in f:
            sumf.write(line)