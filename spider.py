from urllib import request
from bs4 import BeautifulSoup
import re

def runspider(url):
    try:
        html = request.urlopen(url)
    except:
        print("Spider:open url wrong")
        return

    try:
        soup = BeautifulSoup(html.read(),'lxml')
        title = soup.find('h2',{'class':"rich_media_title"}).get_text().strip()
        pattern = re.compile(r"<span class=\'rich_media_title_ios\'>(.*?)</span>")
        title = re.search(pattern,title).groups()[0]
        content = soup.find('div',{'class':"rich_media_content"}).get_text().strip()
        content.replace('\xa0', '')
        article = {
            'url': url,
            'title': title,
            'content': content
        }
        return article
    except Exception as e:
        print("Spider:parse wrong\n",e)

if __name__ == "__main__":
    url = 'https://mp.weixin.qq.com/s/bjkmpigQNlwow4AhW3wdqw'
    article = runspider(url)
    print(article)