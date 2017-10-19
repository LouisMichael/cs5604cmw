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

`solar_urls.txt` - shorter URL list about the 2017 solar eclipse

`urlFetchPython.py` - a simple python URL fetcher, does not do any cleaning

`wgetBash` -  a bash script to fetch URLs this has been replaced with a python script
#### Useful commands:

In order to put output information 

`hdfs dfs -put localfile /user/hadoop/hadoopfile`

`scan 'tablename' , {COLUMNS => 'cfamily:cqualifier'}`

`scan 'cmwf17-test' , {COLUMNS => 'webpage:cleantext'}`

making a table in HBase

