from urllib import request
from bs4 import BeautifulSoup

class OpenURLError(BaseException):
    def __init__(self,msg):
        BaseException.__init__(self)
        self.msg=msg

def runspider(url):
    try:
        html = request.urlopen(url)
    except:
        print("open url wrong")
        raise OpenURLError('Can not open url: '+url)

    soup = BeautifulSoup(html.read(),'lxml')
    title = soup.find('h2',{'class':"rich_media_title"}).get_text().strip()
    content = soup.find('div',{'class':"rich_media_content"}).get_text().strip()
    content.replace('\xa0', '')
    article = {
        'url': url,
        'title': title,
        'content': content
    }
    return article

if __name__ == "__main__":
    url = 'https://mp.weixin.qq.com/s/bjkmpigQNlwow4AhW3wdqw'
    article = runspider(url)
    print(article)