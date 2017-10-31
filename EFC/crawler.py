
from webpage import Webpage
import sys,codecs
from _collections import defaultdict
from utils import getDomain

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'ignore')

class Crawler:
    #def __init__(self,priorityQueue,scorer,options):
    def __init__(self,crawlParams):
        #self.visited = []
        self.visited = {}
        self.pagesCount = 0
        self.priorityQueue = crawlParams['priorityQueue']
        self.scorer = crawlParams['scorer']
        self.pageScoreThreshold = crawlParams['pageScoreThreshold']
        self.urlScoreThreshold = crawlParams['urlScoreThreshold']
        self.pagesLimit = crawlParams['num_pages']
        #self.mode = crawlParams['mode']
        self.restricted = crawlParams['restricted']
        self.combineScore = crawlParams['combineScore']
        self.pagesDir = crawlParams['pagesDir']
        #self.hosts_RelNonRelLists={}
        self.bufferLen = crawlParams['bufferLen']
        self.sourcesImp = defaultdict(lambda : [1.,1.])#list contains number of relevant at index 0 and number of non-relevant at index 1
        self.siScoreCombineMethod = crawlParams['siScoreCombineMethod']
        self.topicWeight = 0.6
        self.siWeight = 0.4
    
    #def saveWebpage(self,pageTxt):
    #    return
    
    def crawl(self):
        self.harvestRatioData = []
        self.relevantPages = []
        webpages = []
        count = 0
        ftext = open(self.pagesDir+"webpagesTxt.txt", "w")
        webpageLabel = 0 # 0 for Non-relevant and 1 for Relevant
        while self.pagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
        
            work_url = self.priorityQueue.pop()
            url = work_url[1]
            #if self.exists(url,1):
            #    continue
            if url in self.visited:
                continue
            #self.visited.append(url)#work_url[1])
            self.visited[url] = 1
            page = Webpage(work_url,self.pagesCount)
            if page.text =='' :
                continue
            
            page.estimatedScore=0
            if self.combineScore:
                page_score = 0
                if len(page.text) > 0:
                    #page_score = self.scorer.calculate_score(page.text,'W')[1]
                    page_score = self.scorer.calculate_score(page,'W')[1]
                    if page_score == -1:
                        continue
                else:
                    print 'page text is empty'
                    continue
                
                page.estimatedScore = page_score
                
                if self.restricted:
                    if page_score < self.pageScoreThreshold:
                        #self.pagesCount += 1
                        continue
                
                pageDom = getDomain(url)
                if page_score >= self.pageScoreThreshold:
                    self.sourcesImp[pageDom][0]+=1
                    webpageLabel = 1
                else:
                    self.sourcesImp[pageDom][1]+=1
                    #self.sourcesImp[pageDom][0] = self.sourcesImp[pageDom][1]
                    webpageLabel = 0
            if self.combineScore:
                print page.pageId,": ",str(page_score),",", -1 * work_url[0],",", work_url[1]#,",", work_url[3]
            else:
                print -1 * work_url[0],",",work_url[1]#,",", work_url[3]
            self.pagesCount += 1
            #self.relevantPages.append((page.pageId,page.pageUrl,page.estimatedScore))
            self.relevantPages.append((page.pageId,(page.pageUrl[1],page.pageUrl[2]),page.estimatedScore))

            wbsStr = page.text.replace('\n', '. ').replace('\t', ' ')
            
            webpages.append(wbsStr)
            count += 1
            #save webpage's text to disk instead of adding to list
            # this will lead to change in evaluation
            if count % self.bufferLen == 0:
                strToWrite = '\n'.join(webpages).encode("utf-8")
                ftext.write(strToWrite)
                webpages = []
            #ftext = open(self.pagesDir+str(page.pageId) + ".txt", "w")
            #ftext.write(page.text.encode("utf-8"))
            #ftext.close()
            #-------

            if page_score < 0.1:
                continue
            page.getUrls()
            
            for link in page.outgoingUrls:
                url = link.address
                
                #if url != None and url != '':
                if url:
                    url = url.strip()
                    if url.find('report-a-typo') != -1:
                        continue
                    if url.find('m.tempo.co/') != -1:
                        continue
                    if url.find('?')!= -1:                            
                        furl = url.split('?')[1]
                        if furl.startswith('id=')==False or furl.startswith('v=')==False or furl.startswith('tid=')==False:
                            url = url.split('?')[0]
                    if url.find('#') != -1:
                        url = url.split('#')[0]
                    
                    if url.endswith('/'):
                        url = url[:-1]
                    #if url.endswith(("comment","comment/","feed","comments","feed/","comments/",".rss","video","video/","link","gif","jpeg","mp4","wav","jpg","mp3","png","share.php","sharer.php","login.php","print","print/","button/","share","email","submit","post",".pdf") ):
                    if url.endswith(("comment","feed","comments",".rss","video","link","gif","jpeg","mp4","wav","jpg","mp3","png","share.php","sharer.php","login.php","print","button","share","email","submit","post",".pdf") ):    
                        continue
                    
                    #if not self.exists(url,1):
                    if url in self.visited:
                        continue
                    #tot_score = 0.0
                    if url.startswith('http'): #and not self.exists(url,2):
                        linkText = link.getAllText()                            
                        #if self.mode == 1:
                        #url_score = self.scorer.calculate_score(linkText,'U')
                        url_score = self.scorer.calculate_score(link,'U')
                        tot_score = url_score
                        if self.combineScore:
                            #tot_score= 0.4 *page_score + 0.6 *url_score
                            
                            tot_score= page_score *url_score
                        if tot_score < self.urlScoreThreshold:
                                continue
                        urlDom = getDomain(url)
                        
                        si_score = self.sourcesImp[urlDom][0]/self.sourcesImp[urlDom][1]
                        if self.siScoreCombineMethod == 1:
                            if webpageLabel:
                                tot_score = tot_score * si_score
                        elif self.siScoreCombineMethod == 2:
                            tot_score = self.topicWeight * tot_score + self.siWeight * si_score
                        #tot_score = tot_score * si_score 
                        #else:
                        #    tot_score = url_score
                        #if tot_score >= self.urlScoreThreshold:
                        #print tot_score, '-', url, linkText
                        if self.restricted:
                            if tot_score < self.urlScoreThreshold:
                                continue
                        if tot_score >= self.urlScoreThreshold :
                            self.priorityQueue.push(((-1 * tot_score),url,page.pageId))#,linkText))
                        #else:
                        #    self.priorityQueue.push(((-1 * page_score),url,page.pageId,link.getAllText()))
            #else:
            #    self.pages.append((page,0))
                                    
        print self.priorityQueue.isempty()

        if webpages:
            strToWrite = '\n'.join(webpages).encode("utf-8")
            ftext.write(strToWrite)
        ftext.close()

        return self.priorityQueue.queue
        #print '\n'.join([str(-1*s[0]) +"," +s[1] for s in self.priorityQueue.queue])
                
    def exists(self,url,s):
        #if s == 1:
        #    urlList = [v for p,v,k,l in self.visited]
        #elif s == 2:
        #    urlList = [v for p,v,k,l in self.priorityQueue.queue]
        return url in self.visited#urlList
