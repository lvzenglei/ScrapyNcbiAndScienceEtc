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
from .items import *
print('load piplines mongo')
class MyspiderPipeline:
    def process_item(self, item, spider):
        return item

class DocpaperPipeline(object):

    pageitem_collection_name = 'PageItem' # 这里的地方是每页对应url连接的数据库表的名字
    doiitem_collection_name = 'DoiItem' # 这里的地方是doi相关信息连接的数据库表的名字
    firstitem_collection_name = 'FirstPageItem' # 这里的地方是doi相关信息连接的数据库表的名字
    GeneVarientsItems_collection_name = 'GeneVarientsItems' # 这里的地方是doi相关信息连接的数据库表的名字    
    CATEGORY_VARIANTSItems_collection_name = 'CategoryVarientsItems' # 这里的地方是doi相关信息连接的数据库表的名字
    MOLECULAR_PROFILESItems_collection_name = 'MolecularProfilesItems' # 这里的地方是doi相关信息连接的数据库表的名字
    GENE_LEVEL_EVIDENCEItems_collection_name = 'GeneLevelEvidenceItems' # 这里的地方是doi相关信息连接的数据库表的名字
    CLINICAL_TRIALSItems_collection_name = 'ClinicalTrialsItems' # 这里的地方是doi相关信息连接的数据库表的名字
    OncoKb_BiologicalItems_collection_name = 'OncoKb_BiologicalItems' # 这里的地方是doi相关信息连接的数据库表的名字

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
            # print('save on process PageItem')
            # self.db[self.pageitem_collection_name].insert_one(ItemAdapter(item).asdict()) # 纯插入
            # print(ItemAdapter(item).asdict())
            self.db[self.pageitem_collection_name].update_one({'url':item['url']},{'$setOnInsert':ItemAdapter(item).asdict()},upsert=True) # 更新或插入
        elif isinstance(item, DoiItem):
            # print('save on process DoiItem')
            # self.db[self.doiitem_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.doiitem_collection_name].update_one({'url':item['url']},{'$set':ItemAdapter(item).asdict()},upsert=True)  # 更新或插入
            self.db[self.pageitem_collection_name].update_one({'url':item['url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        elif isinstance(item, FirstPageItem):
            print('save on process FirstPageItem')
            # self.db[self.firstitem_collection_name].insert_one(ItemAdapter(item).asdict())
            # print('save successfully')
            self.db[self.firstitem_collection_name].update_one({'type_url':item['type_url']},{'$setOnInsert':ItemAdapter(item).asdict()},upsert=True) # 更新或插入
        elif isinstance(item, GeneVarientsItems):
            print('save on process GeneVarientsItems')
            self.db[self.GeneVarientsItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        
        elif isinstance(item, CATEGORY_VARIANTSItems):
            print('save on process CATEGORY_VARIANTSItems')
            self.db[self.CATEGORY_VARIANTSItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        
        elif isinstance(item, MOLECULAR_PROFILESItems):
            print('save on process MOLECULAR_PROFILESItems')
            self.db[self.MOLECULAR_PROFILESItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        
        elif isinstance(item, GENE_LEVEL_EVIDENCEItems):
            print('save on process GENE_LEVEL_EVIDENCEItems')
            self.db[self.GENE_LEVEL_EVIDENCEItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        
        elif isinstance(item, CLINICAL_TRIALSItems):
            print('save on process CLINICAL_TRIALSItems')
            self.db[self.CLINICAL_TRIALSItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取

        elif isinstance(item, OncoKb_BiologicalItems):
            print('save on process OncoKb_BiologicalItems')
            self.db[self.OncoKb_BiologicalItems_collection_name].insert_one(ItemAdapter(item).asdict())  # 纯插入
            self.db[self.firstitem_collection_name].update_one({'type_url':item['origin_url'],'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
        return item
