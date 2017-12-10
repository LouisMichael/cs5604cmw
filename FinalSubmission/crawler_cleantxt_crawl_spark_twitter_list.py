import re
import requests
from bs4 import BeautifulSoup, Comment
import sys
import os
import codecs
import urllib
import csv

## for timestamp
import time
## for language list
from langdetect import detect_langs

## extract domain name
if sys.version_info[0] == 3:
    ## for python3, use:  
    from urllib.parse import urlparse
else:
    ## for python2, use:
    from urlparse import urlparse

## For:
## tokenization
## stopwords removing
## stemming
## lemmatization
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.regexp import WordPunctTokenizer
from nltk import FreqDist,sent_tokenize
from nltk.corpus import stopwords

## For:
## ner problems
from nltk.tag.stanford import StanfordNERTagger 
#from nltk.tag.corenlp import CoreNLPNERTagger 

## for config
import crawler_cleantxt_config_twitter as config

## for platform detecting
import platform

## To ignore warnings
import warnings
warnings.filterwarnings("ignore")

## For Pyspark
from pyspark import SparkContext, SparkConf
sc = SparkContext()

"""
Rewritten base on:
1. EFC written by Mohamed to have similar clean text output as EFC
2. articleDateExtractor_L.py by Ran Geva
3. webclean2.py by 2016fall team

Input: A text file contains URLs

Output: 
One tsv file for each column family
        
Usage: python crawler_cleantxt.py <inputURLFile>

Always remember to change the config file when crawling a new file. 
Especially the COL_EVENT which represents the collection-name.
"""

"""
main function
"""


if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'ignore')

"""
Input clean text
Output: 
list of tokens
without stopwords
"""
def getTokens(texts):
    #global corpusTokens
    #global docsTokens
    tokenizer = WordPunctTokenizer()
    
    allTokens=[]
    #tokens=[]
    if type(texts) != type([]):
        texts = [texts]
    for s in texts:
        #toks = nltk.word_tokenize(s.lower())
        toks = tokenizer.tokenize(s)
        allTokens.extend(toks)
        #corpusTokens.extend(toks)
        #docsTokens.append(toks)
   
    allTokens = [t.lower() for t in allTokens if t.isalnum() and t not in stopwordsList]
    #allTokens_2 = [t.lower() for t in allTokens if len(t)>2 and t.isalnum() and t not in stopwordsList]
    #allTokens_an = [t2 for t2 in allTokens_2 if t2.isalnum()]
    #allTokens_stw = [t3 for t3 in allTokens if t3 not in stopwordsList]
    #allTokens_stw = [t3 for t3 in allTokens_an if t3 not in stopwordsList]
    #allTokens_stw]
    final = [t for t in allTokens if t not in stopwordsList]
    return final
  
"""
Input: tokenized list
Output: POS
"""
def getPOS(allTokens):    
    POS = nltk.pos_tag(allTokens)
    return ["{}:{}".format(i,j) for i,j in POS]

"""
Input: tokenized list
Output: stemmed tokens
"""
def getStemmed(allTokens):
    stemmer = PorterStemmer()
    allTokens_stem = [stemmer.stem(word) for word in allTokens]
    return allTokens_stem

"""
Input: tokenized list
Output: lemmatized tokens
"""
def getLemmatized(allTokens):
    wordnet_lemmatizer = WordNetLemmatizer()
    allTokens_lemmatize = [wordnet_lemmatizer.lemmatize(word) for word in allTokens]
    return allTokens_lemmatize    

"""
Input: 
Output: list of NERs
"""
def getNERs(allTokens, pltfrm = "linux"):
    nerDict = {
    "person":"",
    "org":"",
    "location":""
    }
    st = StanfordNERTagger("/home/cs5604f17_cmw/testCMW/stanfordner/classifiers/english.all.3class.distsim.crf.ser.gz", "/home/cs5604f17_cmw/testCMW/stanfordner/stanford-ner.jar")
    tags = st.tag(allTokens)
    #tags_ners = [i for i,j in tags if j != 'O']
    nerDict['person'] = [i for i,j in tags if j == 'PERSON']
    nerDict['org'] = [i for i,j in tags if j == 'ORGANIZATION']
    nerDict['location'] = [i for i,j in tags if j == 'LOCATION']
    return nerDict
    
    
    
"""
Function to get sub_urls
"""
def getSubURL(parsedHTML):
    URL_regexp = re.compile( r'https?://[a-zA-Z0-9\./-]+' )
    links = parsedHTML.find_all('a')
    urls = []
    for link in links :
        if link.get('href') :
           urls += re.findall(URL_regexp,link.get('href'))
    return urls

"""
Functions to get info from meta names:

author/publisher
organization-name (copyright)
create-time
keywords
"""
def extractMetaName(parsedHTML, url):
    metas = {
    "author":"",
    "copyright":"",
    "publishDate":"",
    "keywords":"",
    "url":url,
    }
    for meta in parsedHTML.find_all("meta"):
        metaName = meta.get('name', '').lower()     
        ## author
        if 'author' == metaName and ('content' in meta):
            metas['author'] = meta['content'].strip()
            
        ## copyright
        if 'copyright' == metaName and ('content' in meta):
            metas['copyright'] = meta['content'].strip()
            
        if 'keywords' == metaName and ('content' in meta):
            metas['keywords'] = meta['content'].strip()
            
        if "og:url" == metaName and ('content' in meta):
            metas['url'] = meta['content'].strip()
                        
            
        ## Various ways to extract publish date
        metaName = meta.get('name', '').lower()
        itemProp = meta.get('itemprop', '').lower()
        httpEquiv = meta.get('http-equiv', '').lower()
        metaProperty = meta.get('property', '').lower()
        
        conditions = (
        'pubdate' == metaName,
        'publishdate' == metaName,
        'timestamp' == metaName,
        'dc.date.issued' == metaName,
        'article:published_time' == metaProperty,
        'article:published_time' == metaName,
        'date' == metaName, 
        'bt:pubdate' == metaProperty,
        'sailthru.date' == metaName,
        'article.published' == metaName,
        'published-date' == metaName,
        'article.created' == metaName,
        'article_date_original' == metaName,
        'cxenseparse:recs:publishtime' == metaName,
        'date_published' == metaName,
        'datepublished' == itemProp,
        'datecreated' == itemProp,
        'date' == httpEquiv,
        )

        #<meta name="pubdate" content="2015-11-26T07:11:02Z" >
        #<meta name='publishdate' content='201511261006'/>            
        #<meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
        #<meta name="DC.date.issued" content="2015-11-26">           
        #<meta property="article:published_time"  content="2015-11-25" />
        #<meta name="Date" content="2015-11-26" />
        #<meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
        #<meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
        #<meta name="article.published" content="2015-11-26T11:53:00.000Z" />
        #<meta name="published-date" content="2015-11-26T11:53:00.000Z" />
        #<meta name="article.created" content="2015-11-26T11:53:00.000Z" />
        #<meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
        #<meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
        #<meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        #<meta itemprop="datecreated" content="2015-11-26T11:53:00.000Z" />
        #<meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">

        if any(conditions) and ('content' in meta):
            metas['publishDate'] = meta['content'].strip()
            

      
    
    return metas
    
"""
Function to get:
clean-text-profanity
"""
def cleanTextProfanity(content):
    with open('profanity_en.txt') as f:
        __profanity_words__ = f.read()[:-1].split('\n')
        
    ProfanityRegexp = re.compile(
        r'(?<=^|(?<=[^a-zA-Z0-9-\.]))(' # Non word character starting
        + '|'.join(__profanity_words__) # Profanity word list
        + r')(?=$|\W)', re.IGNORECASE ) # End with string end or non word character
    
    return re.sub( ProfanityRegexp , '{"profanity"}', content )
    
"""
Functions to get:

raw html
clean text
title
"""
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'iframe']:
        return False
    return True
   
def getTxt(htmlPage):
 
    #soup = BeautifulSoup(htmlPage)
    soup = BeautifulSoup(htmlPage,"lxml")

    title = ""
    text = ""
    if soup.title:
        if soup.title.string:
            title = soup.title.string

    text_nodes = soup.findAll(text=lambda text: not isinstance(text, Comment))
    #text_nodes = soup.findAll(text=True)
    #text_nodes_noLinks = soup.findAll(text=True)
    visible_text = filter(visible, text_nodes)
    
    text = "\n".join(visible_text)
    #textSents = getSentences(text)
    #text = "\n".join(textSents)
    text = title + '\n' + text
    return text,title

    
    
def extractTextFromHTML(page):
    
    #try:
    
    text = ''
    title = ''
    if page:
        text,title = getTxt(page)
    if text.strip():
        wtext = {"text":title + u' '+ text,"title":title}
        #wtext = {'text':text}
    else:
        #print 'No Text in page'#, page
        wtext = {}
    return wtext
    
    
def getWebpageText(url, r = ""):
    #webpagesText = []
    text = {
    "html":"",
    "text":"",
    "title":"",
    "type":"",
    }
    #if r and r.status_code == requests.codes.ok:
        #ct = r.headers['Content-Type']
    ct = r.headers.get('Content-Type','')
    if ct.find('text/html')!= -1:
        page = r.content
        text = extractTextFromHTML(page)
        text["type"] = ct
        if text:
            text['html']= page
        else:
            print('No Text to be extracted from: ', url)
            text["text"] = "2000"
    else:
        #text = {}
        print('Content-Type is not text/html', ct," - ", url) 
        text["type"] = ct
        text["text"] = "1001"
    #else:
    #    print('Could not download:', url)
    #
        #text = {}
#         except Exception as e:
#             raise e
#             print sys.exc_info()
        #text = ""
        #text = {}
    #webpagesText.append(text)
#return webpagesText
    return text
    
## If needed
## Alternative way: 
## sys.platform.lower().startswith("win")
## sys.platform.lower().startswith("linux")
## sys.platform.lower().startswith("linux")
def platformDetector():
    if platform.win32_ver()[0]:
        return "windows"
    elif platform.mac_ver()[0]:
        return "macintosh"
    #elif "ANDROID_PRIVATE" in os.environ:
    #    return "android"
    # missing: os.condition
    else:
        return "linux"

def statusCodeWriter(st_code, url, ct = ""):
    ts = str(time.time())
    theKey = url+"-"+ts
    print('Could not download:', url, " status code: ", st_code)
    return [ct, st_code, theKey, url]

    
    

          
## test 
# url = "https://www.washingtonpost.com/solar-eclipse-2017/"

def crawl(url):
    if url.endswith(".jpg"):
        st_code = "1001"
        ct = "image/jpg"
        return statusCodeWriter(st_code, url, ct)
    try:
        r = requests.get(url.strip(),timeout=10,verify=False,headers=headers) 
        ## If the status code is 4XX or 5XX
        if r.status_code != requests.codes.ok:
            st_code = "0"+str(r.status_code)
            return statusCodeWriter(st_code, url)  
        return [r, url]
    except Exception as e:
        ## If there is not even a status code
        print(e)
        st_code = "2001"
        return statusCodeWriter(st_code, url)
        
    



if __name__ == "__main__":
 
    ## Start time 
    timestart = time.time()
    log_name = "crawling_twitter_%s" %time.time()
    

    
    outpath = config.OUTPATH
    #outfn = config.OUTFN
    
    #col_event = config.COL_EVENT
    #col_id = config.COL_ID[col_event]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    
    stopwordsList = stopwords.words('english') + ["profanity"]
    pltfrm = platformDetector()

    """
    metadata_f = outpath+"cmwf17test_metadata.tsv"
    webpage_f = outpath+"cmwf17test_webpage.tsv"
    cleanwebpage_f = outpath+"cmwf17test_cleanwebpage.tsv"
    """
    output_f = outpath + sys.argv[1].split(".")[0]+"_rst.tsv"
    
    metadata_c = ["doc-type", "collectoion-id", "collection-name", "database", "source"]
    webpage_c = ["url", "html", "language", "title", "author/publisher","organization-name", "create-time", "domain-name" , "domain-location", "sub-urls", "fetch-time", "mime-type", "status-code", "tweet_ids"]
    cleanwebpage_c = ["clean-text", "clean-text-profanity", "keywords", "tokens", "stemmed", "lemmatized","POS", "sner-people", "sner-organization", "sner-location", "real-world-events"]
    
    output_c = ["url-timestamp"] + metadata_c + webpage_c + cleanwebpage_c 


    if not os.path.isfile(output_f):
        with open(output_f, "w") as sumf:
            sumf.write("\t".join(output_c)+"\n")
        #print("New tsv file! ")    
    sumf = open(output_f, "ab")
              
    ## test 
    # url = "https://www.washingtonpost.com/solar-eclipse-2017/"
    #twi_ids = []
    #col_events = []
    #col_ids = []
    urls = []     
    url_info = {}
    
    f = csv.reader(open(sys.argv[1], "rU"), delimiter = ",")
    
    for line in f:
        #twi_ids.append(line[0])
        #col_ids.append(line[1])
        #col_events.append(line[2])
        url = line[3].replace("\n","")
        urls.append(url)
        if url in url_info:
            url_info[url][0].append(line[0])
        else:
            url_info[url] = [[line[0]],line[1],line[2]]

    all_urls = list(set(urls))
    
    n_parts = len(all_urls)//1000 + 1
    #if n_parts == 0:
    #    n_parts = 1
    
    print("n_parts",n_parts)
    """PySpark"""
    
    for part in range(1, n_parts+1):
        if len(all_urls) >= 1000:
            urls = all_urls[:1000]
            del all_urls[:1000]
        else: 
            urls = all_urls
        print("len(urls)",len(urls))
               
        timestart_c = time.time()
        rddAll = sc.parallelize(urls)
        result = rddAll.map(lambda x: crawl(x)).collect()
        
        timeend_c = time.time()
        time_diff_c = timeend_c - timestart_c
        
        counter = len(urls)
        
        cmd = "echo unique crawled url size: %s crawling time: %s input CSV file: %s >> log_%s.txt" %(counter, time_diff_c, sys.argv[1], log_name)
        os.system(cmd)
        # To run: 
        # PYSPARK_PYTHON=/opt/cloudera/parcels/Anaconda/bin/python spark-submit test.py
        
        # https://spark.apache.org/docs/1.1.1/api/python/pyspark.rdd.RDD-class.html
        # The reduce() function seems to be used to reduce the elements in rdd
        for idx in range(len(result)):
            ts = str(time.time())
            st_code = "0"+str(200)
            url = result[idx][-1]
            ## Type: list
            twi_ids = url_info[url][0]
            ## Type: str
            col_id = url_info[url][1]
            col_event = url_info[url][2]
            if len(result[idx]) > 2:
                st_code = result[idx][0]
                ct = result[idx][1]
                theKey = result[idx][2]
                newline_list = [theKey] + [""]*(len(metadata_c)-2)+ [col_id] + [col_event] + [""]*(len(webpage_c)-3) + [ct] + [st_code] + twi_ids + [""]*len(cleanwebpage_c)
                newline = "\t".join(newline_list)+"\n"
                try:
                    newline.encode('utf8')
                    sumf.write(newline)
                except:
                    print("wrong encoding", url)
                continue            
            try:
                ## Type: dict
                ## dict keys: html, title, text
                r = result[idx][0]
                webdict = getWebpageText(urls[idx], r)
                webtype = webdict['type']
                if webdict['text'] in ["1001","2000","2001"]:
                    st_code = webdict['text']
                    rst = statusCodeWriter(st_code, url)
                    st_code = rst[0]
                    ct = rst[1]
                    theKey = rst[2]
                    newline_list = [theKey] + [""]*(len(metadata_c)-2)+ [col_id] + [col_event] + [""]*(len(webpage_c)-3) + [ct] + [st_code] + twi_ids + [""]*len(cleanwebpage_c)
                    newline = "\t".join(newline_list)+"\n"
                    try:
                        newline.encode('utf8')
                        sumf.write(newline)
                    except:
                        print("wrong encoding", url)
                    continue
                webhtml = webdict['html']
                webtext = webdict['text']
                webtitle = webdict['title']
                webhtml_parsed = BeautifulSoup(webhtml, 'lxml' )

                print("Title: "+webtitle)
                print("URL: "+url)

                ## clean-text-profanity to process
                webtext_profanity = cleanTextProfanity(webtext)

                ## Tokenization and remove stopwords
                webtokens = getTokens(webtext_profanity)
                ## POS, this is tricky when encode = utf8
                try:
                    webPOS = getPOS(webtokens)
                except:
                    webPOS = [""]
                ## Stemming and lemmatization
                #print(webstem)
                webstem = getStemmed(webtokens)
                #weblemma = rddtokens.map(lambda x: getLemmatized_rdd(x, wordnet_lemmatizer)).collect()
                weblemma = getLemmatized(webtokens)
                ## NERs
                """Potential Spark mark"""
                nerDict = getNERs(webtokens, pltfrm)
                #nerDict = {
                #'person':'',
                #'org':'',
                #'location':''
                #}
                nerPerson = ";".join(nerDict['person'])
                nerOrg = ";".join(nerDict['org'])
                nerLocation = ";".join(nerDict['location'])
                ## list to string
                webtokens = ",".join(webtokens)
                webstem = ",".join(webstem)
                weblemma = ",".join(weblemma)
                webPOS = ",".join(webPOS)
                
                ## Extract domain_name and domain_location
                ## We might need some mapping to get valid domain location
                parsed_uri = urlparse(url)
                domain_name = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                domain_location = domain_name.split('.')[-1][:-1]
                invalid_domains = ["com","net","edu","org"]
                if domain_location in invalid_domains:
                    domain_location = ""
        
                
                ## Return extracted information from meta name
                ## If there is a original URL
                metadict = extractMetaName(webhtml_parsed, url)
                url = metadict['url']
                
                webAuthor = metadict['author']
                webOrganization = metadict['copyright']
                webCreatedate = metadict['publishDate']
                webKeywords = metadict['keywords']
                
                ## Return list of sub URLs
                sub_urls = getSubURL(webhtml_parsed)
                sub_urls = ";".join(sub_urls)
                
                ## Returns a language list with prob
                ## ['en:0.9999974122572912']
                try:
                    lan = [str(i).split(":")[0] for i in detect_langs(webtext)]
                    #lan = [""]
                except:
                    lan = [""]
                lan = ",".join(lan)
                
                ## A few cleaning
                webtext = webtext.replace("\n",".")
                webtext = webtext.replace("\r",".")
                webtext = webtext.replace("\t",".")
                
                webhtml = webhtml.decode('utf-8')
                webhtml = webhtml.replace("\n",".")
                webhtml = webhtml.replace("\r",".")
                webhtml = webhtml.replace("\t",".")
                
                url = url.replace("\n","")
                url = url.replace("\r","")
                url = url.replace("\t","")
                
                webtitle = webtitle.replace("\n",".")
                webtitle = webtitle.replace("\r",".")
                webtitle = webtitle.replace("\t",".")
                
                ## clean-text-profanity to write
                webtext_profanity = cleanTextProfanity(webtext)

                

                ## Our key: URL+timestamp
                theKey = url+"-"+ts
                
                ## Write tsv files
                """
                newline_list = [theKey,"webpage"]
                newline = "\t".join(newline_list)+"\n"
                sumf_metadata.write(newline.encode('utf8'))
                
                newline_list = [theKey, url, webhtml, lan, webtitle, webAuthor, webOrganization, webCreatedate, domain_name, domain_location, sub_urls, ts]
                newline = "\t".join(newline_list)+"\n"
                sumf_webpage.write(newline.encode('utf8'))
                
                newline_list = [theKey, webtext, webtext_profanity, webKeywords]
                newline = "\t".join(newline_list)+"\n"
                sumf_cleanwebpage.write(newline.encode('utf8'))
                """
                
                twi_ids = ",".join(twi_ids)
                
                newline_list = [theKey]
                
                newline_m = ["webpage", col_id, col_event, "Collect_yTK", "yTK"]
                newline_w = [url, webhtml, lan, webtitle, webAuthor, webOrganization, webCreatedate, domain_name, domain_location, sub_urls, ts, webtype, st_code, twi_ids]
                newline_c = [webtext, webtext_profanity, webKeywords, webtokens, webstem, weblemma, webPOS, nerPerson, nerOrg, nerLocation, col_event.replace("#","")]
                
                newline_list += newline_m + newline_w + newline_c
                
                newline = "\t".join(newline_list)+"\n"
                sumf.write(newline.encode('utf8'))
                

                print('-----------')
            except Exception as e:
                st_code = "2001"
                rst = statusCodeWriter(st_code, url)
                st_code = rst[0]
                ct = rst[1]
                theKey = rst[2]
                newline_list = [theKey] + [""]*(len(metadata_c)-2)+ [col_id] + [col_event] + [""]*(len(webpage_c)-3) + [ct] + [st_code] + twi_ids + [""]*len(cleanwebpage_c)
                newline = "\t".join(newline_list)+"\n"
                try:
                    newline.encode('utf8')
                    sumf.write(newline)
                except:
                    print("wrong encoding", url)
                print(e)
    ## End time
    counter = len(urls)
    timeend = time.time()
    time_diff = timeend - timestart
    cmd = "echo total time: %s >> log_%s.txt" %(time_diff, log_name)
    os.system(cmd)
    