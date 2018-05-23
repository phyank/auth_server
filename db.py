from collections import deque

ID=0
LEARN_NAME=1
TITLE=2
URL=3
ARTICLE_REPORT=4

class Database:
    def __init__(self,max_record_number):
        self.db={}
        self.get=deque()
        self.max=max_record_number

    def put_result(self,id,name,title,url,report):
        self.try_to_clean_db()
        self.db[id]=(id,name,title,url,report)

    def get_result(self,id):
        self.try_to_clean_db()

        try:
            result=self.db[id]

        except:
            return 0
        else:
            self.get.append(id)
            return result

    def try_to_clean_db(self):
        overflow =(len(self.db)>self.max)

        if overflow:
            num_to_delete=len(self.db)-self.max
            while self.get and num_to_delete:
                di=self.db[self.get.popleft()]
                del di
                num_to_delete-=1