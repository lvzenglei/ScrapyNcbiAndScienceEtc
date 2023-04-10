import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import PageItem,DoiItem

def get_urls():
    url_list = []
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    end_day_in_mouth = today.replace(day=1)
    last_month_time = end_day_in_mouth - datetime.timedelta(days=1)
    last_month = last_month_time.month
    last_year = last_month_time.year
    # for key in ['single+cell+RNA+sequencing','scRNA','Single+cell+transcriptome']:
    # 20221212 更新
    for key in ['single+cell+rna','single+cell+transcriptome','scRNA','snRNA','single+nuclei+RNA','single+nuclei+transcriptome','Spatial+transcriptome']:
        url = f'https://www.ahajournals.org/action/doSearch?field1=AllField&text1={key}&Ppub=&AfterMonth={last_month}&AfterYear={last_year}&BeforeMonth={month}&BeforeYear={year}&size=100&startPage=0'
        url_list.append(url)
    print(url_list)
    return url_list

class DocPaperCirculationSpider(scrapy.Spider):
    name = 'docpapercirculation'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaper', doi_path='',doi_list='', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        # self.start_urls = [
        #     # relevancy => Earliest
        #     'https://www.ahajournals.org/action/doSearch?AllField=single+cell+RNA+sequencing&startPage=0&sortBy=Earliest', # website:nature,keyword:single cell RNA sequencing
        #     'https://www.ahajournals.org/action/doSearch?AllField=scRNA&startPage=0&sortBy=Earliest',   # website:nature,keyword:scRNA
        #     'https://www.ahajournals.org/action/doSearch?AllField=Single+cell+transcriptome&startPage=0&sortBy=Earliest',  # website:nature,keyword:Single cell transcriptome
        # ]

    def parse(self, response):
        item = PageItem()
        url = response.url
        keyword = re.match( r'.*?AllField&text1=(.*?)&Ppub=.*', response.url).group(1)
        result_count_list = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "result__count", " " ))]/text()').getall()
        result_count = result_count_list[-1]
        pages = math.ceil(int(result_count)/100)
        print(f'Circulation  {keyword}  Pages count: {pages}')
        for singlepage in range(0,pages):
            page_urls = url.replace('&page=0',f'&page={singlepage}')
            item['origin_url'] = url
            item['url'] = page_urls
            request = scrapy.Request(item['url'], callback=self.paper_parse,dont_filter=True)
            request.meta['item'] = item
            yield request
        
    def paper_parse(self, response):
        item = response.meta['item']
        paperlinks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta__title__margin", " " ))]//a/@href').getall()
        # print(paperlinks)
        for paperlink in paperlinks:
            item['url'] = f'https://www.ahajournals.org{paperlink}'
            item['status'] = 'score'
            item['type'] = 'Circulation'
            item['date'] = datetime.datetime.now()
            item['page'] = re.match( r'.*&startPage=(.*).*', response.url).group(1)
            item['related_url'] = response.url
            yield item

