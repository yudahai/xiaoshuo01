#coding:utf-8
import random
import urllib2
import threading
import cookielib
import urllib
import os
from model import *
from bs4 import BeautifulSoup
from novelutil import produce_consume

novel_text_path = os.path.join('/'.join(os.getcwd().split('/')[:-1]), 'uploads/novel_txt')


def update_novel_infor():
    threads = []
    for x in range(1, 440):
        threads.append(threading.Thread(target=_update_single_novel_infor, args=(x, )))

    produce_consume(threads, 2)


def _update_single_novel_infor(x):
    url = "http://www.ybdu.com/book/allvisit/0/%d/" % x
    response = urllib2.urlopen(url)

    results = []
    content = response.read().decode("gbk", errors='ignore')
    soup = BeautifulSoup(content, 'html.parser')
    items = soup.find("div", class_="rec_rullist").find_all("ul")
    for item in items:
        novel_name = item.find("li", class_="three").a.text[:-5]
        novel_download_url = item.find("li", class_="three").a["href"]
        novel_download_url = "http://www.ybdu.com/modules/article/packdown.php?" + "id=" + \
                             novel_download_url.split('/')[-2] + "&type=txt" + "&fname=" + novel_name
        novel_author = item.find("li", class_="four").a.text
        novel_words_count = int(item.find("li", class_="five").text[:-1]) * 1024
        novel_last_update = "20" + item.find("li", class_="six").text
        novel_type = item.find("li", class_="sev").text[2:4]

        results.append((novel_name, novel_author, novel_download_url, novel_type, novel_last_update,
                        novel_words_count, ))

    import sqlalchemy

    for result in results:
        try:
            novel = db_session.query(Novel).filter(and_(Novel.name == result[0], Novel.author == result[1])).one()
        except sqlalchemy.orm.exc.NoResultFound:
            new_novel = Novel(name=result[0], author=result[1], chapter_source_ybd_url=result[2], type=result[3],
                              last_update=result[4], words_count=result[5])
            db_session.add(new_novel)
            db_session.commit()
        else:
            novel.chapter_source_ybd_url = result[2]
            novel.last_update = result[4]
            db_session.commit()


def _gen_username_email():
    list1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
             'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f',
             'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    username = ''.join(random.sample(list1, random.randint(6, 11)))
    email = ''.join(random.sample(list1, random.randint(6, 11))) + '@163.com'
    return username, email


def get_single_novel_text(download_url, novel_name, novel_id, novel_text_path):
    username, email = _gen_username_email()

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler)

    values = {"action": "newuser", "email": email, "password": "A12345678",
               "repassword": "A12345678", "sex": "0", "username": username}

    data = urllib.urlencode(values)
    request = urllib2.Request("http://www.ybdu.com/register.php?do=submit", data)
    opener.open(request)

    response = opener.open(download_url)
    novel_content = response.read().decode('gbk', errors='ignore')

    with open(novel_text_path + '/' + novel_id + '.text', 'ab') as f:
        f.write(novel_content.encode('utf-8'))

    print novel_name, u':下载完成'


#从upload里面 选取任一个text文件，已经分析，存入数据库
def single_from_text_store_sql(novel_text_path, novel_id):
    import codecs
    with codecs.open(os.path.join(novel_text_path, str(novel_id)+'.text'), 'rb', encoding='utf-8') as f:
        chapter_content, chapter_name = '', ''
        deal_first_time = True
        for line in f.readlines():
            if line[:2] != u'  ' and line != u'\r\n' and line != u'\n' and len(line) < 40 and line[0] != u'—' and line[0] != u'.':
                if not deal_first_time:
                    chapter = Chapter(name=chapter_name, content=chapter_content, novel_id=novel_id)
                    db_session.add(chapter)
                    db_session.commit()
                chapter_name = line
                deal_first_time = False
                chapter_content = ''
            else:
                chapter_content += line

if __name__ == "__main__":
    get_single_novel_text("http://www.ybdu.com/modules/article/packdown.php?id=14066&type=txt&fname=易圣", u'易圣', u'15237', novel_text_path)
    #update_novel_infor()
    #_update_single_novel_infor(3)



