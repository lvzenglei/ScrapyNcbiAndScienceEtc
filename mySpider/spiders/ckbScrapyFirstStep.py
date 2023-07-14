import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import FirstPageItem

class CKBScrapyFirstStepSpider(scrapy.Spider):
    name = 'ckbScrapyFirstStep'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org','ckb.jax.org']
    
    def __init__(self, name='ckbScrapyFirstStep', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = ['https://ckb.jax.org/gene/grid']

    def parse(self, response):
        item = FirstPageItem()
        url = response.url
        gene_contents = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "min-padding", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "btn-gene", " " ))]/text()').getall()
        href_contnets = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "min-padding", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "btn-gene", " " ))]/@href').getall()
        if len(gene_contents) == len(href_contnets):
            for i in  range(len(gene_contents)):
                gene =  gene_contents[i].strip(' ').strip('\n').strip(' ')
                href_url = f"https://ckb.jax.org{href_contnets[i]}"
                item['origin_url'] = url
                item['href_url'] = href_url
                item['gene'] = gene
                item['date'] = datetime.datetime.now()
                item['status'] = 'score'
                for gene_type in ['GENE_VARIANTS','CATEGORY_VARIANTS','MOLECULAR_PROFILES','GENE_LEVEL_EVIDENCE','CLINICAL_TRIALS']:
                    item['type'] = gene_type
                    item['type_url'] = f"{href_url}&tabType={gene_type}"
                    yield item

