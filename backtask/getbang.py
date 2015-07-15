#coding:utf-8
'''
采集各大网站推荐榜的信息，排名前100的，更新url
'''
import threading
import requests
from model import *
from bs4 import BeautifulSoup
from novelutil import headers

#起点推荐榜信息
def update_bang_qidian():
    threads = []
    for x in xrange(1, 11):
        threads.append(threading.Thread(target=update_page_bang_qidian, args=(x,)))

    [t.start() for t in threads]
    [t.join() for t in threads]


#起点推荐榜信息
def update_page_bang_qidian(page_number):
    global headers
    urls = []
    while True:
        r = requests.get(url="http://top.qidian.com/Book/TopDetail.aspx?TopType=2&Time=3&PageIndex=%d" % page_number,
                         headers=headers, stream=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        if len(soup.find("div", id="list1").table.find_all("tr")[1:]) == 50:
            for line in soup.find("div", id="list1").table.find_all("a", class_="name"):
                urls.append(line["href"])

            for url in urls:
                if not db_session.query(Novel).filter(Novel.source_url == url).all():
                    if url.split('//')[1].split('/')[0] == 'free.qidian.com':
                        new_url = "http://www.qidian.com/Book/%s.aspx" % url.split('=')[1]
                        db_session.add(Novel(source_url=new_url))
                    else:
                        db_session.add(Novel(source_url=url))
                db_session.commit()
            break


#创世推荐榜信息
def update_bang_chuangshi():
    urls = []
    r = requests.get(url="http://chuangshi.qq.com/bang/tj/all-zong.html")
    soup = BeautifulSoup(r.content, 'html.parser')

    for line in soup.find("tbody", id="rankList").find_all("tr")[1:]:
        novel_url = line.find_all("a")[0]["href"]
        urls.append(novel_url)

    for url in urls:
        if not db_session.query(Novel).filter(Novel.source_url == url).all():
            db_session.add(Novel(source_url=url))
            db_session.commit()


#17k推荐榜信息
def update_bang_17k():
    urls = []
    r = requests.get(url="http://top.17k.com/flower_wz_all.shtml")

    soup = BeautifulSoup(r.content, 'html.parser')

    for line in soup.find("div", class_="list_wz").ul.find_all("li", class_="table_td"):
        novel_url = line.find("div", class_="zp").a["href"]
        urls.append(novel_url)

    for url in urls:
        if not db_session.query(Novel).filter(Novel.source_url == url).all():
            db_session.add(Novel(source_url=url))
            db_session.commit()


#纵横推荐榜信息
def update_bang_zongheng():
    bang_urls = []
    for x in xrange(1, 5):
        r = requests.get(url="http://book.zongheng.com/store/c0/c0/b9/u2/p%d/v9/s9/t0/ALL.html" % x)
        soup = BeautifulSoup(r.content, 'html.parser')
        urls = soup.find("ul", class_="main_con").find_all("a", class_="fs14")
        [bang_urls.append(url["href"]) for url in urls]

    for url in bang_urls:
        if not db_session.query(Novel).filter(Novel.source_url == url).all():
            db_session.add(Novel(source_url=url))
            db_session.commit()


if __name__ == '__main__':
    update_bang_qidian()
    update_bang_chuangshi()
    update_bang_17k()
    update_bang_zongheng()