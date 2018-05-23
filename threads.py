#{'learn':name,'check':id,'diff':-1,'s1':-1,'s2':-1,'report':'wrong learing set!','error':False}

import threading

from Auth.pyltp_cut import *
#from Auth.parse_and_cut import *
from Auth.dict_standard import *

ARTICLE_REPORT=2

class CalcThread(threading.Thread):
    def __init__(self,inqueue,db,db_mutex):
        threading.Thread.__init__(self)
        self.inqueue=inqueue
        self.db=db
        self.db_mutex=db_mutex

    def run(self):
        while True:
            request=self.inqueue.get()
            id,name,article=request
            url,title,content=article['url'],article['title'],article['content']
            wordlist=get_real_words(content).split()
            try:
                report=cmp_article(id,name,title,url,wordlist)
            except WrongLearingSetError:
                report={'learn':name,'check':id,'diff':-1,'s1':-1,'s2':-1,
                        'report':'wrong learing set!','error':True}

            with self.db_mutex:
                self.db.put_result(id,name,title,url,report)