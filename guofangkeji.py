import requests
import bs4
import csv
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
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def get_article(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    div = soup.find('div', attrs={'class': 'newsContent'})
    if div is None:
        return ''
    ps = div.find_all('p')
    if len(ps) == 0:
        # print(div)
        if div.text is not None:
            return delete_CRLF(div.text)
        return ''
    article = ''
    for p in ps:
        if p.text is None:
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
    return text


def get_urls():
    with open('data/国防科技新闻/国防科技新闻视点.csv', 'a+', newline='', encoding='utf-8') as f:
        csv_f = csv.writer(f)
        for i in range(1, 4004):
            try:
                print('正在爬取第' + str(i) + '页新闻链接')
                html = fetch_url('http://www.dsti.net/Information/ViewPointList/' + str(i))
                soup = bs4.BeautifulSoup(html, 'lxml')
                lis = soup.find('div', attrs={'class': 'listMidContent'}).ul.find_all('li')
                for li in lis:
                    csv_f.writerow([re.search('(?<=\[).*(?=\])', li.h2.text)[0], delete_CRLF(li.h1.a.text), 'http://www.dsti.net' + li.h1.a['href']])
            except:
                print('该链接不可用')


if __name__ == '__main__':
    # 2003 - 12 - 11有问题，先过滤掉
    # 师姐爬取到 2008-10-16
    print('国防科技新闻视点: 爬取开始')
    with open('data/国防科技新闻/国防科技新闻视点新闻2_2.csv', 'a+', newline='', encoding='utf-8') as f_w:
        csv_f_w = csv.writer(f_w)
        with open('data/国防科技新闻/error_urls.csv', 'a+', newline='', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            with open('data/国防科技新闻/国防科技新闻视点2_2.csv', 'r', encoding='utf-8') as f_r:
                csv_f_r = csv.reader(f_r)
                # article_list = []
                i = 1
                bool = True
                for row in csv_f_r:
                    if bool:
                        # 开始运行就好
                        if row[2] == 'http://www.dsti.net/Information/ViewPoint/38290':
                            bool = False
                        i += 1
                        continue
                    # if i > 20:
                    #     break
                    if row[0] == '2003-12-11':
                        f_csv.writerow([row[0].strip(), row[1].strip(), row[2].strip()])
                        print('错误链接' + '\t' + row[2])
                        # i += 1
                        continue
                    try:
                        html = fetch_url(row[2])
                        if html is None:
                            f_csv.writerow([row[0].strip(), row[1].strip(), row[2].strip()])
                            print('错误链接' + '\t' + row[2])
                            # i += 1
                            continue
                        article = get_article(html)
                        if article == '':
                            f_csv.writerow([row[0].strip(), row[1].strip(), row[2].strip()])
                            print('错误链接' + '\t' + row[2])
                            # i += 1
                            continue
                        # article_list.append([row[0].strip(), row[1].strip(), article.strip()])
                        # if i % 10 == 0:
                        #     csv_f_w.writerows(article_list)
                        #     article_list.clear()
                        #     print(str(i - 9) + '-----' + str(i))
                        csv_f_w.writerow([row[0].strip(), row[1].strip(), article.strip()])
                        print(str(i) + '\t' + row[2])
                        i += 1
                    except:
                        f_csv.writerow([row[0].strip(), row[1].strip(), row[2].strip()])
                        print('该篇新闻无法爬取')

    # with open('data/error_urls.csv', 'a+', newline='', encoding='utf-8') as f:
    #     f_csv = csv.writer(f)
    #     for url in error_urls:
    #         f.write([url[0], url[1], url[2]])
