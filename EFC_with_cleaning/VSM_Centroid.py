'''
Created on May 12, 2016

@author: mmagdy
'''
from utils import *



class VSM_CentroidClassifier():
    
    def buildModel(self,posURLs,topK):
        print 'Downloading Pos URLs'    
        posDocs = getWebpageText(posURLs)
        #posDocs = getWebpageText_NoURLs(posURLs)
        posDocs = [d['text'] for d in posDocs if 'text' in d]
        #vocabTks = getTokens(posDocs)
        vocabTksSrt,docsDics = getVocabFromDocs (posDocs,2)
        print 'topK: ',topK
        vocab_keywords = vocabTksSrt[:topK]
        print vocab_keywords
        vocab_keywords = [v[0] for v in vocab_keywords]
        # convert docs to BOW using the vocab chosen in previous step
        print 'Convert Docs to BOW using Vocab: ', vocab_keywords
        docsVocab = []
        for doc in docsDics:
            #docVocab = {}
            #print doc
            #for t in doc:
            #    if t in vocab_keywords:
            #        docVocab[t] = doc[t]
            #normalize doc values with max value
            #print docVocab
            maxVal = max(doc.values())
            docVocab = dict([(t,float(f)/maxVal) for t,f in doc.items() if t in vocab_keywords])
            docsVocab.append(docVocab)
        
        #target repr
        print 'Calc Centroid'
        targetRepr = 'centroid'
        refVect ={}#defaultdict(float)
        if targetRepr == 'centroid':
            #using centroid as ref vec
            #refVect = dict([(t,float(v)/len(docsDics)) for t,f,v in vocabTks if t in vocab_keywords])
            
            for t in vocab_keywords:
                termVal = sum([doc[t] for doc in docsVocab if t in doc])/len(docsVocab)
                refVect[t] = termVal
        print refVect
        #posDocsVocab = getFreq(vocabTks)
        self.modelCentroid = refVect
        #self.modelCentroid = dict([(k,float(v)/len(posDocs)) for k,v in posDocsVocab.items()])
        self.modelCentroidScalar = getScalar(self.modelCentroid.values())
    
    def calculate_score(self,docPage,m='W'):
        res = 0
        if m== 'W':
            doc = docPage.text
            docTks = getTokens(doc)
            docDic = getFreq(docTks)
            '''
            #Transform doc to vocab
            nDocDic = {}
            for k in docDic:
                if k in self.modelCentroid:
                    nDocDic[k] = docDic[k]
            
            #calculate cos sim bet newDoc and model centroid
            score = 0
            for k in nDocDic:
                score += nDocDic[k] * self.modelCentroid[k]
            if score:
                score = score / (getScalar(nDocDic.values()) * self.modelCentroidScalar)
            '''
            maxDocVal = 1
            if docDic:
                maxDocVal = max(docDic.values())
            #wpDic = dict([(t,float(f)/maxDocVal) for t,f in docDic.items() if t in self.modelCentroid])
            wpDic =dict([(t,float(f)/maxDocVal) for t,f in docDic.items()])
            
            #compare wbVocab to refVect using cosSim
            wpScore = calculateCosSim(wpDic, self.modelCentroid)
            return [res,wpScore]
        elif m == 'U':
            docPage.address = docPage.address.replace('_',' ')
            d = docPage.getAllText()
            docTks = getTokens(d)
            docDic = getFreq(docTks)
            maxDocVal =1
            '''
            #Transform doc to vocab
            nDocDic = {}
            for k in docDic:
                if k in self.modelCentroid:
                    nDocDic[k] = docDic[k]
            
            #calculate cos sim bet newDoc and model centroid
            score = 0
            for k in nDocDic:
                score += nDocDic[k] * self.modelCentroid[k]
            if score:
                score = score / (getScalar(nDocDic.values()) * getScalar(self.modelCentroidScalar))
            '''
            if docDic:
                maxDocVal = max(docDic.values())
            #urlDic = dict([(t,f) for t,f in docDic.items() if t in self.modelCentroid])
            #urlVocab = dict([(t,float(f)/maxDocVal) for t,f in urlDic.items()])
            urlDic = dict([(t,float(f)/maxDocVal) for t,f in docDic.items()])
            #compare wbVocab to refVect using cosSim
            urlScore = calculateCosSim(urlDic, self.modelCentroid)
            return urlScore
