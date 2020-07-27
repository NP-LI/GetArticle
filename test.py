from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from lxml import etree
import os
import requests
import csv


def test1():
    import MySQLdb

    # 打开数据库连接
    db = MySQLdb.connect("localhost", "root", "123456", "新闻", charset='utf8' )

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # 使用execute方法执行SQL语句
    cursor.execute("SELECT * FROM 军工武器新闻")

    # 使用 fetchone() 方法获取一条数据
    data = cursor.fetchone()

    print(data)

    # 关闭数据库连接
    db.close()


def test2():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    # 创建chrome浏览器驱动，无头模式
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized");
    driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)

    # 加载界面
    driver.get("https://mil.ifeng.com/shanklist/14-35083-")
    time.sleep(3)


    # 获取页面初始高度
    js = "return action=document.body.scrollHeight"
    height = driver.execute_script(js)

    # # 将滚动条调整至页面底部
    # driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    # time.sleep(5)
    a = driver.find_element_by_class_name('news-stream-basic-more')
    a.click()
    time.sleep(2)

    # 定义初始时间戳（秒）
    t1 = int(time.time())

    # 定义循环标识，用于终止while循环
    status = True

    # 重试次数
    num = 0

    while status:
        # 获取当前时间戳（秒）
        t2 = int(time.time())
        # 判断时间初始时间戳和当前时间戳相差是否大于30秒，小于30秒则下拉滚动条
        if t2 - t1 < 30:
            new_height = driver.execute_script(js)
            if new_height > height:
                a = driver.find_element_by_class_name('news-stream-basic-more')
                a.click()
                time.sleep(2)
                # 重置初始页面高度
                height = new_height
                # 重置初始时间戳，重新计时
                t1 = int(time.time())
        elif num < 3:  # 当超过30秒页面高度仍然没有更新时，进入重试逻辑，重试3次，每次等待30秒
            time.sleep(3)
            num = num + 1
        else:  # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
            print("滚动条已经处于页面最下方！")
            status = False
            # # 滚动条调整至页面顶部
            # driver.execute_script('window.scrollTo(0, 0)')
            break

    # 打印页面源码
    content = driver.page_source
    with open('凤凰.html', 'w', newline='', encoding='utf-8') as f:
        f.write(content)


def test3(url):
    import requests
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }

    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return 0
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def test4():

    # 创建一个无头浏览器对象
    chrome_options = Options()
    # 设置它为无框模式
    chrome_options.add_argument('--headless')
    # 如果在windows上运行需要加代码
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options)

    # 设置一个10秒的隐式等待
    browser.implicitly_wait(10)


    # 使用谷歌无头浏览器来加载动态js
    def start_get(url, news_type):
        browser.get(url)
        sleep(1)
        for one in range(30):
            # 翻到页底
            browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            sleep(1)
        # 拿到页面源代码
        source = browser.page_source
        parse_page(url, source)


    # 对新闻列表页面进行解析
    def parse_page(url, html):
        # 创建etree对象
        tree = etree.HTML(html)
        new_lst = tree.xpath('//ul[@id="recommend"]//a')
        for one_new in new_lst:
            title = one_new.xpath('.//h4/text()')[0]
            link = url + one_new.xpath('./@href')[0]
            try:
                write_in(title, link)
            except Exception as e:
                print(e)


    # 将其写入到文件
    def write_in(title, link, news_type):
        alist = []
        print('开始写入新闻:{}'.format(title))
        # response = requests.get(url=link)
        browser.get(link)
        sleep(1)
        # 再次翻页到底
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        # 拿到页面源代码
        source = browser.page_source
        tree = etree.HTML(source)

        # alist.append(news_type)
        # title = title.replace('?', '')
        alist.append(title)

        con_link = link
        alist.append(con_link)

        content_lst = tree.xpath('//section[@data-type="rtext"]/p')
        con = ''
        if content_lst:
            for one_content in content_lst:
                if one_content.text:
                    con = con + '\n' + one_content.text.strip()
            alist.append(con)

            # post_time_source = tree.xpath('//div[@class="left-t"]')[0].text

            post_time = tree.xpath('//div[@class="metadata-info"]//p[@class="time"]')[0].text
            alist.append(post_time)

            post_source = tree.xpath('//div[@class="metadata-info"]//span[@class="source"]//a')
            if post_source:
                post_source = post_source[0].text
            else:
                post_source = tree.xpath('//div[@class="metadata-info"]//span[@class="source"]//span')[0].text
            alist.append(post_source)
            # 1. 创建文件对象
            f = open('环球网n.csv', 'a+', encoding='utf-8', newline='')
            # 2. 基于文件对象构建 csv写入对象
            csv_writer = csv.writer(f)
            print(alist)
            csv_writer.writerow(alist)
            f.close()

        urls = ['https://mil.huanqiu.com/']
        i = 0
        news_types = ["军事"]
        for url in urls:
            # headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
            if not os.path.exists('data'):
                os.mkdir('data')
            news_type = news_types[i]
            start_get(url, news_type)
            i = i + 1
            browser.quit()


test2()

