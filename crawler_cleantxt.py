import re
import requests
from bs4 import BeautifulSoup, Comment
import sys
import os
import codecs
import json


"""
Modified base on the EFC written by Mohamed to have similar clean text output as EFC

Input: A text file contains URLs
Output: One cleaned text file per web page (current file name: url)
		One summary json file: text, html, title
		
Usage: python crawler_cleantxt.py <inputURLFile>
"""


if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'ignore')


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
    
    
def getWebpageText(URLs = []):
    #webpagesText = []
    text = {
    "html":"",
    "text":"",
    "title":"",
    }
    if type(URLs) != type([]):
        URLs = [URLs]
    for url in URLs:
        try:
            r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)     
        except:
            r =''       
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
        else:
            print('Could not download:', url)
            #text = {}
#         except Exception as e:
#             raise e
#             print sys.exc_info()
            #text = ""
            #text = {}
        #webpagesText.append(text)
    #return webpagesText
    return text


if __name__ == "__main__":

    outpath = "output/"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    
    if not os.path.isfile(outpath+"summary.json"):
        print("New summary file! ")
    
    
    sumf = open(outpath+"summary.json", "a")
              
    with open(sys.argv[1]) as f:
        for url in f:
            print(url)
            try:
                ## Type: list[dict]
                ## Dict keys: html, title, text
                webdict = getWebpageText(url)
                if not webdict:
                    print('No Text to be extracted from: ', url)
                    continue
                webhtml = webdict['html']
                webtext = webdict['text']
                webtitle = webdict['title']
                
                ## A few cleanning
                webtext = webtext.replace("\n",".")
                webtext_notabs = webtext.replace("\t"," ")
                
                # fn = webtitle.replace("/","_")
                ## Should be able to be done by RE
                fn = url.split("://")[1]
                fn = fn.replace("/","_")
                fn = fn.replace(" ","_")
                fn = fn.replace("?","_")
                fn = fn.replace(",","_")
                fn = fn.replace("<","_")
                fn = fn.replace(">","_")
                fn = fn.replace(":","")
                fn = fn.replace("\r","")
                fn = fn.replace("\n","")
                
                ## Write seperate text files for other teams
                with open(outpath+fn+".txt","wb") as ftext:
                    ftext.write(webtext.encode("utf-8"))
                json.dump(webdict, sumf)
            except Exception as e:
                print(e)
            print('\n')