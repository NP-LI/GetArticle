import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import csv


def get_article(html):
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', attrs={'id': 'artbody'})
    if div is None:
        return ''
    blockquote = div('blockquote')
    if blockquote is not None:
        for b in blockquote:
            b.extract()

    figure = div('figure')
    if figure is not None:
        for f in figure:
            f.extract()

    h2 = div('h2')
    if h2 is not None:
        for h in h2:
            h.extract()

    h3 = div('h3')
    if h3 is not None:
        for h in h3:
            h.extract()

    h4 = div('h4')
    if h4 is not None:
        for h in h4:
            h.extract()

    ps = div.find_all('p')
    # ps = div.children
    if len(ps) == 0:
        # print(div)
        if div.text is not None:
            return delete_CRLF(div.text)
        return ''
    article = ''
    for p in ps:
        # print(p)
        if p.text is None:
            continue
        if p.text == '':
            continue
        article += delete_CRLF(p.text)
    return article


def delete_CRLF(string):
    string = string.split('\n')
    text = ''
    for s in string:
        text += s
    string = text

    string = string.split('\r')
    text = ''
    for s in string:
        text += s
    return text.strip()


def fetch_url(url):
    """
    功能：访问 url 的网页，获取网页内容并返回
    参数：目标网页的 url
    返回：目标网页的 html 内容
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    i = 0
    while i < 3:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            return r.text
        except requests.exceptions.RequestException:
            i += 1
    return None


def start(url):
    try:
        html = fetch_url(url[2])
        if html is None:
            with open('data/大纪元/error_urls_test.csv', 'a+', newline='', encoding='utf-8') as f:
                csv_error = csv.writer(f)
                csv_error.writerow([url[0], url[1], url[2]])
            return None
        article = get_article(html)
        if article == '':
            with open('data/大纪元/error_urls_test.csv', 'a+', newline='', encoding='utf-8') as f:
                csv_error = csv.writer(f)
                csv_error.writerow([url[0], url[1], url[2]])
            return None
        # with open('data/大纪元/全球要闻新闻测试.csv', 'a+', newline='', encoding='utf-8') as f_w:
        #     csv_f_w = csv.writer(f_w)
        #     csv_f_w.writerow([url[0], url[1], article])
        lock.acquire()
        global now
        print(str(now) + '\t' + url[2])
        now += 1
        lock.release()
        return article
    except:
        print('该篇新闻无法爬取')


def run(url_q, article_q):
    while url_q.empty() is not True:
        url = url_q.get()
        article = start(url)
        if article is not None:
            article_q.put([url[0], url[1], article])
        if article_q.full():
            with open('data/大纪元/全球要闻新闻测试.csv', 'a+', newline='', encoding='utf-8') as f_w:
                csv_f_w = csv.writer(f_w)
                csv_f_w.writerows(article_q.queue)
            article_q.queue.clear()
        url_q.task_done()


if __name__ == '__main__':
    url_queue = Queue()
    article_queue = Queue(maxsize=10)
    with open('data/大纪元/全球要闻/全球要闻链接1.csv', 'r', encoding='utf-8') as f_r:
        csv_f_r = csv.reader(f_r)
        i = 1
        for row in csv_f_r:
            if i > 50:
                break
            url_queue.put([row[0], row[1], row[2]])
            i += 1
    print('待爬取新闻数 %d' % url_queue.qsize())
    now = 1
    lock = threading.Lock()
    for index in range(10):
        thread = Thread(target=run, args=(url_queue, article_queue, ))
        thread.daemon = True  # 随主线程退出而退出
        thread.start()
        # thread.join()

    url_queue.join()  # 队列消费完 线程结束
    print("main thread start")
    if article_queue.empty() is not True:
        with open('data/大纪元/全球要闻新闻测试.csv', 'a+', newline='', encoding='utf-8') as f_w:
            csv_f_w = csv.writer(f_w)
            csv_f_w.writerows(article_queue.queue)
    print("main thread end")




