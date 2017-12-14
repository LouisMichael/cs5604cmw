COL_ID = {
"VegasShooting":"1025",
"Hurricane Irma":"1008",
"Hurricane Harvey":"1000",
"Eclipse2017":"994",
"NIU shooting": "1036",
"Dunbar High School shooting": "1035",
"University Alabama shooting" : "1043",
"Sparks Middle School shooting" : "1040",
"Worthing High School shooting" : "1039",
"Townville School shooting" : "1042",
"Virginia Tech shooting" : "1038",
"Umpqua College shooting" : "1041",
"Connecticut shooting" : "41",
"oregon school shooting" : "502"
}

COL_EVENT = "Umpqua College shooting"

OUTPATH = "output/"

OUTFN = "cmwf17UmpquaCollegeShooting.tsv"

WARC_FILE = "Umpqua.warc.gz"

FROM_WARC = 1

## This is more like a manual. Not really used in our code. 
REF_CODE = {
"1000":"Content-Type is not text/html",
"2000":"No text data",
"2001":"Unknown reason (URL content successfully fetched)",
}

#JAVA_HOME = 'C:\Program Files\Java\jre1.8.0_144\\bin\java.exe'
#CLASS_PATH = 'C:\Users\eagan\Desktop\Cluster Files\shooting-warc-files\stanford-ner-2017-06-09\stanford-ner.jar'
