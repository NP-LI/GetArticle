import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import csv


def get_content(html):
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
    content = ''
    for p in ps:
        # print(p)
        if p.text is None:
            continue
        if p.text == '':
            continue
        content += delete_CRLF(p.text)
    return content


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


def article_start(url, error_url_path):
    try:
        html = fetch_url(url[2])
        if html is None:
            with open(error_url_path, 'a+', newline='', encoding='utf-8') as f:
                csv_error = csv.writer(f)
                csv_error.writerow([url[0], url[1], url[2]])
            return None
        content = get_content(html)
        if content == '':
            with open(error_url_path, 'a+', newline='', encoding='utf-8') as f:
                csv_error = csv.writer(f)
                csv_error.writerow([url[0], url[1], url[2]])
            return None
        # lock.acquire()
        # global now
        print(str(url[3]) + '\t' + url[2])
        # now += 1
        # lock.release()
        return content
    except:
        with open(error_url_path, 'a+', newline='', encoding='utf-8') as f:
            csv_error = csv.writer(f)
            csv_error.writerow([url[0], url[1], url[2]])
        print('该篇新闻无法爬取')


def get_article(url_q, article_q, article_path, error_url_path):
    while url_q.empty() is not True:
        url = url_q.get()
        article = article_start(url, error_url_path)
        if article is not None:
            article_q.put([url[0], url[1], article])
        if article_q.full():
            with open(article_path, 'a+', newline='', encoding='utf-8') as f_w:
                csv_f_w = csv.writer(f_w)
                csv_f_w.writerows(article_q.queue)
            article_q.queue.clear()
        url_q.task_done()


def get_article_start(url_path, article_path, error_url_path):
    url_queue = Queue()
    article_queue = Queue(maxsize=10)
    with open(url_path, 'r', encoding='utf-8') as f_r:
        csv_f_r = csv.reader(f_r)
        i = 1
        for row in csv_f_r:
            # if i > 200000:
            #     break
            url_queue.put([row[0], row[1], row[2], i])
            i += 1
    print('待爬取新闻数 %d' % url_queue.qsize())
    for index in range(10):
        thread = Thread(target=get_article, args=(url_queue, article_queue, article_path, error_url_path, ))
        thread.daemon = True
        thread.start()

    url_queue.join()
    if article_queue.empty() is not True:
        with open(article_path, 'a+', newline='', encoding='utf-8') as f_w:
            csv_f_w = csv.writer(f_w)
            csv_f_w.writerows(article_queue.queue)


if __name__ == '__main__':
    get_article_start('data/大纪元/国际要闻/国际要闻链接1.csv', 'data/大纪元/国际要闻/国际要闻新闻1.csv', 'data/大纪元/error_urls_1.csv')




