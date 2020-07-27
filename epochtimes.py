import requests
import bs4
import csv
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from time import sleep
import re


error_urls = []
now_url = []


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



def get_article(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
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


def get_urls():
    with open('data/大纪元/全球要闻链接.csv', 'a+', newline='', encoding='utf-8') as f:
        csv_f = csv.writer(f)

        for i in range(1152, 1190):
            # url = 'https://www.epochtimes.com/gb/nimpart_' + str(i) + '.htm'
            # driver.get(url)
            # sleep(1)
            # html = driver.page_source
            # https: // www.epochtimes.com / gb / nsc418_9215.htm
            html = fetch_url('https://www.epochtimes.com/gb/nimpart_' + str(i) + '.htm')
            if html is None:
                i += 1
                continue
            soup = bs4.BeautifulSoup(html, 'lxml')
            divs = soup.find('div', attrs={'id': 'artlist'}).find_all('div', attrs={'class': 'posts column'})
            # print(divs)
            j = 0
            for div in divs:
                csv_f.writerow([delete_CRLF(div.find('div', attrs={'class': 'post-date'}).text),
                                delete_CRLF(div.find('div', attrs={'class': 'arttitle'}).text),
                                delete_CRLF(div.find('div', attrs={'class': 'arttitle'}).a['href'])])
                j += 1
            print('已爬取第' + str(i) + '页新闻链接\t' + '共' + str(j) + '个新闻')
            i += 1


if __name__ == '__main__':
    # get_urls()

    print('大纪元全球要闻: 爬取开始')
    with open('data/大纪元/全球要闻/全球要闻新闻3.csv', 'a+', newline='', encoding='utf-8') as f_w:
        csv_f_w = csv.writer(f_w)
        with open('data/大纪元/error_urls.csv', 'a+', newline='', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            with open('data/大纪元/全球要闻/全球要闻链接3.csv', 'r', encoding='utf-8') as f_r:
                csv_f_r = csv.reader(f_r)
                i = 1
                # 爬到该链接 https://www.epochtimes.com/gb/19/11/12/n11650401.htm
                tag = True
                for row in csv_f_r:
                    # if i > 10000:
                    #     break
                    if tag:
                        if row[2] == 'https://www.epochtimes.com/gb/19/2/4/n11022771.htm':
                            tag = False
                        i += 1
                        continue

                    try:
                        html = fetch_url(row[2])
                        if html is None:
                            f_csv.writerow([row[0], row[1], row[2]])
                            print('错误链接' + '\t' + row[2])
                            # i += 1
                            continue
                        article = get_article(html)
                        if article == '':
                            f_csv.writerow([row[0], row[1], row[2]])
                            print('错误链接' + '\t' + row[2])
                            continue
                        csv_f_w.writerow([row[0], row[1], article])
                        print(str(i) + '\t' + row[2])
                        i += 1
                    except:
                        f_csv.writerow([row[0], row[1], row[2]])
                        print('该篇新闻无法爬取')

