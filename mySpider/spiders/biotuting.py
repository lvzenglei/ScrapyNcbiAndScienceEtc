import scrapy
import pandas as pd
import datetime
import re
import math
import requests

from ..items import PageItem,DoiItem

from lxml import etree
def get_urls():
    url_list = []
    # today = datetime.datetime.today()
    # year = today.year
    # month = today.month
    #end_day_in_mouth = today.replace(day=1)
    #last_month_time = end_day_in_mouth - datetime.timedelta(days=1)
    # last_month = last_month_time.month
    # last_year = last_month_time.year
    #str_today = today.strftime('%Y%m%d')
    #last_month_time = today - datetime.timedelta(days=7)
    #last_day = last_month_time.strftime('%Y%m%d')
    # for key in ['single+cell','rna','sequencing']:
    # 20221212 更新关键词
    for key in range(1,339):
        url = f'https://talk2data.bioturing.com/studies?species=human&page={key}'
        url_list.append(url)
    for key in range(1,15):
        url = f'https://talk2data.bioturing.com/studies?species=primate&page={key}'
        url_list.append(url)
    for key in range(1,81):
        url = f'https://talk2data.bioturing.com/studies?species=mouse&page={key}'
        url_list.append(url)
    return url_list
all_item = []
urls = get_urls()
for url in urls:
  res = requests.get(url)
  html = etree.HTML(res.text)
  title = html.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "search-genes-result-title", " " ))]//p/text()')
  abstract = html.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "custom-datasets-result-abstract", " " ))]/text()')
  ID  = html.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "search-genes-result-info-item", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "search-genes-result-info-item-content", " " ))]/text()')
  for i in range(len(title)):
    item = {}
    item['title'] = title[i].strip()
    item['abstract'] = abstract[i].strip()
    item['ID'] = ID[i].strip()
    item['url'] = url
    all_item.append(item)
df = pd.DataFrame(all_item)
df.to_csv('bioturing.csv',encoding='utf_8_sig')



