import scrapy
import pandas as pd
import datetime
import re
import math

from ..items import PageItem,DoiItem

def get_urls():
    url_list = []
    # for key in ['single%20cell%20RNA%20sequencing','scRNA','Single%20cell%20transcriptome']:
    for key in ['single%cell%rna','single%cell%transcriptome','scRNA','snRNA','single%nuclei%RNA','single%nuclei%transcriptome','Spatial%transcriptome']:
        url = f'https://www.nature.com/search?q={key}&date_range=last_7_days&order=relevance&page=1'
        url_list.append(url)
    return url_list

class DocPaperNatureSpider(scrapy.Spider):
    name = 'docpapernature'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaper', doi_path='',doi_list='', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        print(self.start_urls)
        # self.start_urls = [
        #     # date_desc =>  relevance
        #     'https://www.nature.com/search?q=single%20cell%20RNA%20sequencing&order=date_desc&page=1', # website:nature,keyword:single cell RNA sequencing
        #     'https://www.nature.com/search?q=scRNA&order=date_desc&page=1',   # website:nature,keyword:scRNA
        #     'https://www.nature.com/search?q=Single%20cell%20transcriptome&order=date_desc&page=1',  # website:nature,keyword:Single cell transcriptome
        # ]

    def parse(self, response):
        item = PageItem()
        url = response.url
        if response.status == 200:
            keyword = re.match('.*q=(.*?)&.*',response.url).group(1)
            pages = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-pagination__link", " " ))]/text()').getall()
            print(pages)
            if len(pages) > 0:
                pages = list(filter(None,[singlepage.strip() for singlepage in pages]))[-1]
                pages = int(pages) +1
                print(f'Nature {keyword} Pages count: {pages}')
                if pages >= 20: # nature限制每次只能提取前1000个搜索记录(默认每页50个，因此是20页)
                    pages = 20
            else:
                pages = 1
            for singlepage in range(1,pages+1): # nature 页面从1开始

                page_urls = url.replace('&page=1',f'&page={singlepage}')
                item['origin_url'] = url
                item['url'] = page_urls
                request = scrapy.Request(item['url'], callback=self.paper_parse,dont_filter=True)
                request.meta['item'] = item
                yield request
        else:
            print('请求超时')
        
    def paper_parse(self, response):
        item = response.meta['item']
        paperlinks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "u-link-inherit", " " ))]//@href').getall()
        # print(paperlinks)
        for paperlink in paperlinks:
            item['url'] = f'https://www.nature.com{paperlink}'
            item['status'] = 'score'
            item['type'] = 'Nature'
            item['date'] = datetime.datetime.now()
            item['page'] = re.match( r'.*&page=(.*?).*', response.url).group(1)
            item['related_url'] = response.url
            yield item

