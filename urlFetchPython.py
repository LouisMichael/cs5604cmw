import urllib2
import sys
out = open('html.csv', 'w')
out.write('url, html')
with open(sys.argv[1]) as f:
    for line in f:
        try:
            response = urllib2.urlopen(line)
            html = response.read()
            html = html.replace('\n', '')
            html = html.replace('\r', '')
            html = html.replace(',', '')
            line = line.replace('\n', '')
            line = line.replace('\r', '')
            print line
            out.write(line +','+ html + '\n')
        except Exception as e:
            print e
        
print '\n'
