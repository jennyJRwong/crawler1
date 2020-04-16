from lxml import etree
from pyecharts import Map
import requests
import json
import re

class covin:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }
        self.url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'

    def parsedata(self):
        res = requests.get(url=self.url,headers = self.headers)
        assert res.status_code == 200
        html = etree.HTML(res.content.decode())
        results = html.xpath('//*[@id="getAreaStat"]/text()')[0].split(']')[:-2]
        return results

    def getdata(self,results):
        dataList = []
        for result in results:
            if results.index(result) == 0:
                result=result.replace('try { window.getAreaStat = [','')

            dataDict={}
        #     # print(type(result.strip(',')+'}'))
        #     # data = json.loads(result.strip(',')+'}',strict=False)
            dataDict['provinceShortName'] = re.findall('"provinceShortName":"(.*?)"', result)[0]
            dataDict['currentConfirmedCount'] = int(re.findall('"currentConfirmedCount":(\d+),".*?"statisticsData"', result)[0])
            dataDict['confirmedCount'] = int(re.findall('"confirmedCount":(\d+),".*?"statisticsData"', result)[0])
            dataDict['curedCount'] = int(re.findall('"curedCount":(\d+),".*?"statisticsData"', result)[0])
            dataDict['deadCount'] = int(re.findall('"deadCount":(\d+),".*?"statisticsData"', result)[0])
            dataList.append(dataDict)
        return dataList

    def main(self):
        # 返回数据列表
        return self.getdata(self.parsedata())

if __name__ == '__main__':
    data = covin().main()
    provinceShortName = []
    currentConfirmedCount = []
    confirmedCount = []
    curedCount = []
    deadCount = []
    for i in data:
        provinceShortName.append(i['provinceShortName'])
        currentConfirmedCount.append(i['currentConfirmedCount'])
        confirmedCount.append(i['confirmedCount'])
        deadCount.append(i['deadCount'])
        curedCount.append(i['curedCount'])
    print(len(provinceShortName))
    print(len(confirmedCount))
    map = Map("中国疫情分布图",'',width=1980,height=1024,title_pos='center')
    map.add("",provinceShortName,confirmedCount,visual_range=[0,1000],maptype='china',is_visualmap=True,
            visual_text_color='#000',is_label_show=True)
    map.show_config()
    map.render(path='./中国疫情图.html')