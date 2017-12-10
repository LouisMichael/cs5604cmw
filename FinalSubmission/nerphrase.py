"""
Input: 
Output: list of NERs
"""
def getNERs(allTokens, pltfrm = "linux"):
    nerDict = {
    "person":"",
    "org":"",
    "location":""
    }
    st = StanfordNERTagger("/home/cs5604f17_cmw/testCMW/stanfordner/classifiers/english.all.3class.distsim.crf.ser.gz", "/home/cs5604f17_cmw/testCMW/stanfordner/stanford-ner.jar")
    tags = st.tag(allTokens)
    #tags_ners = [i for i,j in tags if j != 'O']
    #nerDict['person'] = [i for i,j in tags if j == 'PERSON']
    #nerDict['org'] = [i for i,j in tags if j == 'ORGANIZATION']
    #nerDict['location'] = [i for i,j in tags if j == 'LOCATION']
    
    nerDict['person'] = []
    nerDict['org'] = []
    nerDict['location'] = []
    last_tag = "O"
    for i,j in tags:
        cur_tag = j
        if (cur_tag == last_tag):
            if cur_tag == 'PERSON':
                nerDict['person'][-1] += " "+i
            if cur_tag == 'ORGANIZATION':
                nerDict['org'][-1] += " "+i   
            if cur_tag == 'LOCATION':
                nerDict['location'][-1] += " "+i                
        else:
            if cur_tag == 'PERSON':
                nerDict['person'].append(i)
            if cur_tag == 'ORGANIZATION':
                nerDict['org'].append(i) 
            if cur_tag == 'LOCATION':
                nerDict['location'].append(i)             
        last_tag = cur_tag
    return nerDict
