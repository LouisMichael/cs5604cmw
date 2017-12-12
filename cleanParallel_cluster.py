#!/usr/bin/python
# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue, Pipe
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup, Comment
import codecs
import clean_text_config as config
import re
import platform
import os
import sys
import time
import zlib
import bz2
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.regexp import WordPunctTokenizer
from nltk import FreqDist, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger

## for timestamp

import time

## for language list

from langdetect import detect_langs
import warnings

warnings.filterwarnings('ignore')
#os.environ['JAVAHOME'] = config.JAVA_HOME
#os.environ['CLASSPATH'] = config.CLASS_PATH

## extract domain name

if sys.version_info[0] == 3:

    # # for python3, use:

    from urllib.parse import urlparse
else:

    # # for python2, use:

    from urlparse import urlparse

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'ignore')


def platformDetector():
    if platform.win32_ver()[0]:
        return 'windows'
    elif platform.mac_ver()[0]:
        return 'macintosh'
    else:

    # elif "ANDROID_PRIVATE" in os.environ:
    #    return "android"
    # missing: os.condition

        return 'linux'


def statusCodeWriter(st_code, url, ct=''):
    ts = str(time.time())
    theKey = url + '-' + ts
    print ('Could not download:', url, ' status code: ', st_code)
    newline_list = [theKey] + [''] * len(metadata_c) + [''] \
        * (len(webpage_c) - 2) + [ct] + [st_code] + [''] \
        * len(cleanwebpage_c)
    newline = '\t'.join(newline_list) + '\n'
    sumf.write(newline.encode('utf8'))
    print '-----------'


def getWebpageTextWARC(record):
    text = {
        'html': '',
        'text': '',
        'title': '',
        'type': '',
        }

    ct = record.rec_headers.get_header('Content-Type')
    page = record.content_stream().read()
    text = extractTextFromHTML(page)
    text['type'] = ct
    if text:
        text['html'] = page
    else:
        print ('No Text to be extracted from: ', url)
        text['text'] = '2000'

    return text


def getWebpageText(url, r=''):

    # webpagesText = []

    text = {
        'html': '',
        'text': '',
        'title': '',
        'type': '',
        }
    ct = r.headers.get('Content-Type', '')
    if ct.find('text/html') != -1:
        page = r.content
        text = extractTextFromHTML(page)
        text['type'] = ct
        if text:
            text['html'] = page
        else:
            print ('No Text to be extracted from: ', url)
            text['text'] = '2000'
    else:

        # text = {}

        print ('Content-Type is not text/html', ct, ' - ', url)
        text['type'] = ct
        text['text'] = '1001'

    return text


def extractTextFromHTML(page):
    text = ''
    title = ''
    if page:
        (text, title) = getTxt(page)
    if text.strip():
        wtext = {'text': title + u' ' + text, 'title': title}
    else:
        wtext = {}
    return wtext


def getTxt(htmlPage):
    soup = BeautifulSoup(htmlPage, 'lxml')

    title = ''
    text = ''
    if soup.title:
        if soup.title.string:
            title = soup.title.string

    text_nodes = soup.findAll(text=lambda text: not isinstance(text,
                              Comment))
    visible_text = filter(visible, text_nodes)

    text = '\n'.join(visible_text)
    text = title + '\n' + text

    return (text, title)


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head',
                               'iframe']:
        return False
    return True


def cleanTextProfanity(pipe):

    with open('profanity_en.txt') as f:
        __profanity_words__ = f.read()[:-1].split('\n')

    ProfanityRegexp = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))('
                                 + '|'.join(__profanity_words__)
                                 + r')(?=$|\W)', re.IGNORECASE)  # Non word character starting
                                                                 # Profanity word list
                                                                 # End with string end or non word character

    content = pipe.recv()
    while content != -1:
        pipe.send(re.sub(ProfanityRegexp, '{"profanity"}', content))
        content = pipe.recv()


def getTokens(pipe):

    # global corpusTokens
    # global docsTokens

    tokenizer = WordPunctTokenizer()
    stopwordsList = stopwords.words('english') + ['profanity']

    texts = pipe.recv()
    while texts != -1:
        allTokens = []

        if type(texts) != type([]):
            texts = [texts]
        for s in texts:
            toks = tokenizer.tokenize(s)
            allTokens.extend(toks)

        allTokens = [t.lower() for t in allTokens if t.isalnum() and t
                     not in stopwordsList]
        final = [t for t in allTokens if t not in stopwordsList]

        pipe.send(final)
        texts = pipe.recv()


def getPOS(pipe):
    allTokens = pipe.recv()
    while allTokens != -1:
        POS = nltk.pos_tag(allTokens)
        try:
            parts = ['{}:{}'.format(i, j) for (i, j) in POS]
        except:
            parts = ['']
        pipe.send(parts)
        allTokens = pipe.recv()


def getStemmed(pipe):
    stemmer = PorterStemmer()

    allTokens = pipe.recv()
    while allTokens != -1:
        allTokens_stem = [stemmer.stem(word) for word in allTokens]
        pipe.send(allTokens_stem)
        allTokens = pipe.recv()


def getLemmatized(pipe):
    wordnet_lemmatizer = WordNetLemmatizer()

    allTokens = pipe.recv()
    while allTokens != -1:
        allTokens_lemmatize = [wordnet_lemmatizer.lemmatize(word)
                               for word in allTokens]
        pipe.send(allTokens_lemmatize)
        allTokens = pipe.recv()


def getNERs(pipe):
    info = pipe.recv()
    while info != -1:

        nerDict = {'person': '', 'org': '', 'location': ''}

        # altered by Mackenzie

        #nerpath = 'nerClassifier/'
        #if info[1] == 'windows':
        #    st = \
        #        StanfordNERTagger('stanford-ner-2017-06-09//classifiers//english.all.3class.distsim.crf.ser.gz'
        #                          ,
        #                          'stanford-ner-2017-06-09//stanford-ner.jar'
        #                          )
        #else:
        #    st = StanfordNERTagger(nerpath
        #                           + 'english.all.3class.distsim.crf.ser.gz'
        #                           ,
        #                           'stanford-ner-2017-06-09/stanford-ner.jar'
        #                           )
        st = StanfordNERTagger("/home/cs5604f17_cmw/testCMW/stanfordner/classifiers/english.all.3class.distsim.crf.ser.gz", "/home/cs5604f17_cmw/testCMW/stanfordner/stanford-ner.jar")
        tags = st.tag(info[0])
        tags_ners = [i for i,j in tags if j != 'O']
        nerDict['person'] = [i for (i, j) in tags if j == 'PERSON']
        nerDict['org'] = [i for (i, j) in tags if j == 'ORGANIZATION']
        nerDict['location'] = [i for (i, j) in tags if j == 'LOCATION']
        pipe.send(nerDict)
        info = pipe.recv()


def extractMetaName(pipe):

    info = pipe.recv()
    while info != -1:
        metas = {
            'author': '',
            'copyright': '',
            'publishDate': '',
            'keywords': '',
            'url': info[1],
            }
        webhtml_parsed = BeautifulSoup(info[0], 'lxml')
        for meta in webhtml_parsed.find_all('meta'):
            metaName = meta.get('name', '').lower()

            # # author

            if 'author' == metaName and 'content' in meta:
                metas['author'] = meta['content'].strip()

            # # copyright

            if 'copyright' == metaName and 'content' in meta:
                metas['copyright'] = meta['content'].strip()

            if 'keywords' == metaName and 'content' in meta:
                metas['keywords'] = meta['content'].strip()

            if 'og:url' == metaName and 'content' in meta:
                metas['url'] = meta['content'].strip()

            # # Various ways to extract publish date

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

            # <meta name="pubdate" content="2015-11-26T07:11:02Z" >
            # <meta name='publishdate' content='201511261006'/>
            # <meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
            # <meta name="DC.date.issued" content="2015-11-26">
            # <meta property="article:published_time"  content="2015-11-25" />
            # <meta name="Date" content="2015-11-26" />
            # <meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
            # <meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
            # <meta name="article.published" content="2015-11-26T11:53:00.000Z" />
            # <meta name="published-date" content="2015-11-26T11:53:00.000Z" />
            # <meta name="article.created" content="2015-11-26T11:53:00.000Z" />
            # <meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
            # <meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
            # <meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
            # <meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
            # <meta itemprop="datecreated" content="2015-11-26T11:53:00.000Z" />
            # <meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">

            if any(conditions) and 'content' in meta:
                metas['publishDate'] = meta['content'].strip()

        pipe.send(metas)
        info = pipe.recv()


def getSubURL(pipe):
    URL_regexp = re.compile(r'https?://[a-zA-Z0-9\./-]+')

    html = pipe.recv()
    while html != -1:
        parsedHTML = BeautifulSoup(html, 'lxml')

        links = parsedHTML.find_all('a')
        urls = []
        for link in links:
            if link.get('href'):
                urls += re.findall(URL_regexp, link.get('href'))

        pipe.send(urls)
        html = pipe.recv()


if __name__ == '__main__':
    start = time.time()  # for monitoring process speed

    # region Pipes and Processes

    (profanity_pipe, child_profanity) = Pipe()
    profanity_process = Process(target=cleanTextProfanity,
                                args=(child_profanity, ))
    profanity_process.start()

    (token_pipe, child_token) = Pipe()
    token_process = Process(target=getTokens, args=(child_token, ))
    token_process.start()

    (pos_pipe, child_pos) = Pipe()
    pos_process = Process(target=getPOS, args=(child_pos, ))
    pos_process.start()

    (stem_pipe, child_stem) = Pipe()
    stem_process = Process(target=getStemmed, args=(child_stem, ))
    stem_process.start()

    (lem_pipe, child_lem) = Pipe()
    lem_process = Process(target=getLemmatized, args=(child_lem, ))
    lem_process.start()

    (ner_pipe, child_ner) = Pipe()
    ner_process = Process(target=getNERs, args=(child_ner, ))
    ner_process.start()

    (meta_pipe, child_meta) = Pipe()
    meta_process = Process(target=extractMetaName, args=(child_meta, ))
    meta_process.start()

    (sub_url_pipe, child_sub_url) = Pipe()
    sub_url_process = Process(target=getSubURL, args=(child_sub_url, ))
    sub_url_process.start()

    # endregion

    outpath = config.OUTPATH
    outfn = config.OUTFN

    col_event = config.COL_EVENT
    col_id = config.COL_ID[col_event]

    headers = \
        {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

    stopwordsList = stopwords.words('english') + ['profanity']

    pltfrm = platformDetector()

    output_f = outpath + outfn

    metadata_c = ['doc-type', 'collectoion-id', 'collection-name']
    webpage_c = [
        'url',
        'html',
        'language',
        'title',
        'author/publisher',
        'organization-name',
        'create-time',
        'domain-name',
        'domain-location',
        'sub-urls',
        'fetch-time',
        'mime-type',
        'status-code',
        ]
    cleanwebpage_c = [
        'clean-text',
        'clean-text-profanity',
        'keywords',
        'tokens',
        'stemmed',
        'lemmatized',
        'POS',
        'sner-people',
        'sner-organization',
        'sner-location',
        'real-world-events',
        ]

    output_c = ['url-timestamp'] + metadata_c + webpage_c + cleanwebpage_c

    if not os.path.isfile(output_f):
        with open(output_f, 'w') as sumf:
            sumf.write('\t'.join(output_c) + '\n')

            # print("New tsv file! ")

    sumf = open(output_f, 'ab')
	
    #start_index = sys.argv[1]
    #end_index = sys.argv[2]
    #print start_index
    #print end_index

    #counter = 0
    if config.FROM_WARC == 1:
        with open(config.WARC_FILE, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
					
					url = record.rec_headers.get_header('WARC-Target-URI').replace('\n', '')
					if url.endswith('.jpg'):
						st_code = '1001'
						ct = 'image/jpg'
						statusCodeWriter(st_code, url, ct)
						continue
					
					ts = str(record.rec_headers.get_header('WARC-Date'))
					
					# status codes for WARC files - 3XXX
					
					st_code = '3200'
					
					webdict = getWebpageTextWARC(record)
					webtype = webdict['type']
					webhtml = webdict['html']
					webtext = webdict['text']
					webtitle = webdict['title']
					
					# webhtml_parsed = BeautifulSoup(webhtml, 'lxml'); too big to send in pipe
					
					print 'Title: ' + webtitle
					
					# region Send Profanity, meta, sub_url, tokens
					
					profanity_pipe.send(webtext)
					
					meta_pipe.send([webhtml, url])
					sub_url_pipe.send(webhtml)
					
					webtext_profanity = profanity_pipe.recv()
					token_pipe.send(webtext_profanity)
					
					webtokens = token_pipe.recv()
					
					# endregion
					
					# region Processes - require Tokens
					
					pos_pipe.send(webtokens)
					stem_pipe.send(webtokens)
					lem_pipe.send(webtokens)
					ner_pipe.send([webtokens, pltfrm])
					
					# endregion
					
					# # Extract domain_name and domain_location
					# # We might need some mapping to get valid domain location
					
					parsed_uri = urlparse(url)
					domain_name = \
						'{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
					domain_location = (domain_name.split('.')[-1])[:-1]
					invalid_domains = ['com', 'net', 'edu', 'org']
					if domain_location in invalid_domains:
						domain_location = ''
					
					try:
						lan = [str(i).split(":")[0] for i in detect_langs(webtext)]
					except:
						lan = ['']
					lan = ','.join(lan)
					
					# region Receive info
					
					webPOS = pos_pipe.recv()
					webstem = stem_pipe.recv()
					weblemma = lem_pipe.recv()
					nerDict = ner_pipe.recv()
					metadict = meta_pipe.recv()
					sub_urls = sub_url_pipe.recv()
					
					# endregion
					
					url = metadict['url']
					webAuthor = metadict['author']
					webOrganization = metadict['copyright']
					webCreatedate = metadict['publishDate']
					webKeywords = metadict['keywords']
					
					nerPerson = ';'.join(nerDict['person'])
					nerOrg = ';'.join(nerDict['org'])
					nerLocation = ';'.join(nerDict['location'])
					
					webtokens = ','.join(webtokens)
					webstem = ','.join(webstem)
					weblemma = ','.join(weblemma)
					webPOS = ','.join(webPOS)
					
					sub_urls = ';'.join(sub_urls)
					
					# region Cleaning
					
					webtext = webtext.replace('\n', '.')
					webtext = webtext.replace('\r', '.')
					webtext = webtext.replace('\t', '.')
					
					webtext_profanity = webtext_profanity.replace('\n',
							'.')
					webtext_profanity = webtext_profanity.replace('\r',
							'.')
					webtext_profanity = webtext_profanity.replace('\t',
							'.')
					
					try:
						webhtml = webhtml.decode('utf-8')
					except:
						webhtml = webhtml.decode('utf-8',
								errors='ignore')
					
					webhtml = webhtml.replace('\n', '.')
					webhtml = webhtml.replace('\r', '.')
					webhtml = webhtml.replace('\t', '.')
					
					url = url.replace('\n', '')
					url = url.replace('\r', '')
					url = url.replace('\t', '')
					
					webtitle = webtitle.replace('\n', '.')
					webtitle = webtitle.replace('\r', '.')
					webtitle = webtitle.replace('\t', '.')
					
					# endregion
					
					# region Write to TSV
					# # Our key: URL+timestamp
					
					theKey = url + '-' + ts
					
					# write to tsv
					
					newline_list = [theKey]
					
					newline_m = ['webpage', col_id, col_event]
					newline_w = [
						url,
						webhtml,
						lan,
						webtitle,
						webAuthor,
						webOrganization,
						webCreatedate,
						domain_name,
						domain_location,
						sub_urls,
						ts,
						webtype,
						st_code,
						]
					newline_c = [
						webtext,
						webtext_profanity,
						webKeywords,
						webtokens,
						webstem,
						weblemma,
						webPOS,
						nerPerson,
						nerOrg,
						nerLocation,
						col_event,
						]
					
					# newline_c = [webtext, webtext_profanity]
					
					newline_list += newline_m + newline_w + newline_c
					
					newline = '\t'.join(newline_list) + '\n'
					sumf.write(newline.encode('utf8'))
					
					# endregion
					
					print '-----------'
    

    # region Send Kill Signal, Close Pipes, and Join Processes

    profanity_pipe.send(-1)
    profanity_process.join()
    profanity_pipe.close()

    token_pipe.send(-1)
    token_process.join()
    token_pipe.close()

    pos_pipe.send(-1)
    pos_process.join()
    pos_pipe.close()

    stem_pipe.send(-1)
    stem_process.join()
    stem_pipe.close()

    lem_pipe.send(-1)
    lem_process.join()
    lem_pipe.close()

    ner_pipe.send(-1)
    ner_process.join()
    ner_pipe.close()

    meta_pipe.send(-1)
    meta_process.join()
    meta_pipe.close()

    sub_url_pipe.send(-1)
    sub_url_process.join()
    sub_url_pipe.close()

    # endregion

    end = time.time()
    print end - start

			
