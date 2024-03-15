import scrapy
import pandas as pd
import numpy as np
import datetime
import re
import pymongo
from ..items import OncoKb_BiologicalItems
from ..settings import MONGO_URI,MONGO_DATABASE


def get_oncokb_biological(response, gene, Refseq):
    table_elements = response.xpath('//div[@class="rt-tbody"]//div[contains(@class, "-odd") or contains(@class, "-even")]')
    biological_list = []
    for table_element in table_elements:
        cells = table_element.xpath('.//div[@class="rt-td"]')
        row_data = [cell.xpath('string()').get() for cell in cells]
        biological_list.append(row_data)
    df = pd.DataFrame(biological_list)
    if not df.empty:
        df.columns = ["Alteration","Oncogenic","Mutation_Effect","Description"]
        df = df.drop(["Description"],axis=1)
        df['gene'] = gene
        df['Refseq'] = Refseq
        df['origin_url'] = response.url
        df['type'] = 'Oncokb_Biological'
        df['date'] = datetime.datetime.now()
        df['status'] = 'suceess'
    return df.to_dict(orient='index')

class OncoKBScrapySecondStepSpider(scrapy.Spider):
    name = 'oncokbScrapySecondStep'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org','ckb.jax.org','oncokb.org']
    
    def __init__(self, name='oncokbScrapySecondStep', **kwargs):
        super().__init__(name, **kwargs)
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DATABASE]
        all_urls = []
        # all_urls = db['PageItem'].find({'status':'score','type':'Circulation'},{'url':1})
        # all_urls = db['FirstPageItem'].find({'status':'score'},{'type_url':1})
        all_score = db['FirstPageItem'].find({'status':'score','type':'Biological'},{'type_url':1, 'gene':1, 'refseq_id':1}).sort('_id', -1).limit(50)
        # all_score = db['FirstPageItem'].find({'status':'score','type':'Biological'},{'type_url':1, 'gene':1, 'refseq_id':1}).sort('_id', -1).limit(2)
        for single_score in all_score:
            all_urls.append(single_score['type_url'])
        self.start_urls = all_urls
        self.db = db
        self.firstitem_collection_name = 'FirstPageItem'


    def parse(self, response):

        if response.status == 200:
            url = response.url
            return_item = OncoKb_BiologicalItems()
            gene = re.match(r'.*gene/(.*?)#tab=Biological.*',url).group(1)
            onco_score = self.db['FirstPageItem'].find({'gene':gene,'type':'Biological'},{'refseq_id':1}).sort('_id', -1).limit(2)
            Refseq = onco_score[0]['refseq_id']
            items = get_oncokb_biological(response, gene, Refseq)
            if not items:
                self.db[self.firstitem_collection_name].update_one({'type_url':url,'status':'score'},{'$set':{'status':'success'}}) #将关联url设置为爬取成功，后续就不再爬取
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item
        else:
            self.logger.warning(f"Failed to fetch {response.url}. Status code: {response.status}. Maybe all pages had been scrapyd")

