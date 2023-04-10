from scrapy.cmdline import execute   #调用此函数可以执行scrapy的脚本
from scrapy.crawler import CrawlerProcess
from collections import defaultdict
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

import subprocess
import datetime
import pymongo
import requests
import json
import sys
import os


# class PrepareProxy():
#     def __init__(self, settings):
#         self.setting = get_project_settings()
#         self.mongo_uri = self.setting.get('mongo_uri')
#         self.mongo_db = self.setting.get('MONGO_DATABASE', 'items')
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#         self.pritem_collection_name = 'IPpoolItem'
#         self.KUAI_ORDERID = self.settings.get('KUAI_ORDERID')
#         self.KUAI_SIGNATURE = self.settings.get('KUAI_SIGNATURE')
#         self.default_num  = self.settings.get('KUAI_Default_Num')
#         auth = kdl.Auth(self.KUAI_ORDERID, self.KUAI_SIGNATURE)
#         self.proxyclient = kdl.Client(auth)
#     def prepareIpProxy(self):
#         allproxy_object = self.db[self.pritem_collection_name].find({'company':'KUAIPROXY','status':'useful'})
#         allproxy_object_count = allproxy_object.count()
#         setting_proxy = []
#         origin_proxy_list = []
#         useful_proxy = []
#         outtime_proxy = []
#         single_proxy_mongo_object = defaultdict()
#         proxy_mongo_objects = []
#         proxy_list = []
#         # 代理池中有值则获取所有proxy
#         if allproxy_object_count > 0:
#             for proxy_object in allproxy_object:
#                 origin_proxy_list.append(proxy_object.proxy)
#         # 若获取到proxy，对proxy判断是否可用
#         # useful_proxy 
#         # outtime_proxy -- 过期proxy数据库直接删掉
#         if origin_proxy_list:
#             valids = self.proxyclient.check_dps_valid(origin_proxy_list)
#             expire_second = self.proxyclient.get_dps_valid_time(origin_proxy_list)
#             for single_proxy in origin_proxy_list:
#                 if valids[single_proxy] and expire_second[single_proxy] > 30:
#                     useful_proxy.append(single_proxy)
#                 else:
#                     outtime_proxy.append(single_proxy)
#         if len(outtime_proxy) >0:
#             self.db[self.pritem_collection_name].deleteMany({'proxy':{"$in": outtime_proxy}})
#         #获取剩余IP数，若代理池中IP小于200，且还有剩余数，则补充剩余IP到代理池中
#         left_count = self.proxyclient.get_ip_balance(sign_type='hmacsha1')
#         if len(useful_proxy) < 500 and left_count > 0:
#             single_count = self.default_num
#             if left_count < single_count:
#                 single_count = left_count
#             url = 'http://dps.kdlapi.com/api/getdps'
#             param = {'orderid':self.KUAI_ORDERID,'signature':self.KUAI_SIGNATURE,'num':single_count,'format':'json'}
#             r  = requests.get(url,param)
#             proxy_info = json.loads(r.text)
#             if proxy_info.get('code') == 0:
#                 proxy_list = proxy_info.get('data').get('proxy_list')
#                 useful_proxy.extend(useful_proxy)
#                 for proxy in proxy_list:
#                     single_proxy_mongo_object['proxy'] = proxy
#                     single_proxy_mongo_object['add_time'] = datetime.datetime.now()
#                     single_proxy_mongo_object['status'] = 'useful'
#                     single_proxy_mongo_object['company'] = 'KUAIPROXY'
#                     proxy_mongo_objects.append(single_proxy_mongo_object)
#                     self.db[self.pageitem_collection_name].find({'company':'KUAIPROXY'})
#             if len(proxy_mongo_objects)>0:
#                 self.db[self.pageitem_collection_name].insertMany(proxy_mongo_objects)
#         self.setting['IPPOOL'] = useful_proxy
setting = get_project_settings()
crawler = CrawlerProcess(setting)
crawler.crawl('docpapernature')
crawler.crawl('docpapercell')
crawler.crawl('docpapercirculation')
crawler.crawl('docpaperncbi')
crawler.crawl('docpaperscience')
d = crawler.join()
d.addBoth(lambda _: reactor.stop())
reactor.run() # the script will block here until all crawling jobs are finished