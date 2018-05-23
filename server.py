import tornado.ioloop,tornado.web
from queue import Queue
import threading,json
from tornado import gen
from threads import *

from spider import *
from db import *

MAX_EXTHREAD_NUM=4

mainMutex=threading.Lock()
dbMutex=threading.Lock()

articleQueue=Queue()


class MainStatus:
    def __init__(self):
        self.request_number=0

    def get_request_id(self):
        self.request_number+=1
        return self.request_number

    def get_request_number(self):
        return self.request_number

mainStatus=MainStatus()
mainDB=Database(1000)

calcThreadPool=[]
for i in range(0,MAX_EXTHREAD_NUM+1):
    new_thread=CalcThread(articleQueue,mainDB,dbMutex)
    new_thread.daemon=True
    calcThreadPool.append(new_thread)

class BaseHandler(tornado.web.RequestHandler):


    def write_error(self, status_code,**kwargs):
        self.finish("<html><title>%(code)d: %(message)s</title>"
                    "<body>%(code)d: %(message)s</body></html>" % {
                        "code": status_code,
                        "message": kwargs['content'],
                    })

class PostHandler(BaseHandler):
    def get(self):
        raise tornado.web.HTTPError(403)

    def post(self):
        try:
            name,url=self.get_body_argument('name'),self.get_body_argument('url')
            try:
                article=runspider(url)
            except OpenURLError as e:
                self.write_error(500,content=e.msg)
            else:
                with mainMutex:
                    request_id=mainStatus.get_request_id()

                articleQueue.put((request_id,name,article))
                self.write(str(request_id))

        except BaseException as e:
            self.write_error(500,content=str(e.args))

class GetHandler(BaseHandler):
    def post(self):
        self.write_error(403,content='403 Forbidden: \nYou should not post to here.')

    def get(self):
        if 'id' in self.request.arguments:
            request_id=int(self.get_argument('id'))
            with dbMutex:
                result=mainDB.get_result(request_id)

            if result:
                result=json.dumps(result[ARTICLE_REPORT])
                self.write(result)
            else:
                self.write_error(403,content='No Result')
        else:
            self.write_error(403,content="403 Forbidden:\nYou should provide an id in url")

class HomeHandler(BaseHandler):
    def get(self):
        self.write('Welcome!')

def make_app():
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/post", PostHandler),
        (r"/get", GetHandler),
    ])


if __name__=='__main__':
    app = make_app()
    app.listen(8888)

    for thread in calcThreadPool:
        thread.start()
    print("All threads started.")

    tornado.ioloop.IOLoop.current().start()