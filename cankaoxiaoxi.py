import requests
import bs4
import csv


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
    # fs-small
    # ps = soup.find('div', attrs={'class': 'articleText'}).find_all('p')
    div = soup.find('div', attrs={'class': 'articleText'})
    if div is None:
        div = soup.find('div', attrs={'class': 'fs-small'})
    if div is None:
        return ''
    ps = div.find_all('p')
    article = ''
    for p in ps:
        if p.strong is not None:
            p.strong.extract()
            article += p.text
            continue
        if p.a is not None:
            p.a.extract()
            article += p.text
            continue
        if p.string is None:
            continue
        article += p.string
    return article


if __name__ == '__main__':
    for file in ['中国军情', '国际军情', '武器装备']:
        print(file + ' 爬取开始')
        with open('data/' + file + '新闻.csv', 'w', newline='', encoding='utf-8') as f_w:
            csv_f_w = csv.writer(f_w)
            with open('data/' + file + '.csv', 'r', encoding='utf-8') as f_r:
                csv_f_r = csv.reader(f_r)
                i = 1
                for row in csv_f_r:
                    try:
                        html = fetch_url(row[2])
                        if html is None:
                            continue
                        article = get_article(html)
                        for page in range(2, 50):
                            html = fetch_url(row[2][:-6] + '_' + str(page) + '.shtml')
                            if html is None:
                                break
                            article += get_article(html)
                        csv_f_w.writerow([row[0], row[1], article])
                        print(str(i) + '\t' + row[2])
                        i += 1
                    except:
                        print('该篇新闻无法爬取')

