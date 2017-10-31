'''
Created on Feb 18, 2014

@author: mohamed
'''
#from eventUtils import getFreq
#from zss import simple_distance, Node
from _collections import defaultdict
import utils
#from nltk.stem.porter import PorterStemmer
import sys
class EventModel:
    
    def visible(self,element):
            if element.parent.name in ['style', 'script', '[document]', 'head']:
                return False
            return True
    
    def __init__(self,topK=3,th=5):
        self.entities = {}
        self.topK=topK
        self.intersectionTh=th
    
    def buildEventModel(self,seedURLs,eventType = 'Shooting',minTopicTermFreq=10,minLocTermFreq=10,minDateTermFreq=10):
        print 'Download Webpages'
        txtsCnts = utils.getWebpageText(seedURLs)
        txts = [t['text'] for t in txtsCnts if 'text' in t]
        docsHTML = [t['html'] for t in txtsCnts if 'html' in t]
        print len(txts)
        
        # find event Date
        pubDates = []
        for url,docHTML in zip(seedURLs,docsHTML):
            pubDate = utils.getPublishingDate(url,docHTML)
            pubDates.append(pubDate)
        pubDates = [pd for pd in pubDates if pd]
        pubDatesDic = utils.getFreq(pubDates)
        #pubDatesSrt = utils.getSorted(pubDatesDic.items(), 1,reverse=False)
        #evtDate = pubDatesSrt[0]
        #evtDate = evtDate[0]
        evtDate = min(pubDatesDic.keys())
        self.evtDate = evtDate
        print 'Event Date: ', self.evtDate
        
        # build location vector
        locsDist = []
        datesDist = []
        locFreqThresh = minLocTermFreq
        docsSents = utils.getSentences(txts)
        sentsEnts = utils.getEntities(docsSents)
        
        for sentEnt in sentsEnts:
            locsDist.extend(sentEnt.get('LOCATION',[]))
            datesDist.extend(sentEnt.get('DATE',[]))
        
        evtLocsDist = utils.getFreq(locsDist)
        print evtLocsDist
        evtDatesDist = utils.getFreq(datesDist)
        evtLocMaxVal = max(evtLocsDist.values())
        evtLocsDist = dict([(l,f*1.0/evtLocMaxVal) for l,f in evtLocsDist.items() if f>=locFreqThresh])
        evtLocsSrt = utils.getSorted(evtLocsDist.items(), 1)
        print 'Locs:',evtLocsSrt
        self.evtLocsVec = evtLocsDist
        
        self.evtLocsTks = defaultdict(int)
        for el in self.evtLocsVec:
            elTks = utils.getTokens(el)
            for elt in elTks:
                self.evtLocsTks[elt] += self.evtLocsVec[el]
        evtLocMaxVal = max(self.evtLocsTks.values())
        #self.evtLocsTks = dict([(l,f*1.0/evtLocMaxVal) for l,f in self.evtLocsTks.items() if f>=locFreqThresh])
        self.evtLocsTks = dict([(l,f) for l,f in self.evtLocsTks.items()])
        
        # build topic reference vector (centroid)
        vocabTksSrt,docsDics = utils.getVocabFromDocs(txts,2)
        #print "Before: ", vocabTksSrt
        
        #remove most freq location entity only
        #evtLocsDatesTks = utils.getTokens(' '.join([evtLocsSrt[0][0]] + evtDatesDist.keys()))
        #OR remove all locs entities
        #evtLocsDatesTks = utils.getTokens(' '.join(evtLocsDist.keys() + evtDatesDist.keys()))
        #vocabTksSrt = [v[0] for v in vocabTksSrt if v[0] not in evtLocsDatesTks]
        #print "After: ", vocabTksSrt
        
        print 'topK: ',self.topK
        vocab_keywords = vocabTksSrt[:self.topK]
        vocab_keywords = [v[0] for v in vocab_keywords]
        
        # convert docs to BOW using the vocab chosen in previous step
        print 'Convert Docs to BOW using Vocab: ', vocab_keywords
        docsVocab = []
        for doc in docsDics:
            #docVocab = {}
            #for t in doc:
            #    if t in vocab_keywords:
            #        docVocab[t] = doc[t]
            #maxVal = max(docVocab.values())
            maxVal = max(doc.values())
            docVocab = dict([(t,float(f)/maxVal) for t,f in doc.items() if t in vocab_keywords])
            docsVocab.append(docVocab)
        print 'Calc Centroid'
        targetRepr = 'centroid'
        refVect ={}#defaultdict(float)
        if targetRepr == 'centroid':
            for t in vocab_keywords:
                termVal = sum([doc[t] for doc in docsVocab if t in doc])/len(docsVocab)
                refVect[t] = termVal
        self.refVec = refVect
        print refVect
    
    def calculateCosSimAll(vec1):
    #vec1 should be url or webpage dic
        sc = getScalar(vec1.values())
        cosSim = 0.0
        s = 0
        for k in vec1:
            if k in self.refVec:
                s1 += vec1[k] * self.refVec[k]
            if k in self.evtLocsTks:
                s2 += vec1[k] * self.evtLocsTks[k]
        if s>0:
            vec1S = getScalar(vec1.values())
            vec2S = getScalar(vec2.values())
            cosSim = float(s) / (vec1S * vec2S)
        return cosSim


    
    def calculate_score(self, docPage, m='W'):
        res = 0
        topicWeight = 0.4
        locWeight = 0.2
        dateWeight = 0.4
        topicWeight_ = topicWeight / (topicWeight + locWeight)
        locWeight_ = locWeight / (topicWeight + locWeight)
        
        if m == 'W':
            docDate = utils.getPublishingDate(docPage.pageUrl[1], docPage.html)
            if docDate == None:
                docDateScore = 0
            else:
                docDateScore = utils.getDateScore(docDate, self.evtDate)
                if docDateScore == 0:
                    return [0,0]
            
            doc = docPage.text
            wpTks = utils.getTokens(doc)
            wpDic = utils.getFreq(wpTks)
            maxDocVal = 1
            wpTopicScore = utils.calculateCosSim(wpDic, self.refVec)
            #wpTopicScore = utils.calculateCosSimMod(wpDic, self.refVec)
            try:
                wpEnts = utils.getEntities(doc)[0]
            except Exception as e:
                print 'Get Entities exited with Exception: ', sys.exc_info()
                return [res, -1]
            wpLocsDist = wpEnts.get('LOCATION',[])
            wpLocsDist = utils.getFreq(wpLocsDist)
            
            wpLocScore = utils.calculateCosSim(self.evtLocsVec, wpLocsDist)
            
            if docDateScore == 0:
                #docScore = (wpTopicScore + wpLocScore)/2.0
                docScore = topicWeight_ * wpTopicScore + locWeight_ * wpLocScore
            else:
                #docScore = (wpTopicScore+docDateScore+wpLocScore)/3.0
                docScore = topicWeight * wpTopicScore + locWeight * wpLocScore + dateWeight * docDateScore
            #docScore = (wpTopicScore+docDateScore+wpLocScore)/3.0
            return [res,docScore]
        elif m =='U':
            docDate = utils.extractDateFromURL(docPage.address)
            if docDate == None:
                docDateScore = 0
            else:
                docDateScore = utils.getDateScore(docDate, self.evtDate)
                if docDateScore == 0:
                    return 0
            docPage.address = docPage.address.replace('_',' ')
            doc = docPage.getAllText()
            urlTks = utils.getTokens(doc)
            urlDic = utils.getFreq(urlTks)
            urlTopicScore = utils.calculateCosSim(urlDic, self.refVec)
            #urlTopicScore = utils.calculateCosSimMod(urlDic, self.refVec)
            urlLocScore = utils.calculateCosSim(self.evtLocsTks, urlDic)
            
            if docDateScore==0:
                urlScore = (urlTopicScore+urlLocScore)/2.0
                urlScore = topicWeight_ * urlTopicScore + locWeight_ * urlLocScore 
            else:
                #urlScore = (docDateScore + urlTopicScore + urlLocScore)/3.0
                urlScore = dateWeight * docDateScore + topicWeight * urlTopicScore + locWeight * urlLocScore
            #urlScore = (docDateScore + urlTopicScore + urlLocScore)/3.0
            return urlScore
            
    
