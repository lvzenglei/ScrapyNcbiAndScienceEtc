# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import os
import pymongo
from .items import PageItem,DoiItem
class MyspiderPipeline:
    def process_item(self, item, spider):
        return item

class DocpaperPipeline(object):

    pageitem_collection_name = 'PageItem' # 这里的地方是每页对应url连接的数据库表的名字
    doiitem_collection_name = 'DoiItem' # 这里的地方是doi相关信息连接的数据库表的名字

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),  # get中有两个参数，一个是 配置的MONGO_URL ，另一个是localhost
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items') # 这里的两个参数,第一个是数据库配置的.第二个是它的表的数据库的名字
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, PageItem):
            print('save on process PageItem')
            # self.db[self.pageitem_collection_name].insert_one(ItemAdapter(item).asdict()) # 纯插入
            # print(ItemAdapter(item).asdict())
            self.db[self.pageitem_collection_name].update_one({'url':item['url']},{'$setOnInsert':ItemAdapter(item).asdict()},upsert=True) # 更新或插入
        elif isinstance(item, DoiItem):
            print('save on process DoiItem')
            # self.db[self.doiitem_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.doiitem_collection_name].update_one({'url':item['url']},{'$set':ItemAdapter(item).asdict()},upsert=True)  # 更新或插入
            self.db[self.pageitem_collection_name].update_one({'url':item['url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        return item
    
    def get_item(self,begin_date,end_date):
        allitem = self.db[self.doiitem_collection_name].find({'uploaddate':{ '$gt': begin_date, '$lt': end_date }})
        return allitem

