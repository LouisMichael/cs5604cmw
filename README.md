# cs5604cmw

### Code developed for retrieving and processing webpages as is relevant for CS5604

Further information is discussed in our ongoing paper which can be found [here](https://www.overleaf.com/11453323jhcyxdhjjsvj#/43271700/ "paper")

#### File overview:
cleanTextPy2 -  This folder is a first crack at getting our cleaning and fetching python to run the meat of the folder is `crawler_cleantextPy2.py` which is the a python script that takes in a list of urls and scraps and cleans their html to produce a csv or relevant information  

cleanTextPy3 -  This is currently the most up to date version of our python script and it is what should be examined and expanded on

Note: Originally there was believed to be a version issue which is why the above folders are named 2 and 3 respectively this is a misnomer however both files should be run with a python 2.7 interpreter. Also both of these directors currently have empty subdirectories for output while we work on determining how to upload large files to our github and getting git-lfs to work

otherOutput - This a folder that contains additional output, it is currently empty while we determine how to upload large files into our github

urls - this directory contains lists of urls that are fed into our scripts to clean and fetch 

`Load_HTML.pig` - This file is a [pig](https://pig.apache.org/) script to load a .csv which is already in HDFS into HBase. This process in the future is going to be done in a yet unwritten bash script since the SOLR team provided a command line way of loading the file. 

`README.md` - You're reading this file right now, update this with new info you want to share about this repo

`crawler_cleantext.py` - basic crawler and cleaner, updated version in cleanTextPy3

`crawler_cleantexPy2.py` - deprecated version of the crawler and cleaner, possibility this is erased

output_irma and vegas - The raw output of crawls for Hurricane Irma and The recent Las Vegas shooting. 

`profanity_en.txt` - Our profanity blacklist, these are words and phrases that get eliminated when we clean for profanity

`solar_urls.txt` - shorter URL list about the 2017 solar eclipse

`urlFetchPython.py` - a simple python URL fetcher, does not do any cleaning

`wgetBash` -  a bash script to fetch URLs this has been replaced with a python script
#### Useful commands:

In order to put output information 

`hdfs dfs -put localfile /user/hadoop/hadoopfile`

`scan 'tablename' , {COLUMNS => 'cfamily:cqualifier'}`

`scan 'cmwf17-test' , {COLUMNS => 'webpage:cleantext'}`

making a table in HBase

### Current crawler_cleantext_advanced.py 11/06/17

##### Supported:
metadata   doc-type  
metadata   collection-id  
metadata   collection-name 

webpage   html  
webpage   language   [language:confidence, language:confidence]   
webpage   url  [og:url if exists]
webpage   title  
webpage   author/publisher  
webpage   sub-urls   [url;url]  
webpage   create-time  
webpage   domain-name  
webpage   domain-location  
webpage   organization-name  
webpage   fetch-time  [UnixTime]  
webpage   mime-type [image/jpg, image/png, html/txt,...]
webpage  status-code [0200, 0404, 0502, 1000, ...]
*See the config file for our self-defined status codes*

clean-webpage   clean-text   
clean-webpage   clean-text-profanity  
clean-webpage   real-world-events [same as collection-name for EFC URLs]
clean-webpage  tokens [tokenized and stopwords removed]   
clean-webpage  lemmatized    [stemmed and lemmatized using tokens]  
clean-webpage   sner-people  
clean-webpage   sner-organization  
clean-webpage   sner-location  
clean-webpage  POS   
*These features starting from "tokens" are supported by library: nltk*  

*Where to find collection-id:
http://hadoop.dlib.vt.edu:81/twitter/
http://hadoop.dlib.vt.edu:82/twitter/*

##### To be updated if needed:
webpage   domain-location   
*Use GeoIP to generate a bounding box at country level   
Or recognize the location of copyright organization   
For now, we leave locations in sner-location to be processed*

### Current write to hbase bash command
hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.separator='   ' -Dimporttsv.columns="HBASE_ROW_KEY,metadata:doc-type,webpage:url,webpage:html,webpage:language,webpage:title,webpage:author/publisher,webpage:organization-name,webpage:create-time,webpage:domain-name,webpage:domain-location,webpage:sub-urls,webpage:fetch-time,cleanwebpage:clean-text,cleanwebpage:clean-text-profanity,cleanwebpage:keywords,cleanwebpage:tokens,cleanwebpage:lemmatized,cleanwebpage:POS,cleanwebpage:sner-people,cleanwebpage:sner-organization,cleanwebpage:sner-location" table_name cmwf17test.tsv
