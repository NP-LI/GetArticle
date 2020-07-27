import requests
import bs4
import csv
import re


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


def get_names_1(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    div = soup.find('div', attrs={'class': 'mw-parser-output'})
    uls = div.find_all('ol')
    if uls is None:
        return []
    names = []
    i = 1
    for ul in uls:
        lis = ul.find_all('li')
        # print(a_s)
        for li in lis:
            names.append(li.a.text)
    return names


def get_names(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    tables = soup.find_all('table', attrs={'class': 'wikitable'})
    # wikitable toccolours
    if tables is None:
        return []
    names = []
    for table in tables:
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        bool = True
        for tr in trs:
            # if bool:
            #     bool = False
            #     continue
            tds = tr.find_all('td')
            # for td in tds:
            if tds is None:
                continue
            i = 1
            for td in tds:
                if i == 2:
                    a_s = td.find_all('a')
                    if a_s is None:
                        continue
                    l = -1
                    for a in a_s:
                        l += 1
                    if l == -1:
                        continue
                    names.append(a_s[l].string)
                i += 1
    return names


if __name__ == '__main__':
    url = 'https://zh.wikipedia.org/wiki/%E8%8B%B1%E5%9B%BD%E9%99%86%E5%86%9B%E5%85%83%E5%B8%85%E5%88%97%E8%A1%A8'

    # html = fetch_url(url)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    # 创建chrome浏览器驱动，无头模式
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized");
    driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)
    driver.implicitly_wait(10)
    # 加载界面
    driver.get(url)
    html = driver.page_source
    time.sleep(3)
    names = get_names(html)
    print(names)
    with open('data/英国/英国陆军元帅列表.txt', 'w', newline='', encoding='utf-8') as f:
        # f.write(html)
        for name in names:
            f.write(name)
            f.write('\n')
