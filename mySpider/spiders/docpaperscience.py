import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import PageItem,DoiItem

def get_urls():
    url_list = []
    today = datetime.datetime.today()
    str_today = today.strftime('%Y%m%d')
    last_month_time = today - datetime.timedelta(days=7)
    last_day = last_month_time.strftime('%Y%m%d')
    # for key in ['single+cell+RNA+sequencing','scRNA','Single+cell+transcriptome']:
    for key in ['single+cell+rna','single+cell+transcriptome','scRNA','snRNA','single+nuclei+RNA','single+nuclei+transcriptome','Spatial+transcriptome']:
        url = f'https://www.science.org/action/doSearch?field1=AllField&text1={key}&Ppub=&Ppub={last_day}-{str_today}&startPage=0&pageSize=100'
        url_list.append(url)
    print(url_list)
    return url_list

class DocPaperScienceSpider(scrapy.Spider):
    name = 'docpaperscience'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaper', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        # self.start_urls = [
        #     # Earliest  => recency
        #     'https://www.science.org/action/doSearch?AllField=single+cell+RNA+sequencing&startPage=0&pageSize=100&sortBy=Earliest', # website:nature,keyword:single cell RNA sequencing
        #     'https://www.science.org/action/doSearch?AllField=scRNA&startPage=0&pageSize=100&sortBy=Earliest',   # website:nature,keyword:scRNA
        #     'https://www.science.org/action/doSearch?AllField=Single+cell+transcriptome&startPage=0&pageSize=100&sortBy=Earliest',  # website:nature,keyword:Single cell transcriptome
        # ]

    def parse(self, response):
        item = PageItem()
        url = response.url
        keyword = re.match('.*AllField&text1=(.*?)&Ppub=&Ppub.*',response.url).group(1)
        pages = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "page-link", " " ))]/text()').getall()
        if len(pages) > 0:
            pages = list(filter(None,[singlepage.strip() for singlepage in pages]))[-1]
            pages = int(pages)
            print(f'Sciences  {keyword}  Pages count: {pages}')
            if pages >= 19: # science 按照相关性排行只取前2000个
                pages = 19
        else:
            pages = 1 #只有一页
        for singlepage in range(0,pages): 
            page_urls = url.replace('startPage=0&',f'startPage={singlepage}&')
            # page_urls = f'https://www.science.org/action/doSearch?AllField={keyword}&startPage={singlepage}&pageSize=100&sortBy=Earliest'
            item['origin_url'] = url
            item['url'] = page_urls
            request = scrapy.Request(item['url'], callback=self.paper_parse,dont_filter=True)
            request.meta['item'] = item
            yield request
        
    def paper_parse(self, response):
        item = response.meta['item']
        paperlinks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "animation-underline", " " ))]//@href').getall()
        # print(paperlinks)
        for paperlink in paperlinks:
            item['url'] = f'https://www.science.org{paperlink}'
            item['status'] = 'score'
            item['type'] = 'Science'
            item['date'] = datetime.datetime.now()
            item['page'] = re.match( r'.*&startPage=(.*)&pageSize=.*', response.url).group(1)
            item['related_url'] = response.url
            yield item

