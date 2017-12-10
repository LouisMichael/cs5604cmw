import re


class Url:
    def __init__(self,anchor_text,url_address,context=""):
        self.anchor = anchor_text
        self.address = url_address
        self.context = context

    def getAllText(self):
        parts = [s for s in re.findall(r'\w+',self.address) if s]
        parts = [s for s in parts if s not in ['https','http','www','com','htm','html','asp','jsp','aspx','php','org','net','pl','cgi']]
        '''
        rem = ['https','http','www','com','htm','html','asp','jsp','aspx','php','org','net','pl','cgi']
        addr = self.address
        for r in rem:
            addr = addr.replace(r,' ')
        return addr + "," + self.anchor
        '''
        return "%s %s %s" % (self.anchor.strip(),' '.join(parts),self.context)
