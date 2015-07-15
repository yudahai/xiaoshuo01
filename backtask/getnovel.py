#coding:utf-8
from backtask.soupnovel import *
from model import *
from novelutil import produce_consume, headers
import threading


def update_single_infor(url, add=False):
    """
    根据url跟新novel_infor中的 时间、字数、推荐数、描述等
    """
    resp = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.content, "html.parser")
    deal_route = {
        'www.qdmm.com': soup_qdmm,
        'free.qidian.com': soup_free,
        'www.qdwenxue.com': soup_qdwenxue,
        'www.qidian.com': soup_qidian,
        'chuangshi.qq.com': soup_chuangshi,
        'www.17k.com': soup_17k,
        'book.zongheng.com': soup_zongheng,
        'huayu.baidu.com': soup_huayu,
        'www.xbiquge.com': soup_xbiquge
                  }

    for key in deal_route:
        if resp.url.split('//')[1].split('/')[0] == key:
            new_novel = deal_route[key](soup)

            new_novel.source_url = url
            resp.close()

            if add:
                db_session.add(new_novel)
                db_session.flush()
                newid = new_novel.id
                db_session.commit()
                return newid
            else:
                db_session.query(Novel).filter(Novel.source_url == new_novel.source_url).update({
                    "name": new_novel.name, "author": new_novel.author, "type": new_novel.type, "recommend": new_novel.recommend,
                    "image": new_novel.image, "description": new_novel.description, "words_count": new_novel.words_count,
                    "last_update": new_novel.last_update
                })


def update_infor():
    """
    #更新novel小说信息，比如：最近更新时间，字数，推荐数
    """
    threads = []
    urls = db_session.query(Novel.source_url).all()
    for url in urls:
        threads.append(threading.Thread(target=update_single_infor, args=(url[0],)))
    produce_consume(threads, 50)


def update_single_novel_content_url(url):
    """
    根据url更新novel_infor表中的novel_content_url信息，如果已经存在infor信息，只添加 novel_content_url信息；否则加入完整信息
    """
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    result = soup_xbiquge(soup)
    result.append(url)
    result.append(url)
    novel_name, novel_author = result[0], result[3]
    db_session.query(Novel).filter(and_(Novel.name == novel_name, Novel.author == novel_author)).update({"chapter_source_bequge_url": url})
    db_session.commit()


def update_chapter_infor():
    """
    根据novel_content_url更新chapter表的 url和 name 信息
    """
    threads = []
    novel_content_id_urls = db_session.query(Novel.id, Novel.source_url).filter(Novel.source_url is not None).all()
    for novel_id, url in novel_content_id_urls:
        threads.append(threading.Thread(target=update_single_chapter_infor, args=(novel_id, url,)))

    produce_consume(threads, 5)


def update_single_chapter_infor(novel_id, url):
    """
    #更新chapter表的 url和 name 信息
    """
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.content.decode("utf8"), 'html.parser')
    result = soup_chapter_title_xbiquge(soup, url=url)
    old_chapters = db_session.query(Chapter.name, Chapter.url).filter(and_(Chapter.novel_id == novel_id,
                                                                           Chapter.content_source == 2)).all()
    new_chapters = [x for x in result if x not in old_chapters and x[1] != 'dt']

    for item in new_chapters:
        new_chapter = Chapter(novel_id=novel_id, url=item[0], name=item[1], content_source=2)
        db_session.add(new_chapter)
    db_session.commit()

    update_single_chapter_last_and_next(novel_id, source=2)


def update_single_chapter_last_and_next(novel_id, source):
    """
    #更新chapter表中之间last_chapter和next_chapter关系
    """
    items = db_session.query(Chapter.id, Chapter.last_chapter, Chapter.next_chapter).\
        filter(and_(Chapter.novel_id == novel_id, Chapter.content_source == source)).order_by(Chapter.id).all()

    items = list(items)
    items = [list(item) for item in items]

    for item in items:
        if item == items[0]:
            item[2] = items[1][0]
        elif item == items[-1]:
            item[1] = items[-2][0]
        else:
            item[1] = items[items.index(item)-1][0]
            item[2] = items[items.index(item)+1][0]

    query_chapter = db_session.query(Chapter)
    for item in items:
        query_chapter.filter(Chapter.id == item[0]).update({Chapter.last_chapter: item[1], Chapter.next_chapter: item[2]})
        db_session.flush()
    db_session.commit()


"""
根据chapter_url更新novel_chapter中的chapter_content内容
"""
#更新novel_chapter中的chapter_content内容
def update_single_chapter_content(url, chapter_id):
    global headers
    r = requests.get(url=url, headers=headers)

    if r.url.split('//')[1].split('/')[0] == 'www.xbiquge.com':
        content = r.content.decode('utf8')
        soup = BeautifulSoup(content, 'html.parser')
        chapter_content = soup_chapter_content_xbiquge(soup)

        db_session.query(Chapter).filter(Chapter.id == chapter_id).update({"content": chapter_content})
        db_session.commit()


def update_chapter_content(novel_id):
    threads = []
    chapter_content_empty_items = db_session.query(Chapter.id, Chapter.url).filter(and_(Chapter.novel_id == novel_id,
                                                                                        Chapter.content_source == 2,
                                                                                        Chapter.content == None
                                                                                        )).all()
    for chapter_id, chapter_url in chapter_content_empty_items:
        threads.append(threading.Thread(target=update_single_chapter_content, args=(chapter_url, chapter_id, )))
    produce_consume(threads=threads, MAX_THREADS=5)


if __name__ == '__main__':
    #update_single_infor('http://www.qidian.com/Book/18636.aspx')
    update_infor()