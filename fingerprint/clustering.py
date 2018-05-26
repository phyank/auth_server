from time import sleep

from fingerprint.common import *

def get_similarity(rid,account):
    sleep(1)
    return 0.5

def get_fingerprint(rid,aritcle_content):
    sleep(2)
    return rid,[0,0,0,0,0,0,0,0,0,0]

def get_recommend(rid):
    sleep(0.5)
    return [{'imgurl':TEST_IMG,'accountname':'no','title':'no title','url':'/','ifcopy':True}]