import scrapy
import pandas as pd
import numpy as np
import datetime
import os
import shutil
import pymongo
from ..items import OncoKb_Biological_ExportItems
from ..settings import MONGO_URI,MONGO_DATABASE,ONCOKB_FINAL_DIR,ONCOKB_SHEET_NAME

class OncoKbScrapyThirdStepExportSpider(scrapy.Spider):
    name = 'oncokbScrapyThirdStepExport'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org','ckb.jax.org','oncokb.org']
    
    def __init__(self, name='oncokbScrapyThirdStepExport', **kwargs):
        super().__init__(name, **kwargs)
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DATABASE]
        self.start_urls = ['https://www.baidu.com/']
        self.collection = db['OncoKb_BiologicalItems']
        current_date = datetime.datetime.now()
        self.formatted_date = current_date.strftime('%Y%m%d')

    def parse(self, response):

        item = OncoKb_Biological_ExportItems()
        # 查询字段并挑选字段
        query = {}  # 可以根据需要添加查询条件
        projection = {'gene': 1, 'Alteration': 1, 'Oncogenic': 1, 'Mutation_Effect': 1, 'Refseq': 1}  # 挑选需要的字段，1表示要包含在结果中，0表示不包含
        # 查询数据
        cursor = self.collection.find(query, projection)
        try:
            # 将查询结果转换为 DataFrame
            df = pd.DataFrame(list(cursor)).drop('_id',axis=1)
            
            # 将数据写入 Excel 文件
            output_file = f'./Scrapy_Out_database/OncoKB_{self.formatted_date}.xlsx'
            self.logger.info(df.head())
            self.logger.info(f"output_file: {output_file}")
            df.to_excel(output_file, index=False, sheet_name=ONCOKB_SHEET_NAME)

            os.makedirs(ONCOKB_FINAL_DIR,exist_ok=True)
            shutil.copy(output_file,ONCOKB_FINAL_DIR)
            self.logger.info(f'Data exported to {ONCOKB_FINAL_DIR}/{os.path.basename(output_file)}')
        except Exception as e:
            self.logger.info(f'Data exported Error: {e}')

        item['date'] = datetime.datetime.now()
        item['batch'] = self.formatted_date
        item['status'] = 'success'
        item['action'] = 'OncoKb_Export'

        return item


