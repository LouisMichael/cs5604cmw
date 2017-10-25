import re
import requests
from bs4 import BeautifulSoup, Comment
import sys
import os
import codecs
## for timestamp
import time
## for language list
from langdetect import detect_langs

## extract domain name
## for python3, use:
#from urllib.parse import urlparse
## for python2, use:
from urlparse import urlparse




"""
Rewritten base on:
1. EFC written by Mohamed to have similar clean text output as EFC
2. articleDateExtractor_L.py by Ran Geva
3. webclean2.py by 2016fall team

Input: A text file contains URLs

Output: 
One tsv file for each column family
		
Usage: python crawler_cleantxt.py <inputURLFile>
"""


if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'ignore')

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

"""
def extractMetaName(parsedHTML):
    metas = {
    "author":"",
    "copyright":"",
    "publishDate":"",
    "keywords":"",
    }
    for meta in parsedHTML.find_all("meta"):
        metaName = meta.get('name', '').lower()     
        ## author
        if 'author' == metaName:
            metas['author'] = meta['content'].strip()
            
        ## copyright
        if 'copyright' == metaName:
            metas['copyright'] = meta['content'].strip()
            
        if 'keywords' == metaName:
            metas['keywords'] = meta['content'].strip()
                        
            
        ## Various ways to extract publish date
        metaName = meta.get('name', '').lower()
        itemProp = meta.get('itemprop', '').lower()
        httpEquiv = meta.get('http-equiv', '').lower()
        metaProperty = meta.get('property', '').lower()
        
        #<meta name="pubdate" content="2015-11-26T07:11:02Z" >
        if 'pubdate' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name='publishdate' content='201511261006'/>
        elif 'publishdate' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
        elif 'timestamp' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="DC.date.issued" content="2015-11-26">
        elif 'dc.date.issued' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta property="article:published_time"  content="2015-11-25" />
        elif 'article:published_time' == metaProperty:
            metas['publishDate'] = meta['content'].strip()
            
        elif 'article:published_time' == metaName:
            metas['publishDate'] = meta['content'].strip()
            
            #<meta name="Date" content="2015-11-26" />
        elif 'date' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
        elif 'bt:pubdate' == metaProperty:
            metas['publishDate'] = meta['content'].strip()
            
            #<meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
        elif 'sailthru.date' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="article.published" content="2015-11-26T11:53:00.000Z" />
        elif 'article.published' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="published-date" content="2015-11-26T11:53:00.000Z" />
        elif 'published-date' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="article.created" content="2015-11-26T11:53:00.000Z" />
        elif 'article.created' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
        elif 'article_date_original' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
        elif 'cxenseparse:recs:publishtime' == metaName:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
        elif 'date_published' == metaName:
            metas['publishDate'] = meta['content'].strip()
            


        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        elif 'datepublished' == itemProp:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta itemprop="datecreated" content="2015-11-26T11:53:00.000Z" />
        elif 'datecreated' == itemProp:
            metas['publishDate'] = meta['content'].strip()
            

        #<meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">
        elif 'date' == httpEquiv:
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
    if element.parent.name in ['style', 'script', '[document]', 'head']:
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
    

    
    text_nodes = soup.findAll(text=True)
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
    }
    if r and r.status_code == requests.codes.ok:
        #ct = r.headers['Content-Type']
        ct = r.headers.get('Content-Type','')
        if ct.find('text/html')!= -1:
            page = r.content
            text = extractTextFromHTML(page)
            if text:
                text['html']= page
            else:
                print('No Text to be extracted from: ', url)
        else:
            #text = {}
            print('Content-Type is not text/html', ct," - ", url) 
            text = ""
    else:
        print('Could not download:', url)
        text = ""
        #text = {}
#         except Exception as e:
#             raise e
#             print sys.exc_info()
        #text = ""
        #text = {}
    #webpagesText.append(text)
#return webpagesText
    return text

"""
main function
"""
if __name__ == "__main__":

    outpath = "output/"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}


    metadata_f = outpath+"cmwf17test_metadata.tsv"
    webpage_f = outpath+"cmwf17test_webpage.tsv"
    cleanwebpage_f = outpath+"cmwf17test_cleanwebpage.tsv"
    
    metadata_c = ["url-timestamp", "doc-type"]
    webpage_c = ["url-timestamp", "url", "html", "language", "title", "author/publisher","organization-name", "create-time", "domain-name" , "domain-location", "sub-urls", "fetch-time"]
    cleanwebpage_c = ["url-timestamp", "clean-text", "clean-text-profanity", "keywords"]

    
    if not os.path.isfile(metadata_f):
        with open(metadata_f, "w") as sumf:
            sumf.write("\t".join(metadata_c)+"\n")
            
    if not os.path.isfile(webpage_f):
        with open(webpage_f, "w") as sumf:
            sumf.write("\t".join(webpage_c)+"\n")
            
    if not os.path.isfile(cleanwebpage_f):
        with open(cleanwebpage_f, "w") as sumf:
            sumf.write("\t".join(cleanwebpage_c)+"\n")
        #print("New tsv file! ")    

        

    sumf_metadata = open(metadata_f, "ab")
    sumf_webpage = open(webpage_f, "ab")       
    sumf_cleanwebpage = open(cleanwebpage_f, "ab")
              
    ## test 
    # url = "https://www.washingtonpost.com/solar-eclipse-2017/"
    
    with open(sys.argv[1]) as f:
        for url in f:
            url = url.replace("\n","")
            print(url)
            try:
                content = requests.get(url.strip(),timeout=10,verify=False,headers=headers) 
                ts = str(time.time())
            except:
                content ='' 
                print('Could not download:', url)
                continue
            try:
                ## Type: dict
                ## dict keys: html, title, text
                webdict = getWebpageText(url, content)
                if not webdict:
                    print('No Text to be extracted from: ', url)
                    continue
                webhtml = webdict['html']
                webtext = webdict['text']
                webtitle = webdict['title']
                webhtml_parsed = BeautifulSoup(webhtml, 'lxml' )
                print("Title: "+webtitle)
                
                ## Extract domain_name and domain_location
                ## We might need some mapping to get valid domain location
                parsed_uri = urlparse(url)
                domain_name = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                domain_location = domain_name.split('.')[-1][:-1]
                invalid_domains = ["com","net","edu","org"]
                if domain_location in invalid_domains:
                    domain_location = ""
        
                
                ## Return extracted information from meta name
                metadict = extractMetaName(webhtml_parsed)
                
                webAuthor = metadict['author']
                webOrganization = metadict['copyright']
                webCreatedate = metadict['publishDate']
                webKeywords = metadict['keywords']
                
                ## Return list of sub URLs
                sub_urls = getSubURL(webhtml_parsed)
                sub_urls = ";".join(sub_urls)
                
                ## Returns a language list with prob
                ## ['en:0.9999974122572912']
                lan = [str(i) for i in detect_langs(webtext)]
                lan = ",".join(lan)
                
                ## clean-text-profanity
                webtext_profanity = cleanTextProfanity(webtext)
                
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
                
                webtitle = webtitle.replace("\t",".")

                ## Our key: URL+timestamp
                theKey = url+"-"+ts
                
                ## Write tsv files
                newline_list = [theKey,"webpage"]
                newline = "\t".join(newline_list)+"\n"
                sumf_metadata.write(newline.encode('utf8'))
                
                newline_list = [theKey, url, webhtml, lan, webtitle, webAuthor, webOrganization, webCreatedate, domain_name, domain_location, sub_urls, ts]
                newline = "\t".join(newline_list)+"\n"
                sumf_webpage.write(newline.encode('utf8'))
                
                newline_list = [theKey, webtext, webtext_profanity, webKeywords]
                newline = "\t".join(newline_list)+"\n"
                sumf_cleanwebpage.write(newline.encode('utf8'))
                
            except Exception as e:
                print(e)
            print('-----------')
