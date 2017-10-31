#written in python 3

import builtins
import os
import sys
import warc
import warcat.model
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator
import requests
from time import gmtime, strftime
import lzma

def convert_to_warc(website, filename):
	with open(filename + '.warc.gz', 'wb') as output:
		writer = WARCWriter(output, gzip=True)
		
		resp = requests.get(website,
                        headers={'Accept-Encoding': 'identity'},
                        stream=True)
						
		# get raw headers from urllib3
		headers_list = resp.raw.headers.items()


		http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')

		record = writer.create_warc_record(website, 'response',
                                   payload=resp.raw,
                                   http_headers=http_headers)
								   
		writer.write_record(record)


#move to directory with the URL text file
modelFileName = sys.argv[1].replace("input/", "").replace(".txt", "")
os.chdir("output")
os.chdir("input")
os.chdir(modelFileName)
os.chdir("base-webpages")

urls = {}
urlCount = 0

for line in open("base-Output-URLS.txt", "r"):
	urls["url-" + str(urlCount)] = line.rstrip('\n')
	urlCount = urlCount + 1

if not os.path.exists("Warc_Records"):
	os.makedirs("Warc_Records")

os.chdir("Warc_Records")
	
for key, value in urls.items():
	convert_to_warc(value, key)

	
for i in range(0, urlCount):
	data = open("url-" + str(i) + ".warc.gz", "rb").read()
	records = data.split(b"WARC/0.17")
	first = True
	for rec in records:
		with lzma.open("WarcFile.warc", "ab", preset=9) as o:
			if first:
				first = False
			else:
				o.write(b"WARC/0.17")
			o.write(rec)
	
print("WARC Files Created")