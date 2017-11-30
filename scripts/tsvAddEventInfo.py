import sys

sumf = open(argv[5], "ab")
with open(sys.argv[1]) as f:
        for line in f:
            line += "\t" + argv[2] + "\t" + argv[3] + "\t" + argv[4] + "\n"
            sumf.write(line.encode('utf8'))
