import os

import sys
import warc
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter
import requests


#move to directory with the URL text file
#one directory dependant on what the text file was named
modelFileName = sys.argv[1].replace("input/", "").replace(".txt", "")
os.chdir("output")
os.chdir("input")
os.chdir(modelFileName)
os.chdir("base-webpages")

urls = []

for line in open("base-Output-URLS.txt", "r"):
    urls.append(line.rstrip('\n'))

#convert_to_warc(value, key)
with open(modelFileName + '.warc.gz', 'wb') as output:
    writer = WARCWriter(output, gzip=True)
    for url in urls:
						
        resp = requests.get(url,
            headers={'Accept-Encoding': 'identity'},
            stream=True)
						
        # get raw headers from urllib3
        headers_list = resp.raw.headers.items()


        http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')

        record = writer.create_warc_record(url, 'response',
            payload=resp.raw,
            http_headers=http_headers)
								   
        writer.write_record(record)

	
print "WARC Files Created"