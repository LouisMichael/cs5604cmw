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
keywords
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

        if any(conditions):
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
#    if element
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

    """
    metadata_f = outpath+"cmwf17test_metadata.tsv"
    webpage_f = outpath+"cmwf17test_webpage.tsv"
    cleanwebpage_f = outpath+"cmwf17test_cleanwebpage.tsv"
    """
    output_f = outpath+"cmwf17test.tsv"
    
    metadata_c = ["url-timestamp", "doc-type"]
    webpage_c = ["url-timestamp", "url", "html", "language", "title", "author/publisher","organization-name", "create-time", "domain-name" , "domain-location", "sub-urls", "fetch-time"]
    cleanwebpage_c = ["url-timestamp", "clean-text", "clean-text-profanity", "keywords"]
    
    output_c = metadata_c + webpage_c + cleanwebpage_c 

    """
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
    """
    if not os.path.isfile(output_f):
        with open(output_f, "w") as sumf:
            sumf.write("\t".join(output_c)+"\n")
        #print("New tsv file! ")    
    sumf = open(output_f, "ab")
              
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
                
                ## clean-text-profanity
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
                
                newline_list = [theKey]
                
                newline_m = ["webpage"]
                newline_w = [theKey, url, webhtml, lan, webtitle, webAuthor, webOrganization, webCreatedate, domain_name, domain_location, sub_urls, ts]
                newline_c = [theKey, webtext, webtext_profanity, webKeywords]
                
                newline_list += newline_m + newline_w + newline_c
                
                newline = "\t".join(newline_list)+"\n"
                sumf.write(newline.encode('utf8'))
                
            except Exception as e:
                print(e)
            print('-----------')
