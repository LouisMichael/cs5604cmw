'''
Created on May 12, 2016

@author: mmagdy
'''
from operator import itemgetter
import re
from math import sqrt

import requests
from bs4 import BeautifulSoup, Comment
from nltk.stem.porter import PorterStemmer
from nltk.tokenize.regexp import WordPunctTokenizer
from nltk import FreqDist,sent_tokenize
from nltk.corpus import stopwords
from articleDateExtractor_L import extractArticlePublishedDate as getPubDate
from dateutil.parser import parse
import pytz
import ner

from _collections import defaultdict
import requests_cache

#requests_cache.install_cache('fc_cache', backend='sqlite')


stopwordsList = stopwords.words('english')
#stopwordsList.extend(["last","time","week","favorite","home","search","follow","year","account","update","com","video","close","http","retweet","tweet","twitter","news","people","said","comment","comments","share","email","new","would","one","world"])
stopwordsList.extend(["com","http","retweet","tweet","twitter","news","people","world","video","said"])

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}#'Digital Library Research Laboratory (DLRL)'}

#from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings()


def getDomain(url):
    domain = ""
    ind = url.find("//")
    if ind != -1 :
        domain = url[ind+2:]
        ind = domain.find("/")
        domain = domain[:ind]
    return domain

def getVocabFromDocs(docs,docFreqThresh = 5):
    # docs is a list of text strings
    docsDics = []
    vocab = defaultdict(list)
    for txt in docs:
        docTks = getTokens(txt)
        docDic = getFreq(docTks)
        docsDics.append(docDic)
        for docTerm,f in docDic.items():
            #vocab[docTerm]+= docDic[docTerm]
            vocab[docTerm].append(f)
        
    
    
    #vocabTks = [(t,len(v),sum(v)) for t,v in vocab.items() if len(v)>=docFreqThresh]
    vocabTks = [(t,len(v)*sum(v)) for t,v in vocab.items() if len(v)>=docFreqThresh]
    #vocabFreq = 
    vocabTksSrt = getSorted(vocabTks, 1)
    #print vocabTksSrt
    return vocabTksSrt,docsDics

def getDateScore(wpDateStr,eventDate,evtType = 'Shooting',yearsTolerance = 1,monthsTolerance=1):
    # come up with a value that tells how much the date can predict the relevance of webpage
    # i.e. comparing the date of webpage with event date and give a score and see how that score predicts the true label
    #yearsTolerance = 1
    #numDaysTol = 366.0 * yearsTolerance
    numDaysTol = 30 * monthsTolerance
    #evtType = 'Shooting'
    #eventDateStr = '2015/12/02'
    #print eventDateStr, wpDateStr
    #print wpDateStr
    if wpDateStr=='None':
        return 0
    
    if type(wpDateStr) == type(""):
        wpDate = parse(wpDateStr)
    else:
        wpDate = wpDateStr
    #print wpDate
    
    wpDate = wpDate.replace(tzinfo = pytz.utc)
    #print wpDate
    #wpDate = parse('2013/1/1')
    dateDiff = wpDate - eventDate
    dateDiff_days = dateDiff.days
    
    if dateDiff_days > numDaysTol:#i.e the webpage date is after the event date with more than the num of months tolerance
        return 0
    
    dateRatio = 1
    #if evtType == 'Hurricane':
        
    if dateDiff_days >= 0:
        dateRatio = dateDiff_days / numDaysTol
    elif evtType == 'Hurricane':
        dateRatio = -1 * dateDiff_days / float(numDaysTol)
    
    dateScore = 1 - dateRatio
    return dateScore

def getPublishingDate(url,html=None):
    pd = getPubDate(url, html)
    if pd:
        pd = pd.replace(tzinfo = pytz.utc)
    return pd

def getScalar(doc_tfidf):
        total = 0
        for i in range(len(doc_tfidf)):
            total += doc_tfidf[i] * doc_tfidf[i]
        #for k in doc_tfidf:
        #    total += doc_tfidf[k] * doc_tfidf[k]
        return sqrt(total)

def calculateCosSimMod(vec1, vec2):
    cosSim = 0.0
    s = 0
    count = 0
    for k in vec1:
        if k in vec2:
            s += vec1[k] * vec2[k]
            count +=1
    if s>0:
        vec1S = getScalar(vec1.values())
        vec2S = getScalar(vec2.values())
        cosSim = float(s) / (vec1S * vec2S)
        cosSim = cosSim * count/len(vec2)  
    return cosSim


def calculateCosSim(vec1, vec2):
    cosSim = 0.0
    s = 0
    for k in vec1:
        if k in vec2:
            s += vec1[k] * vec2[k]
    if s>0:
        vec1S = getScalar(vec1.values())
        vec2S = getScalar(vec2.values())
        cosSim = float(s) / (vec1S * vec2S)  
    return cosSim

def getSorted(tupleList,fieldIndex, reverse=True):
    sorted_list = sorted(tupleList, key=itemgetter(fieldIndex), reverse=True)
    return sorted_list

def getTokens(texts):
    #global corpusTokens
    #global docsTokens
    stemmer = PorterStemmer()
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
   
    allTokens_2 = [t.lower() for t in allTokens if len(t)>2 and t.isalnum() and t not in stopwordsList]
    #allTokens_an = [t2 for t2 in allTokens_2 if t2.isalnum()]
    #allTokens_stw = [t3 for t3 in allTokens if t3 not in stopwordsList]
    #allTokens_stw = [t3 for t3 in allTokens_an if t3 not in stopwordsList]
    allTokens_stem = [stemmer.stem(word) for word in allTokens_2]#allTokens_stw]
    final = [t for t in allTokens_stem if t not in stopwordsList]
    return final

def getFreq(tokens):
    #toks = [t.lower() for t in tokens]
    fd = FreqDist(tokens)
    fdict = dict(fd.items())
    return fdict

def readFileLines(filename):
    f = open(filename,"r")
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    return lines
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True
def parseStrDate(dateString):
    try:
        dateTimeObj = parse(dateString)
        return dateTimeObj
    except:
        return None
def extractDateFromURL(url):

    #Regex by Newspaper3k  - https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
    m = re.search(r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if m:
        return parseStrDate(m.group(0))


    return  None
def getEntities(texts):
        
        if type(texts) != type([]):
            texts = [texts]   
        """
        Run the Stanford NER in server mode using the following command:
        java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.muc.7class.distsim.crf.ser.gz -port 8000 -outputFormat inlineXML
        """
        
        tagger = ner.SocketNER(host='localhost',port=8000)
        entities = []
        for t in texts:
            ents = tagger.get_entities(t)
            entities.append(ents)
        return entities

def getTxt(htmlPage):
    
    soup = BeautifulSoup(htmlPage)
    title = ""
    text = ""
    if soup.title:
        if soup.title.string:
            title = soup.title.string
    
    comments = soup.findAll(text=lambda text:isinstance(text,Comment))
    [comment.extract() for comment in comments]

    
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

def getSentences(textList =[]):
    #stopwordsList = stopwords.words('english')
    #stopwordsList.extend(["news","people","said"])
    if type(textList) != type([]):
        textList = [textList]
    sents = []
    for text in textList:
        sentences = sent_tokenize(text)
        newSents = []
        for s in sentences:
            if len(re.findall(r'.\..',s))>0:
                ns = re.sub(r'(.)\.(.)',r'\1. \2',s)
                newSents.extend(sent_tokenize(ns))
            else:
                newSents.append(s)

        
        newSents = [s for sent in newSents for s in sent.split("\n") if len(s) > 3]
        cleanSents = [sent.strip() for sent in newSents if len(sent.split()) > 3]
        sents.extend(cleanSents)
    return sents

def getWebpageText(URLs = []):
    webpagesText = []
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
                    print 'No Text to be extracted from: ', url
            else:
                text = {}
                print 'Content-Type is not text/html', ct," - ", url 
        else:
            print 'Could not downlaod:', url
            text = {}
#         except Exception as e:
#             raise e
#             print sys.exc_info()
            #text = ""
            #text = {}
        webpagesText.append(text)
    return webpagesText
