import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import PageItem,DoiItem

def get_urls():
    url_list = []
    # today = datetime.datetime.today()
    # year = today.year
    # month = today.month
    # day = today.day
    # # end_day_in_mouth = today.replace(day=1)
    # last_month_time = today - datetime.timedelta(days=7)
    # last_month = last_month_time.month
    # last_year = last_month_time.year
    # last_day = last_month_time.day
    # # for key in ['single+cell+RNA+sequencing','scRNA','Single+cell+transcriptome']:
    # # 20221212更新
    # for key in ['single+cell+rna','single+cell+transcriptome','scRNA','snRNA','single+nuclei+RNA','single+nuclei+transcriptome','Spatial+transcriptome']:
    #     url = f'https://pubmed.ncbi.nlm.nih.gov/?term={key}&filter=dates.{last_year}%2F{last_month}%2F{last_day}-{year}%2F{month}%2F{day}&sort=date&size=100&page=1'
    #     # url = f'https://pubmed.ncbi.nlm.nih.gov/?term={key}%20AND%20((%22{last_year}%2F{last_month}%2F{last_day}%22%5BDate%20-%20Publication%5D%20%3A%20%22{year}%2F{month}%2F{day}%22%5BDate%20-%20Publication%5D))&size=100&page=1'
    #     # url = f'https://pubmed.ncbi.nlm.nih.gov/?term=%28{key}%29+AND+%28%28%22{year}%2F{month}%2F{day}%22%5BDate+-+Publication%5D+%3A+%22{last_year}%2F{last_month}%2F{last_day}%22%5BDate+-+Publication%5D%29%29&size=100&page=1'
    #     url_list.append(url)
    # print(url_list)
    url_list= ['https://pubmed.ncbi.nlm.nih.gov/?term=%28china%29+AND+%28single+cell%29&sort=date&filter=simsearch1.fha']
    return url_list

class DocPaperNCBIEmailSpider(scrapy.Spider):
    name = 'docpaperncbiemail'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaper', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        print(self.start_urls)
        # self.start_urls = [
        #     # 
        #     # 'https://pubmed.ncbi.nlm.nih.gov/?term=single+cell+RNA+sequencing&size=100&page=1', # website:nature,keyword:single cell RNA sequencing
        #     # 'https://pubmed.ncbi.nlm.nih.gov/?term=scRNA&size=100&page=1',   # website:nature,keyword:scRNA
        #     # 'https://pubmed.ncbi.nlm.nih.gov/?term=Single+cell+transcriptome&size=100&page=1',  # website:nature,keyword:Single cell transcriptome
        #     #按照date排序抓取
        #     'https://pubmed.ncbi.nlm.nih.gov/?term=single+cell+RNA+sequencing&sort=date&size=100',
        #     'https://pubmed.ncbi.nlm.nih.gov/?term=scRNA&sort=date&size=100',
        #     'https://pubmed.ncbi.nlm.nih.gov/?term=Single+cell+transcriptome&sort=date&size=100',
        # ]

    def parse(self, response):
        item = PageItem()
        url = response.url
        keyword = re.match('.*?term=\((.*?)\)',response.url).group(1)
        pages_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "of-total-pages", " " ))]/text()').getall()
        if len(pages_content) > 0:
            pages = pages_content[-1].split(' ')[-1]
            pages = int(pages)
            print(f'NCBI  {keyword}  Pages count: {pages}')
        else:
            pages = 1 + 1 
        for singlepage in range(1,pages):
        # for singlepage in range(1,pages_test): #ncbi 从page = 1开始编号 
            page_urls = url.replace('&page=1',f'&page={singlepage}')
            item['origin_url'] = url
            item['url'] = page_urls
            request = scrapy.Request(item['url'], callback=self.paper_parse,dont_filter=True)
            request.meta['item'] = item
            yield request
        
    def paper_parse(self, response):
        item = response.meta['item']
        paperlinks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "docsum-title", " " ))]//@href').getall()
        # print(paperlinks)
        for paperlink in paperlinks:
            item['url'] = f'https://pubmed.ncbi.nlm.nih.gov{paperlink}'
            item['status'] = 'score_email'
            item['type'] = 'NCBI'
            item['date'] = datetime.datetime.now()
            item['page'] = re.match( r'.*&size=.*&page=(.*)', response.url).group(1)
            item['related_url'] = response.url
            yield item

