from lxml import etree
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from multiprocessing import Process
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import threading
import os

'''
#多进程：相当于创建多个部门来完成工作
plist=[]
for item in []:
    p = Process(target='要执行的任务',args='这个任务执行的对象')
    #生成进程
    p.start()
    plist.append(p)
#阻塞终止进程的执行
[i.join() for i in plist]
os.getpid()#可以查看正在工作的进程

#多线程：相当于给这个部门增加多几个人手工作
plist=[]
for item in []:
    #循环创建线程
    p = Thread(target='要执行的任务',args='这个任务执行的对象')
    #生成线程
    p.start()
    plist.append(p)
#阻塞终止线程的执行
[i.join() for i in plist]
threading.current_thread()#查看正在工作的线程

#线程池
#创建线程
pool = ThreadPoolExecutor(max_workers='你需要并行计算的个数')
#循环指派任务和参数
[pool.submit('任务函数名','被执行任务的名单') for use in userlist]
#关闭线程池
pool.shutdown()#默认为True
'''


class MonkeyLearn():
    loginurl = 'https://www.lmonkey.com/login'
    orderurl = 'https://www.lmonkey.com/my/order'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    req = None
    token = ''

    def __init__(self):
        self.req = requests.session()
        if self.gettoken():
            if self.postlogin():
                self.getorder()

    def gettoken(self):
        res = self.req.get(url=self.loginurl,headers=self.headers)
        if res.status_code ==200:
            print('get登录页面请求成功')
            html = etree.HTML(res.text)
            self.token = html.xpath('//input[@name="_token"]/@value')
            print('token请求成功')
            return True
        else:
            print('请求失败')

    def postlogin(self):
        uname = input('手机号：')
        passw = input('密码：')
        data = {
            '_token': self.token,
            'username': uname,
            'password': passw
        }
        res = self.req.post(url=self.loginurl,headers = self.headers,data=data)
        if res.status_code == 200 or res.status_code == 302:
            print('登录成功')
            return True

    def getorder(self):
        res = self.req.get(url=self.orderurl,headers = self.headers)
        if res.status_code==200:
            html = etree.HTML(res.text)
            r = html.xpath('//div[@class="avatar-content"]//small/text()')
            ordername=[''.join(r[i].split('：')[0]).strip()+str(i+1) for i in range(len(r))]
            orderID = [''.join(r[i].split('：')[1]).strip() for i in range(len(r))]
            print(list(zip(ordername,orderID)))

class YuanZhu():
    url = 'https://www.lmonkey.com/essence'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    data = ''
    def __init__(self):
        res = requests.get(url=self.url,headers = self.headers)
        if res.status_code ==200:
            with open('./HtmlCode.html','w') as f:
                f.write(res.text)
            if self.parse():
                self.savedata()


    def parse(self):
        html = etree.parse('./HtmlCode.html',etree.HTMLParser())
        print(html)
        author = html.xpath('//div[contains(@class,"col-md-9")]//div[contains(@class,"list-group")]//strong/a/text()')
        title = html.xpath('//div[contains(@class,"col-md-9")]//div[contains(@class,"list-group")]//div[contains(@class,"topic_title")]/text()')
        paperurl = html.xpath('//div[contains(@class,"col-md-9")]//div[contains(@class,"list-group")]//div[contains(@class,"flex-fill")]/a/@href')

        data = []
        for i in range(len(author)):
            res = {'author':author[i],'title':title[i],'paperurl':paperurl[i]}
            data.append(res)
        self.data = data
        return True

    def savedata(self):
        with open('./yuanzhu.json','w') as f:
            json.dump(self.data,f)

class beatiful_soup():
    url = 'https://www.lmonkey.com/t'

    data = []
    html = None

    def __init__(self):
        res = requests.get(url=self.url,headers = self.headers)
        if res.status_code ==200:
            # with open('./yuanquan.html','w') as f:
            #     f.write(res.text)
            self.html = res.text
            if self.parsedata():
                self.savedata()

    def parsedata(self):
        soup = BeautifulSoup(self.html, 'lxml')
        try:
            allpaper = soup.find_all('div', class_='list-group-item list-group-item-action p-06')#先爬一部分html码出来
            data = []
            for i in allpaper:
                r = i.find('div',class_='topic_title')#根据tag规则匹配下面的标签
                if r:
                    dict = {
                        'title': r.text.split('\n')[0],
                        'author':i.strong.a.text,#是
                        'url':i.a['href'],#属性要记得加[]
                        'time':i.span['title']
                    }

                    self.data.append(dict)
            return True
        except:
            return False

    def savedata(self):
        frame = pd.DataFrame(self.data)
        frame.to_csv('./yuanquan.csv')

class RegularExpressions():
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    url = 'https://www.lmonkey.com/ask'
    r_html = None
    DataDict=None

    def __init__(self):
        r = requests.get(url=self.url,headers=self.headers)
        self.r_html=r.text
        # if r.status_code == 200:
        #     with open('./yuanlairuci.html','w') as f:
        #         f.write(r.text)
        if self.parsedata():
            self.savedata()

    def parsedata(self):
        try:
            reg_title = '<div class="topic_title mb-0 lh-180 ml-n2">(.*?)<small'
            title = re.findall(reg_title,self.r_html)
            reg_author = '<strong>(.*?)</strong>'
            author = re.findall(reg_author,self.r_html)
            reg_url = '<a href="https://www.lmonkey.com/ask/\d+" target="_blank">'
            url = re.findall(reg_url,self.r_html)
            reg_date = '<span data-toggle="tooltip" data-placement="top" title="(.*?)">'
            date = re.findall(reg_date,self.r_html)
            data = list(zip(title,author,date,url))
            self.DataDict = [{'title':i[0],'author':i[1],'date':i[2],'url':i[3]} for i in data]
            return True
        except:
            return False

    def savedata(self):
        frame = pd.DataFrame(self.DataDict)
        frame.to_csv('./yuanlairuci.csv')

class getIP():
    url = 'https://www.xicidaili.com/nn/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    html = None
    data = None
    def __init__(self):
        self.res = requests.get(url=self.url,headers = self.headers)
        if self.res.status_code == 200:
            self.resopne = self.res.content.decode('utf-8')
            self.html = etree.HTML(self.resopne)
            if self.parse():
                self.savedata()

    def parse(self):
        try:
            ips = self.html.xpath('//table[@id="ip_list"]//tr//td[2]/text()')
            ports = self.html.xpath('//table[@id="ip_list"]//tr//td[3]/text()')
            self.data = [{'IP':ips[i],'PPRTS':ports[i]} for i in range(len(ips))]
            return True
        except:
            return False


    def savedata(self):
        print('saving data...')
        frame = pd.DataFrame(self.data)
        frame.to_csv('./ip.csv')

class GetIps():
    #发起请求
    def getpage(self,url):
        print('getting web htmlcode...')
        url = url
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        res = requests.get(url = url,headers = headers)
        if res.status_code == 200:
            response = res.content.decode('utf-8')
            return response
        else:
            return False

    #解析网页获得数据
    def parsedata(self,html):
        print('parsing data...')
        try:
            html = etree.HTML(html)
            ips = html.xpath('//table[@id="ip_list"]//tr//td[2]/text()')
            ports = html.xpath('//table[@id="ip_list"]//tr//td[3]/text()')
            data = [{'IP': ips[i], 'PORTS': ports[i]} for i in range(len(ips))]
            return data
        except:
            return False

    #测试IP是否能用
    def testIP(self,ip):
        url = 'http://httpbin.org/get'
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        proxies = {
            'http':f'{ip["IP"]}:{ip["PORTS"]}',
            'https':f'{ip["IP"]}:{ip["PORTS"]}'
        }
        try:
            res = requests.get(url=url,headers = headers,proxies = proxies,timeout = 3)
            if res.status_code == 200:
                print('测试IP成功')
                return True
            else:
                return False
        except:
            return False

    #保存数据
    def savedata(self,FinalIP):
        print('saving data')
        frame = pd.DataFrame(FinalIP)
        frame.to_csv('./finalIP.csv',mode='a')

    #主程序
    def main(self,num):
        #拼接url
        url = f'https://www.xicidaili.com/nn/{num}'
        #发起请求
        html = self.getpage(url)
        if html:
            #解析网页，获取IPlist
            iplist = self.parsedata(html)
            FinalIp = []
            for ip in iplist:
                #测试ip是否能用
                okIP = self.testIP(ip)
                if okIP:
                    FinalIp.append(ip)
            #保存数据
            data = self.savedata(FinalIp)

class baiduImage():
    # 发起请求
    def getdata(self,kw, num):
        url = 'http://image.baidu.com/search/acjson'
        params = []
        for i in range(30, 30 * num + 30, 30):
            params.append({
                'tn': 'resultjson_com',
                'ipn': 'rj',
                'ct': '201326592',
                'is': ' ',
                'fp': 'result',
                'queryWord': kw,
                'cl': '2',
                'lm': '-1',
                'ie': 'utf-8',
                'oe': 'utf-8',
                'adpicid': ' ',
                'st': ' ',
                'z': ' ',
                'ic': ' ',
                'hd': ' ',
                'latest': ' ',
                'copyright': ' ',
                'word': kw,
                's': ' ',
                'se': ' ',
                'tab': ' ',
                'width': ' ',
                'height': ' ',
                'face': ' ',
                'istype': ' ',
                'qc': ' ',
                'nc': ' 1',
                'fr': ' ',
                'expermode': ' ',
                'force': ' ',
                'cg': ' star',
                'pn': i,
                'rn': '30',
                'gsm': ' 3c',
                '1584159963318': ' ',
            })
        # 获取图片的url
        urllist = []
        for par in params:
            res = requests.get(url, params=par).json()['data']
            urllist.append(res)
        return urllist

    def downloadimage(self,datalist, dir):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        # 检测文件是否存在
        if not os.path.exists(dir):
            os.mkdir(dir)
        x = 0
        for data in datalist:
            for i in data:
                if i.get('thumbURL') != None:
                    res_download = requests.get(i.get('thumbURL'), headers=headers)
                    print(res_download.status_code)
                    x += 1
                    open(f'{dir}/{x}.jpg', 'wb').write(res_download.content)

class doubancomment():
    # 初始化
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
    # 发起请求
    def getpages(self,url):
        try:
            res = requests.get(url = url,headers=self.headers)
            if res.status_code == 200:
                print('请求成功。。。')
                html = res.text
                return html
            else:
                return None
        except:
            return None

    def getID(self,url):
        html = self.getpages(url)
        reg = '<h2><a href="https://movie.douban.com/review/(.*?)/">'
        id = re.findall(reg,html)
        return id

    def commentdata(self,id):
        print('parsing data...')
        try:
            sub_url = f'https://movie.douban.com/j/review/{id}/full'
            res = self.getpages(sub_url)
            content_pattern = re.compile('data-original(.*?)main-author', re.S) #re.S 它表示“.” 的作用扩展到整个字符串，包括“\n”
            content = re.findall(content_pattern, res)
            text_pattern = re.compile('[\u4e00-\u9fa5|，、“”‘’：！~@#￥《》『』【】*（）——+。；？]+', re.S)
            text = re.findall(text_pattern, content[0])
            text = ''.join(text)
            return text
        except:
            print('获取影评失败。。。')
            return None

    def otherdata(self,url):
        html = self.getpages(url)
        res_html = etree.HTML(html)
        items = res_html.xpath('//div[@class = "review-list chart "]')
        for item in items:
            data = {
                '作者':item.xpath('//header[contains(@class,"main-hd")]//a[contains(@class,"name")]/text()'),
                '推荐指数':item.xpath('//header[contains(@class,"main-hd")]//span/@title'),
                '题目':item.xpath('//div[contains(@class,"main-bd")]/h2/a/text()'),
            }
        print(data)
        return data

    def savedata(self,data):
        print('saving data...')
        frame = pd.DataFrame(data)
        frame.to_csv('./douban.csv',mode='a')

    # 主程序
    def main(self,url):
        yingping=[]
        id = self.getID(url)
        for i in range(len(id)):
            yingping.append(self.commentdata(id[i]))
        data = self.otherdata(url)
        data['影评'] = yingping
        self.savedata(data)

if __name__ == '__main__':
    # MonkeyLearn()
    # YuanZhu()
    # beatiful_soup()
    # RegularExpressions()
    # getIP()
    # for num in range(1,5):
    #     print(f'正在提取第{num}页IP')
    #     GetIps().main(num)
    #     time.sleep(5)

    # # 爬取百度图片
    # #主程序
    # f = baiduImage()
    # keyword = input('请输入您想要寻找的图片:')
    # #调用函数，进行数据爬取，可以指定关键字和下载页数
    # datalist = f.getdata(keyword,2)
    # #下载并保存数据
    # f.downloadimage(datalist,'./baidu')

    # 豆瓣影评
    for i in range(5):
        url = f'https://movie.douban.com/review/best/?start={i*20}'
        f = doubancomment().main(url)
        time.sleep(3)





