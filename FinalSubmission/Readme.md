
# cs5604cmw

## File overview:

### 1. crawler_cleantxt_advanced_alone.py  
Crawler + cleaner without PySpark.   
#### Input:   
A single .txt file, list of URLs  
#### Usage:   
$ python crawler_cleantxt_advanced.py <inputURLFile>   
On cluster:  
$ /opt/cloudera/parcels/Anaconda/bin/python crawler_cleantxt_advanced.py <inputURLFile>    
#### Config file:   
crawler_cleantxt_config.py   
Always remember to **change the config file** when crawling a new file.   
Especially the **COL_EVENT** which represents the collection-name.


### 2. crawler_cleantxt_stem_spark.py   
Parallel stemming using PySpark.  
#### Input:    
A single .txt file, list of URLs    
#### Usage on cluster:    
$ PYSPARK_PYTHON=/opt/cloudera/parcels/Anaconda/bin/python spark-submit crawler_cleantxt_stem_spark.py <inputURLFile>
#### Config file:   
crawler_cleantxt_config.py  


### 3. crawler_cleantxt_crawl_spark.py   
Parallel crawling using PySpark.  
#### Input:    
A single .txt file, list of URLs    
#### Usage on cluster:    
$ PYSPARK_PYTHON=/opt/cloudera/parcels/Anaconda/bin/python spark-submit crawler_cleantxt_crawl_spark.py <inputURLFile>
#### Config file:   
crawler_cleantxt_config.py  


### 4. crawler_cleantxt_crawl_spark_twitter_list.py   
Parallel crawling using PySpark for Twitter collections.  
#### Input:    
.csv tweet collection files fetched from HBase. **No need** to perform dupliction elimination beforehand.  
#### Usage on cluster:    
$ PYSPARK_PYTHON=/opt/cloudera/parcels/Anaconda/bin/python spark-submit crawler_cleantxt_crawl_spark_twitter_list.py <inputURLFile>
#### Config file:   
crawler_cleantxt_config_twitter.py

### 5. crawler_cleantxt_advanced.py   
Only used to be intergrated in EFC. See the details in the following section. 

### 6. nerphrase.py   
NER dectection function to perform "next to each other stratege": if two neighbour words have the same detected NER property, they will be put together as one phrase. 

## Details about crawler_cleantxt_\*.py 

#### Dependencies:
Put following files in the same directory:  
* profanity_en.txt  
* stanford-ner

*We inherited profanity_en.txt from 2016's class*  
*The standford-ner can be downloaded from: https://nlp.stanford.edu/software/CRF-NER.html*  

#### Use together with EFC:
As mentioned before, put following dependencies in the same directory:  
* crawler_cleantxt_advanced.py  
* crawler_cleantxt_config.py  
* profanity_en.txt  
* nerClassifier  
* stanford-ner-2017-06-09  

Add one line in EFC/utils:  
`import crawler_cleantxt_advanced as cln`

Change one line in EFC/utils.getWebpageText()  
`r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)`  
to:  
`r = cln.main(url, efc = True)`  

The integrated version is under folder EFC_with_cleaning.   

Usage:  
$python FocusedCrawler.py b model.txt seed.txt

#### Supported:
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
webpage   mime-type [image/jpg, image/png, text/html,...]    
webpage  status-code [0200, 0404, 0502, 1001, 2001, ...]    

*See the config file for our self-defined status codes*

clean-webpage   clean-text   
clean-webpage   clean-text-profanity  
clean-webpage   real-world-events [same as collection-name for EFC URLs]   
clean-webpage  tokens [stopwords removed tokens based on clean-text-profanity]   
clean-webpage stemmed [stemmed tokens]     
clean-webpage  lemmatized  [lemmatized tokens]     
clean-webpage   sner-people  
clean-webpage   sner-organization  
clean-webpage   sner-location  
clean-webpage  POS   
clean-webpage  keywords [keywords in meta tags, could be inaccurate]   

*These features starting from "tokens" are supported by library: nltk    
stopwords are the default english stopwords supported by nltk. To handle relatively high frequency of word "profanity" in clean-text-profanity, "profanity" is added to our stopwords list. *


##### To be updated if needed:
webpage   domain-location   
*Use GeoIP to generate a bounding box at country level   
Or recognize the location of copyright organization   
For now, we leave locations in sner-location to be processed*

