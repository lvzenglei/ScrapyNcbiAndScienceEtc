import scrapy
import pandas as pd
import datetime
from io import StringIO

from ..items import FirstPageItem

class OncoKBScrapyFirstStepSpider(scrapy.Spider):
    name = 'oncokbScrapyFirstStep'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org','ckb.jax.org','oncokb.org']
    
    def __init__(self, name='oncokbScrapyFirstStep', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = ['https://www.oncokb.org/api/v1/utils/cancerGeneList.txt']

    def parse(self, response):
        item = FirstPageItem()
        url = response.url
        content = response.text
        df = pd.read_csv(StringIO(content), sep='\t')
        df = df.fillna('NA')
        df = df[['Hugo Symbol','GRCh37 RefSeq']]
        for index, row in  df.iterrows():
            gene = str(row['Hugo Symbol']).strip()
            refseq_id = str(row['GRCh37 RefSeq']).strip()
            item['origin_url'] = url
            item['href_url'] = url
            item['gene'] = gene
            item['date'] = datetime.datetime.now()
            item['status'] = 'score'
            item['type'] = 'Biological'
            item['type_url'] = f"https://www.oncokb.org/gene/{gene}#tab=Biological"
            item['refseq_id'] = refseq_id
            yield item

