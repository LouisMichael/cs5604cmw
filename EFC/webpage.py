
import utils
from url import Url
from bs4 import BeautifulSoup

class Webpage:
    '''
    def __init__(self):
        self.pageUrl = ""
        self.html = ""
        self.title = ""
        self.text = ""
        self.outgoingUrls=[]
    '''
    def getUrls(self):
        if self.html:
            wpsoup =  BeautifulSoup(self.html) 
            links = wpsoup.find_all('a')
            for link in links:
                anchor =""
                if link.string:
                    anchor = link.string
                elif link.text:
                    anchor = link.text
                else:
                    anchor = ""
                u = Url(anchor,link.get('href'),"")
                self.outgoingUrls.append(u)
    
    def __init__(self,url,pageId):
        self.pageUrl = url
        self.pageId = pageId
        self.text = ""
        self.title = "" 
        self.outgoingUrls=[]
        #self.soup = None
        res = utils.getWebpageText(url[1])[0]
        
        if res and 'text' in res:
            self.text = res['text']
            self.title = res['title']
            #self.soup = BeautifulSoup(res['html'])
            self.html = res['html']