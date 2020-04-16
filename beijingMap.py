from pyecharts import Map,Geo
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import webbrowser
from math import *


'''
district = ['丰台区','海淀区','朝阳区','昌平区','大兴区','西城区','通州区','石景山区','顺义区','东城区','房山区','密云县','怀柔区','门头沟区']
num = [72,50,184,33,32,46,35,10,19,38,11,5,3,5]

map = Map("北京市生鲜店分布图",'',width=1000,height=1000,title_pos='center')
map.add("",district,num,visual_range=[0,51],maptype='北京',is_visualmap=True,visual_text_color='#003',is_label_show=True,
        label_text_size=18,formatter= ["name", "value"])
map.show_config()
map.render(path='./beijing.html')
'''
# # 热力图
# geo = Geo("北京市生鲜店分布图",title_color="#fff", title_pos="center", width=1200, height=600,background_color='#404a59')
# # type="effectScatter", is_random=True, effect_scale=5  使点具有发散性
# geo.add("", district, num, maptype='北京',type="heatmap",is_random=True, visual_text_color="#fff",effect_scale=15,
#         visual_range=[1,50], symbol_size=15, is_visualmap=True, is_roam=False)
# geo.render(path='./beijing1.html')

data = pd.read_csv('./shopDetail.csv')
List=[]
for line in data['coordinate'].values:
    lng,lat = line.split('：')[1].split(',')
    List.append([float(lng),float(lat),1])
    print('{"lng":'+lng+',"lat":'+lat+',"count":1},')
# print(List)
# map_osm = folium.Map(location=[35, 110], zoom_start=2)
# HeatMap(List).add_to(map_osm)
# file_path = './beijing2.html'
# map_osm.save(file_path)  # 保存本地
# # webbrowser.open(file_path)  # 在本地浏览器打开



