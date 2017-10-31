#!/usr/local/bin/python
import sys
import requests_cache
from crawler import Crawler
from priorityQueue import PriorityQueue
from eventModel import EventModel
from VSM_Centroid import VSM_CentroidClassifier
from utils import readFileLines
import os
import cPickle as pickle

def baseFC(crawlParams):
    seedURLs = crawlParams['seedURLs']
    t = [(-1,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    classifierFileName = crawlParams['classifierFileName']
    crawlParams["priorityQueue"]=priorityQueue
    try:
        classifierFile = open(classifierFileName,"rb")
        vsmClf = pickle.load(classifierFile)
        #self.classifier.error = 0.05
        #self.classifier.relevanceth = 0.75
        classifierFile.close()
    except:
        #vsmClf = VSMClassifier()
        vsmClf = VSM_CentroidClassifier()
        vsmClf.buildModel(crawlParams['model'], topK=10)
        #vsmClf.buildVSMClassifier(crawlParams['seedURLs'],classifierFileName,crawlParams['eventType'], crawlParams['minCollFreq'])
        print 'Saving model to file'
        classifierFile = open(classifierFileName,"wb")
        pickle.dump(vsmClf,classifierFile)
        classifierFile.close()
    crawlParams['scorer']=vsmClf
    #keywordModel = KeywordModel()
    #keywordModel.buildModel(crawlParams['model'])#,crawlParams['No_Keywords'])
    #crawlParams['scorer']=keywordModel
    
    #crawler = Crawler(priorityQueue,scorer,options)
    crawler = Crawler(crawlParams)
    qu = crawler.crawl()
    quS = '\n'.join([str(-1*s[0]) +"," +s[1] for s in qu])
    with open('queueBase.txt','w') as fw:
        fw.write(quS.encode('utf8'))
    return crawler.relevantPages
    #return crawler.relevantPages

def eventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-1,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    
    eventModel = EventModel(crawlParams['No_Keywords'])
    eventModel.buildEventModel(crawlParams['model'],crawlParams['eventType'],minTopicTermFreq=20,minLocTermFreq = crawlParams['minLocTermFreq'],minDateTermFreq=20)
    
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    
    #crawler.crawl()
    qu = crawler.crawl()
    quS = '\n'.join([str(-1*s[0]) +"," +s[1] for s in qu])
    with open('queueEvent.txt','w') as fw:
        fw.write(quS.encode('utf8'))
    return crawler.relevantPages



def writeEvaluation(res,filename):
    f = open(filename,"w")
    #for p,e in zip(relevantPages,res):
    rel = 0
    tot = 0
    for r in res:
        rel = rel + r
        tot = tot + 1 
        f.write(str(rel) + "," + str(tot) + "\n")
    f.close()

if __name__ == "__main__":
    
    seedsFiles=['niceAttack.txt','BrexitAllLongURLs-URLs-Unique-Filtered.txt','OrlandoLongURLs-URLs-Unique.txt','zikaLongURLs-only-Unique-Filtered.txt','allLongURLsEgyptAir-Only-Unique-Filtered.txt','brusselsAttack-Bombing-10-redundantSources.txt','Seeds-flintWaterCrisis.txt','allCaliforniaShootingLongURLs-Rel-Parsed.txt','Output-chapelhillshooting.txt','Output-germanwings_crash.txt',\
                'Output-Joaquin-2.txt','Output-tunisiaHotelAttack.txt','Output-nepalEarthquake-2.txt','Output-samesexmarriage.txt',\
                'Output-fifaArrests.txt','Output-boatCapsized.txt','Output-ParisAttacks.txt','Output-TSU-shooting.txt',\
                'Output-deltaStateUnivShooting.txt','Output-RussianPlaneCrash-2.txt','Output-oregonCommCollegeShooting.txt',\
                'Output-CharlestonShooting.txt','seeds-Sandra.txt','seeds_459.txt','seeds_474.txt','seedsURLs_z_534.txt',\
                'seedsURLs_z_501.txt','seedsURLs_z_540.txt']
    posFiles = ['brusselsAttack-Bombing.txt','Seeds-flintWaterCrisis.txt','Output-californiaShooting.txt','Output-chapelhillshooting.txt','Output-germanwings_crash.txt','Output-Joaquin.txt','Output-tunisiaHotelAttack.txt','Output-nepalEarthquake.txt','Output-samesexmarriage.txt','Output-fifaArrests.txt','Output-boatCapsized.txt','paris-Pos-URLs.txt','Output-TSU-shooting.txt','Output-deltaStateUnivShooting.txt','Output-RussianPlaneCrash.txt','oregon-Pos-URLs.txt','charleston-Pos-URLs.txt','evaluate-SandraBland.txt','pos-tunisiaHotelAttack.txt','pos-samesexmarriage.txt','Output-fifaArrests.txt','Output-boatCapsized.txt','Output-nepalEarthquake.txt','pos-FSU.txt','pos-Hagupit.txt','pos-AirAsia.txt','pos-sydneyseige.txt','pos-Charlie.txt']
    negFiles = ['california-Neg-URLs.txt','','','','','','','','','paris-Neg-URLs.txt','Output-TSU-shooting.txt','','','oregon-Neg-URLs.txt','charleston-Neg-URLs.txt','neg-FSU.txt','neg-Hagupit.txt','neg-AirAsia.txt','neg-sydneyseige.txt','neg-Charlie.txt']
    modelFiles = ['niceAttack.txt','output-brexit.txt','output-orlandoShooting.txt','Output-zikaVirus.txt','egyptAirPlaneCrash.txt','brusselsAttack-Bombing-23.txt','Seeds-flintWaterCrisis.txt','Output-californiaShooting.txt','Output-chapelhillshooting.txt','Output-germanwings_crash.txt','Output-Joaquin.txt','Output-tunisiaHotelAttack.txt','Output-nepalEarthquake.txt','Output-samesexmarriage.txt','Output-fifaArrests.txt','Output-boatCapsized.txt','Output-ParisExplosionShooting.txt','Output-TSU-shooting.txt','Output-deltaStateUnivShooting.txt','Output-RussianPlaneCrash.txt','Output-oregonCommCollegeShooting.txt','Output-CharlestonShooting.txt','model-SandraBland.txt','model-tunisiaHotelAttack.txt','model-samesexmarriage.txt','model-CharlestonShooting.txt']
    eventKeywords=['brussels attack bombing','flint water crisis','california shooting','chapel hill shooting','germanwings plane crash','hurricane joaquin','tunisia hotel attack',\
                   'nepal earthquake','same sex marriage','fifa arrest','boat capsized','paris terror attack',\
                   'tennesse state university shooting','delta state university shooting', 'russian plane crash',\
                   'oregon community college shooting','charleston shooting']
    #1 10 14 15
    #for i in range(3):
    i=0
    ct = sys.argv[1]#'b'
    if ct =='b':
        cacheT = '-base'
    else:
        cacheT = '-event'
    #reqCacheFileName = 'fc_cache'+cacheT+'-'+seedsFiles[i].split('.')[0]
    reqCacheFileName = 'fc_cache'+cacheT+'-'+sys.argv[2].split('/')[1].split('.')[0]
    requests_cache.install_cache(reqCacheFileName, backend='sqlite')
    eventType ='Attack'#'Disease_Outbreak'#'Plane_Crash'#'Shooting'#'Hurricane'# ###'Plane_Crash''Earthquake'
    vsmClassifierFileName = 'classifierVSM-Centroid-'+seedsFiles[i].split(".")[0]+".p"

    parameters = {}
    for line in open("config.txt", "r"):
        splitLine = line.rstrip('\n').split(" : ")
        parameters[splitLine[0]] = splitLine[1]

    allVocab = float(parameters["allVocab"])
    pagesLimit = float(parameters["pagesLimit"])
    combineScore = float(parameters["combineScore"])
    restrictedCrawl = float(parameters["restrictedCrawl"])
    noK = float(parameters["noK"])
    pageTh = float(parameters["pageTh"])
    urlsTh = float(parameters["urlsTh"])
    bufferLen = float(parameters["bufferLen"])
    minLocTermFreq = float(parameters["minLocTermFreq"])
    minNumDoc = float(parameters["minNumDoc"])
    minCollFreq = float(parameters["minCollFreq"])
    error = float(parameters["error"])
    roundPrec = float(parameters["roundPrec"])

    posFile = posFiles[i]
    #negFile = negFiles[i]
    #inputFile = 'input/'+seedsFiles[i]
    #modelFile = 'input/'+modelFiles[i]#'modelFile.txt'#inputFile
    inputFile = sys.argv[2]
    modelFile = sys.argv[3]
  
    #vsmClassifierFileName = 'classifierVSM-Centroid-'+inputFile.split(".")[0].split('-')[1]+".p"
    file = inputFile.split(".")[0].split("/")[1]
    vsmClassifierFileName = 'classifierVSM-Centroid-'+file+".p"
    
    
    #mode = 1 # URL scoring with no page scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageTh,"urlScoreThreshold":urlsTh }#,"mode":mode}
    crawlParams["bufferLen"]=bufferLen
    crawlParams['No_Keywords']=noK
    crawlParams['minCollFreq'] = minCollFreq
    crawlParams['minNumDoc'] = minNumDoc
    crawlParams['siScoreCombineMethod'] =1
    seedURLs = readFileLines(inputFile)
    crawlParams['seedURLs'] = seedURLs
    #negURLs = readFileLines(negFile)
    #crawlParams['negURLs'] = negURLs
    modelURLs = readFileLines(modelFile)
    crawlParams['model']=modelURLs #eventKeywords[i]
    crawlParams['restricted'] = restrictedCrawl
    crawlParams['combineScore'] = combineScore
    #crawlParams['classifierFileName'] =naiveBayesEventClfFileName#naiveBayesClfFileName#vsmClassifierFileName
    crawlParams['allVocab']=allVocab
    crawlParams['eventType']=eventType
    outputDir = 'output/'+inputFile.split(".")[0]
    #crawlParams['t'] = t
    if ct =='b':
        #baseRelevantPages =baseFC(crawlParams)
        pagesDir=outputDir+"/base-webpages/"
        logDataFilename=pagesDir+"base-logData.txt"
        outputURLsFilename=pagesDir+"base-Output-URLs.txt"
        evalFilename=pagesDir+"base-evaluateData.txt"
        crawlParams['classifierFileName'] =vsmClassifierFileName
        crawlParams['pagesDir'] = pagesDir
        if not os.path.exists(pagesDir):
            os.makedirs(pagesDir)
        rp = baseFC(crawlParams)
        #rp = baseFC_OneTargetVector(crawlParams)
        
    elif ct =='e': 
        #eventRelevantPages = eventFC(crawlParams)
        pagesDir=outputDir+"/event-webpages/"
        logDataFilename=pagesDir+"event-logData.txt"
        outputURLsFilename=pagesDir+"event-Output-URLs.txt"
        evalFilename=pagesDir+"event-evaluateData.txt"
        crawlParams['pagesDir'] = pagesDir
        crawlParams['minLocTermFreq'] = minLocTermFreq
        if not os.path.exists(pagesDir):
            os.makedirs(pagesDir)
        rp = eventFC(crawlParams)
    
    f = open(logDataFilename,"w")
    furl = open(outputURLsFilename,"w")
    evalRes = []
    for p in rp:
        #f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        #furl.write(p.pageUrl[1].encode("utf-8")+"\n")
        pageID = p[0]
        pageURL = p[1]
        f.write(str(pageID) + "," + str(pageURL[1]) + "\n")
        furl.write(pageURL[0].encode("utf-8")+"\n")
        evalRes.append(p[2])
        #ftext = open(pagesDir+str(p.pageId) + ".txt", "w")
        #textNoNewLine=''
        #ps = p.text.split('\n')
        #psNotEmpty = [l for l in ps if l]
        #textNoNewLine = '\n'.join(psNotEmpty)
        ##ftext.write(p.text.encode("utf-8"))
        #ftext.write(textNoNewLine.encode("utf-8"))
        #ftext.close()
    f.close()
    furl.close()
    res = []
    for er in evalRes:
        if er >= pageTh:
            res.append(1)
        else:
            res.append(0)
    
    print evalRes
    print res
    print sum(res)
    print len(res)
    writeEvaluation(res,evalFilename)
    with open('output/consoleOut.txt','w') as fw:
        #strTow = [str(er) for er in evalRes]
        #fw.write(','.join(strTow))
        fw.write(str(evalRes))
        fw.write('\n--\n')
        fw.write(str(res))
        fw.write(str(sum(res)))
        fw.write(str(len(res)))
