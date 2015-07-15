#coding:utf-8
from bs4 import BeautifulSoup
import requests
from model import Novel

#分析qdmm
def soup_qdmm(soup):
    title = soup.find("div", class_="title")
    name = title.find("strong", itemprop="name").text.strip()
    author = title.find("span", itemprop="name").text.strip()
    info_box = soup.find("div", class_="info_box")
    type = info_box.find("span", itemprop="genre").text.strip()
    recommend = info_box.find("span", itemprop="totalRecommend").text.strip()
    image = soup.find("div", class_="pic_box").img["src"]
    description = soup.find("span", itemprop="description").get_text("\n")
    words_count = info_box.find("span", itemprop="wordCount").text
    last_update = soup.find("div", class_="tabs").find("div", class_="right").text.strip()

    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析free
def soup_free(soup):
    title = soup.find("div", class_="title")
    name = title.find("h1", itemprop="name").text
    author = title.find("span", itemprop="name").text

    info_box = soup.find("div", class_="info_box")
    type = info_box.find("span", itemprop="genre").text
    recommend = info_box.find("span", itemprop="totalRecommend").text
    last_update = None
    words_count = info_box.find("span", itemprop="wordCount").text

    image = soup.find("div", class_="pic_box").img["src"]
    description = soup.find("span", itemprop="description").get_text("\n")
    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析qdwenxue
def soup_qdwenxue(soup):
    title = soup.find("div", class_="title")
    name = title.find("h1").text.strip()
    author = title.find("a").text.strip()

    info_box = soup.find("div", class_="info_box").find_all("td")
    type = info_box[4].a.text
    recommend = info_box[5].text.split(u"：")[1].strip()
    words_count = info_box[9].text.split(u"：")[1].strip()

    last_update = soup.find("div", class_="tabs").find("div", class_="right").text.strip()

    data = soup.find("div", class_="data").find_all("td")
    image = soup.find("div", class_="pic_box").img["src"]
    description = soup.find("div", class_="txt")
    description.script.extract()
    description.script.extract()
    description.b.extract()
    description = description.get_text("\n").strip()
    #novel_words_count = novel_data[3].text.split(u"：")[1].strip()
    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析起点
def soup_qidian(soup):
    title = soup.find("div", class_="title")
    name = title.find("h1", itemprop="name").text.strip()
    author = title.find("span", itemprop="name").text.strip()

    last_update = soup.find("div", class_="tabs").find("span", itemprop="dateModified").text

    info_box = soup.find("div", class_="info_box")
    type = info_box.find("span", itemprop="genre").text
    recommend = info_box.find("span", itemprop="totalRecommend").text
    words_count = info_box.find("span", itemprop="wordCount").text

    image = soup.find("div", class_="pic_box").img["src"]
    description = soup.find("span", itemprop="description").get_text("\n")

    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析创世
def soup_chuangshi(soup):
    title = soup.find_all("div", class_="title")[1].find_all("a")
    name = title[3].text
    type = title[2].text

    image = soup.find("a", class_="bookcover").img["src"]
    description = soup.find("div", class_="info").get_text("\n")


    infor = soup.find("div", id="novelInfo").find_all("tr")
    words_count = infor[4].find_all("td")[0].text.split(u"：")[1]
    recommend = infor[1].find_all("td")[2].text.split(u"：")[1]

    chaptername = soup.find("div", id="newChapterList").div
    chaptername.b.extract()
    chaptername.span.extract()
    last_update = chaptername.text[6:25]
    return Novel(name=name, author=None, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析17k
def soup_17k(soup):
    bookTit = soup.find("div", class_="bookTit").find_all("font", itemprop="name")
    name = bookTit[0].text
    author = bookTit[1].text

    bookBox_l = soup.find("div", class_="bookBox_l")
    image = bookBox_l.find("img", itemprop="image")["src"]
    recommend = bookBox_l.find("li", id="postFlower").text

    bookBox_r = soup.find("div", class_="bookBox_r")
    description = bookBox_r.find("font", itemprop="description").text
    words_count = bookBox_r.find("em", itemprop="wordCount").text

    last_update = soup.find("span", class_="time").text.split(u"：")[1]
    last_update = '2010-01-01'
    type = soup.find("div", id="tab91_div1").find("font", itemprop="genre").get_text("\n")

    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析创世的作者
def soup_chuangshi_author(url):
    new_url = url[:-5]+'-r-10.html'
    r = requests.get(new_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    novel_author = soup.find("div", class_="toptool_left").span.a.text
    return novel_author


#分析花语
def soup_huayu(soup):
    lebg = soup.find("div", class_="lebg")
    name = lebg.h1.find("a").text
    author = lebg.h1.find_all("a")[1].text
    info = lebg.find("div", class_="booknumber").text.split("\n")

    recommend = info[3].split(u'：')[1].strip()
    last_update = info[5].split(u'：')[1].strip()
    words_count = info[2].split(u'：')[1].strip()
    type = soup.find("div", class_="loca").find_all("a")[2].text
    image = soup.find("div", class_="bookinfo").find("img")["src"]
    description = soup.find("div", class_="bookinfo").find("p", class_="jj").text
    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析笔趣阁
def soup_xbiquge(soup):
    info = soup.find("div", id="info")
    name = info.find("h1").string.strip()
    author = info.p.string.strip().split(u"：")[1]
    last_update = info.find_all("p")[2].text.split(u"：")[1]
    description = soup.find("div", id="intro").get_text("\n").strip()
    image = "http://www.biquwo.com"+soup.find("div", id="fmimg").img["src"]
    type = soup.find("div", class_="con_top").find_all("a")[2].text
    words_count = None
    recommend = None
    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析纵横，得到novel的infor
def soup_zongheng(soup):
    status = soup.find("div", class_="status")
    name = status.find_all("a")[1].text
    author = status.find_all("a")[0].text
    type = status.find_all("a")[2].text
    words_count = status.find("span", itemprop="wordCount").text
    recommend = status.find("div", class_="booksub").find_all("span")[2].text
    description = status.find("div", class_="info_con").text.strip()
    last_update = soup.head.find_all("meta")[22]["content"]
    image = soup.find("div", class_="book_cover").find("img")["src"]
    return Novel(name=name, author=author, type=type, recommend=recommend, image=image,
                 description=description, words_count=words_count, last_update=last_update)


#分析笔趣阁，得到其chapter的url和name
def soup_chapter_title_xbiquge(soup, url):
    chapter_titles_worked = []
    chapter_titles = soup.find("div", id="list").dl.find_all(["dt", "dd"])

    for item in chapter_titles:
        if item.name == "dd":
            chapter_titles_worked.append([url+item.a["href"], item.a.text])

    return chapter_titles_worked


#分析xbiquge章节内容，并且返回章节内容
def soup_chapter_content_xbiquge(soup):
    #soup.find("div", id="content").script.extract()
    #soup.find("div", id="content").p.extract()
    #soup.find("div", id="content").p.extract()
    chapter_content = soup.find("div", id="content").get_text('\n')
    return chapter_content