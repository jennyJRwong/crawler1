# 线程
import threading
#队列
from queue import Queue
from lxml import etree
import requests
import json

class ThreadCrawl(threading.Thread):
    def __init__(self,threadname,pageQueue,dataQueue):
        # 调用父类初始化方法
        super(ThreadCrawl,self).__init__()
        # 线程名
        self.threadName = threadname
        # 页码队列
        self.pageQueue = pageQueue
        # 数据队列
        self.dataQueue = dataQueue
        # 请求头
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    def run(self):
        print('启动'+self.threadName)
        while not CRAWL_EXIT:
            try:
                # 取出一个数字，先进先出
                # 可选参数black，默认值为True
                #1。如果队列为空，block为True的话，不会结束，会进入阻塞状态，直到队列有新的数据
                #2。如果队列为空，block为False的话，就弹出一个Queue.empty()异常
                page = self.pageQueue.get(False)
                url = 'http://www.qiushibaike.com/8hr/page/'+str(page)+'/'
                content = requests.get(url,headers = self.headers)
                self.dataQueue.put(content)
            except:
                pass
class ThreadParse(threading.Thread):
    def __init__(self,threadName,dataQueue,filename):
        super(ThreadParse,self).__init__()
        self.threadName = threadName
        self.dataQueue = dataQueue
        # 保存解析数据的文件名
        self.filename = filename
        while not PARSE_EXIT:
            try:
                html = self.dataQueue.get(False)
                self.parse(html)
            except:
                pass
    def parse(self,html):
        html = etree.HTML(html)
        node_list = html.xpath('//div[contains(@id,"qiushi"]')
        items = {}
        for node in node_list:
            username = node.xpath('./div/a/@title')[0] #xpath返回的是list，只有一个内容，【0】取里面的字符串
            content = node.xpath('.//div/[@class="content]')[0].text
            items={
                'username':username
                "content":content
            }
        self.filename.write(json.dumps(items,ensure_ascii=False).encode('utf-8')+'\n')

CRAWL_EXIT = False
PARSE_EXIT = False
def main():
    # 页码队列，表示10个页面
    pageQueue = Queue(10)
    # 放入1-10的数字先进先出
    for i in range(1,11):
        pageQueue.put(i)

    #采集结果（每页HTML源码）的数据队列，参数为空表示不限制
    dataQueue = Queue()
    filename = open('duanzi.json','a')

    # 3个采集线程的名字
    crawList = ['采集线程1号','采集线程2号','采集线程3号']

    # 存储3个采集线程
    threadCrawl = []
    for threadName in crawList:
        thread = ThreadCrawl(threadName,pageQueue,dataQueue) #ThreadCrawl是自己创建的类
        thread.start()
        threadCrawl.append(thread)

    parseList = ['解析线程1号','解析线程2号','解析线程3号']
    # 存储3个解析线程
    threadparse = []
    for threadName in parseList:
        thread = ThreadCrawl(threadName,dataQueue,filename)
        thread.start()
        threadparse.append(thread)

    # 等待pageQueuq队列为空，就是等待之前的操作执行完毕
    while  not pageQueue.empty():
        pass
    # 如果pageQueuq队列为空，采集线程退出循环
    global CRAWL_EXIT
    CRAWL_EXIT = True
    print('pageQueuq队列为空')

    # 阻塞状态
    for thread in threadCrawl:
        thread.join()
        print('')
    filename.close()

if __name__ == '__main__':
    main()
