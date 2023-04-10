import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import PageItem,DoiItem

def get_urls():
    url_list = []
    today = datetime.datetime.today()
    # year = today.year
    # month = today.month
    end_day_in_mouth = today.replace(day=1)
    last_month_time = end_day_in_mouth - datetime.timedelta(days=1)
    # last_month = last_month_time.month
    # last_year = last_month_time.year
    str_today = today.strftime('%Y%m%d')
    last_month_time = today - datetime.timedelta(days=7)
    last_day = last_month_time.strftime('%Y%m%d')
    # for key in ['single+cell','rna','sequencing']:
    # 20221212 更新关键词
    for key in ['single+cell+rna','single+cell+transcriptome','scRNA','snRNA','single+nuclei+RNA','single+nuclei+transcriptome','Spatial+transcriptome']:
        url = f'https://www.cell.com/action/doSearch?text1={key}&field1=AllField&startPage=0&pageSize=100&Ppub=%5B{last_day}%20TO%20{str_today}%5D'
        url_list.append(url)
    print(url_list)
    return url_list

class DocPaperCellSpider(scrapy.Spider):
    name = 'docpapercell'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaper', doi_path='',doi_list='', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        # self.start_urls = [
        #     # Earliest => relevancy
        #     'https://www.cell.com/action/doSearch?text1=single+cell&sortBy=Earliest&startPage=0&pageSize=100', # website:nature,keyword:single cell RNA sequencing
        #     'https://www.cell.com/action/doSearch?text1=rna&sortBy=Earliest&startPage=0&pageSize=100',   # website:nature,keyword:scRNA
        #     'https://www.cell.com/action/doSearch?text1=sequencing&sortBy=Earliest&startPage=0&pageSize=100',  # website:nature,keyword:Single cell transcriptome
        # ]

    def parse(self, response):
        item = PageItem()
        url = response.url
        keyword = re.match('.*text1=(.*?)&.*',response.url).group(1)
        pages = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "current-page", " " ))]/text()').getall()
        if len(pages) > 0:
            pages = int(pages[-1].split(' ')[-1])
            print(f'CELL  {keyword}  Pages count: {pages}')
            if pages >= 20: #cell网站限制只能取前2000条记录，因此限制page=100的情况下，只显示20页
                pages = 20
        else:
            pages = 1
        for singlepage in range(0,pages):
        # for singlepage in range(0,pages_test): #cell 从startpage = 0开始编号 
            page_urls = f'https://www.cell.com/action/doSearch?text1={keyword}&sortBy=Earliest&startPage={singlepage}&pageSize=100'
            item['origin_url'] = url
            item['url'] = page_urls
            request = scrapy.Request(item['url'], callback=self.paper_parse,dont_filter=True)
            request.meta['item'] = item
            yield request
        
    def paper_parse(self, response):
        item = response.meta['item']
        paperlinks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta__title", " " ))]//a//@href').getall()
        # print(paperlinks)
        for paperlink in paperlinks:
            item['url'] = f'https://www.cell.com{paperlink}'
            item['status'] = 'score'
            item['type'] = 'CELL'
            item['date'] = datetime.datetime.now()
            item['page'] = re.match( r'.*&startPage=(.*?)&pageSize=100', response.url).group(1)
            item['related_url'] = response.url
            yield item

