import collections
from socket import TIPC_CRITICAL_IMPORTANCE
import scrapy
import pandas as pd
import datetime
import time
import re
import math

from ..items import PageItem,DoiItem
from ..settings import MONGO_URI,MONGO_DATABASE
from collections import defaultdict
import bs4
from bs4 import BeautifulSoup
import pymongo
import requests

def get_paper_ifactor(searchName):
    ifactor = 'NA'
    url = f"https://pubmed.pro/api/openjournal/searchPrecise?searchName={searchName}"
    response = requests.request("POST", url)
    if response.ok:
        content = response.json()
        if content['data']['object']:
            for object in content['data']['object']:
                if searchName == object.get('name'):
                    ifactor = object.get('ifactor')
    return ifactor

def get_urls():
    url_list = []
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    # all_urls = db['PageItem'].find({'status':'score','type':'Circulation'},{'url':1})
    all_urls = db['PageItem'].find({'status':'score'},{'url':1})
    # all_urls = db['DoiItem'].find({'publictime':None},{'url':1})
    # all_urls = db['PageItem'].find({'status':'score','type': {'$in' : ['NCBI','Nature'] }},{'url':1})
    # getdict = {'CELL':0,'NCBI':0,'Science':2,'Circulation':0,'Nature':0}
    # print(getdict.keys())
    # for key in getdict.keys():
    #     all_urls = db['PageItem'].find({'status':'score','type':key},{'url':1})
    #     for url_score in all_urls:
    #         if getdict[key] <= 1 :
    #             url_list.append(url_score.get('url'))
    #             getdict[key] += 1
    for url_score in all_urls:
        url_list.append(url_score.get('url'))
    print(len(url_list))
    return url_list
# 影响因子做后续处理
def get_science_keyword(response):
    item = DoiItem()
    item['url'] = response.url
    author_list = response.xpath('//*[@id="frontmatter"]/header/div/div[2]/span/span[1]/span[1]//text()').getall()
    DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "doi", " " ))]//a/text()').extract_first()
    abstract_info = response.xpath('//*[(@id = "abstract")]//div/text()').getall()
    item['Title']  = response.xpath('//h1/text()').extract_first()
    item['firstauthor'] = 'NA'
    deal_author_list = []
    if author_list:
        for key in author_list:
            key = re.sub('\s', ' ', key) #处理到字符串中的空格
            if key != ' ' and not key.startswith('https'):
                deal_author_list.append(key)
        item['firstauthor'] = ' '.join(deal_author_list)
    item['publictime'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "core-date-published", " " ))]//span/text()').extract_first()
    item['DOI'] = DOI_info.replace('DOI: ','')
    item['Abstract'] = ' '.join(abstract_info)
    item['paper_fullspare']  = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "core-self-citation", " " ))]//div[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//span/text()').extract_first()
    now = datetime.datetime.now()
    item['uploadtime'] = now
    item['uploaddate'] = now.strftime('%Y-%m-%d')
    item['Website'] = 'Science'
    item['ifactor'] = get_paper_ifactor(item['paper_fullspare'])
    return item

def get_ncbi_keyword(response):
    item = DoiItem()
    item['url'] = response.url
    DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "citation-doi", " " ))]/text()').extract_first().strip().strip('.')
    title_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "heading-title", " " ))]/text()').getall()
    Abstract_info = response.xpath('//*[(@id = "enc-abstract")]//p/text()').extract_first()
    if Abstract_info:
        Abstract_info = Abstract_info.strip()
    item['Title']  = ' '.join([x.strip().replace('\n        ','') for x in title_info]).strip()
    item['firstauthor'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "authors-list-item", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "full-name", " " ))]/text()').extract_first()
    item['publictime'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "cit", " " ))]/text()').extract_first().split(';')[0]
    item['DOI'] = DOI_info.replace('doi: ','')
    item['Abstract'] = Abstract_info
    now = datetime.datetime.now()
    item['uploadtime'] = now
    item['uploaddate'] = now.strftime('%Y-%m-%d')
    soup=BeautifulSoup(response.text,features="lxml")
    paper_fullspare_info = soup.find(name='button',attrs={"id":"full-view-journal-trigger"})
    item['paper_fullspare'] =  paper_fullspare_info.attrs['title']
    item['Website'] = 'NCBI'
    item['ifactor'] = get_paper_ifactor(item['paper_fullspare'])
    return item

def get_cell_keyword(response):
    item = DoiItem()
    item['url'] = response.url
    soup=BeautifulSoup(response.text,features="lxml")
    auther_info  = soup.find(name='a',attrs={"class":"loa__item__name article-header__info__ctrl loa__item__email"})
    deal_auther_info = 'NA'
    if auther_info:
        deal_auther_info = auther_info.contents[0]
    title_info =  soup.find(name='h1',attrs={"class":"article-header__title"})
    deal_title_info = []
    if len(title_info.contents) >= 1:
        for single_info in title_info.contents:
            if(isinstance(single_info,bs4.element.Tag)):
                deal_title_info.append(single_info.text)
            elif(isinstance(single_info,str)):
                deal_title_info.append(single_info)

    DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article-header__doi__value", " " ))]/text()').extract_first()
    deal_doi_info = 'NA'
    if DOI_info:
        deal_doi_info = DOI_info.replace('https://doi.org/','')
    deal_Abstract_info = 'NA'
    Abstract_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "section-paragraph", " " ))]/text()').getall()
    if Abstract_info:
        deal_Abstract_info = ' '.join([x.strip().replace('\n        ','') for x in Abstract_info]).strip()
    paper_fullspare_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "journal-logos", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//img').extract_first()
    if not paper_fullspare_info:
        paper_fullspare_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "journal-logos", " " ))]//img').extract_first()
    if paper_fullspare_info:
        deal_paper_fullspare_info = re.match('<img alt="(.*?)".*',paper_fullspare_info).group(1)
    else:
        deal_paper_fullspare_info = 'NA'
    publictime_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article-header__publish-date__value", " " ))]/text()').extract_first()
    if not publictime_info:
        publictime_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article-header__date", " " ))]/text()').extract_first()
    
    item['Title']  =  ' '.join(deal_title_info)
    item['firstauthor'] = deal_auther_info
    item['publictime'] = publictime_info
    item['DOI'] = deal_doi_info
    item['Abstract'] = deal_Abstract_info
    item['paper_fullspare']  = deal_paper_fullspare_info
    now = datetime.datetime.now()
    item['uploadtime'] = now
    item['uploaddate'] = now.strftime('%Y-%m-%d')
    item['Website'] = 'CELL'
    item['ifactor'] = get_paper_ifactor(item['paper_fullspare'])
    return item

def get_nature_keyword(response):
    item = defaultdict()
    ad_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-article-identifiers__type", " " ))]/text()').extract_first()
    if ad_info == 'ADVERTISEMENT FEATURE':
        item['DOI'] = 'NA'
        item['url'] = response.url
        item['Title']  = 'ADVERTISEMENT FEATURE'
        item['publictime'] = 'NA'
        item['DOI_link'] = response.url + '#citeas'
        item['Abstract'] = 'NA'
        item['paper_fullspare']  = 'NA'
        item['firstauthor'] = 'NA'
        now = datetime.datetime.now()
        item['uploadtime'] = now
        item['uploaddate'] = now.strftime('%Y-%m-%d')
        item['Website'] = 'Nature'
        return item
    DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article-item--open", " " ))]//em/text()').extract_first()
    if DOI_info and DOI_info.startswith('doi'):
        item['DOI'] = DOI_info.replace('doi: https://doi.org/','')
    title_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-article-title", " " ))]/text()').extract_first()
    if not title_info:
        title_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-article-magazine-title", " " ))]/text()').extract_first()
    Abstract_info = response.xpath('//*[(@id = "Abs1-content")]//p/text()').extract_first()
    if not Abstract_info:
        Abstract_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__teaser", " " ))]/text()').extract_first()
    firstauthor_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-article-author-list__item", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//a/text()').extract_first()
    if firstauthor_info:
        firstauthor_info = firstauthor_info.strip()
    item['url'] = response.url
    item['Title']  = title_info
    item['publictime'] = response.xpath('//time/text()').extract_first()
    item['DOI_link'] = response.url + '#citeas'
    item['Abstract'] = Abstract_info
    item['paper_fullspare']  = response.xpath('//i/text()').extract_first()
    item['firstauthor'] = firstauthor_info
    now = datetime.datetime.now()
    item['uploadtime'] = now
    item['uploaddate'] = now.strftime('%Y-%m-%d')
    item['Website'] = 'Nature'
    item['ifactor'] = get_paper_ifactor(item['paper_fullspare'])
    return item


def get_circulation_keyword(response):
    item = DoiItem()
    item['url'] = response.url
    DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "epub-section__doi__text", " " ))]/text()').extract_first()
    Abstract_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "abstractInFull", " " ))]//p/text()').getall()
    title_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "citation__title", " " ))]//a/text()').extract_first()
    if not title_info:
        title_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "citation__title", " " ))]/text()').extract_first()
    item['Title']  = title_info
    item['firstauthor'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "accordion__closed", " " ))]//span/text()').extract_first()
    item['publictime'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "epub-section__date", " " ))]/text()').extract_first()
    item['DOI'] = DOI_info.replace('https://doi.org/','')
    item['Abstract'] = ';'.join([x.strip().replace('\n        ','') for x in Abstract_info]).strip()
    item['paper_fullspare']  = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__tocHeading", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]/text()').extract_first()
    now = datetime.datetime.now()
    item['uploadtime'] = now
    item['uploaddate'] = now.strftime('%Y-%m-%d')
    item['Website'] = 'Circulation'
    item['ifactor'] = get_paper_ifactor(item['paper_fullspare'])
    return item

class DocPaperDOISpider(scrapy.Spider):
    name = 'docpaperdoi'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org']
    
    def __init__(self, name='docpaperdoi', **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = get_urls()
        print(self.start_urls)
        # self.start_urls = [
        #     'https://www.cell.com/ajhg/fulltext/S0002-9297(22)00363-9',
        #     'https://www.science.org/doi/10.1126/science.350.6261.699-a',
        #     # 'https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.122.060454',
        #     'https://www.nature.com/articles/s41467-022-32970-1',
        #     'https://pubmed.ncbi.nlm.nih.gov/27442339/'
        # ]
    def parse(self, response):
        if 'www.nature.com' in response.url:
            try:                
                item = DoiItem()
                single_item = get_nature_keyword(response)
                if 'DOI' in single_item.keys():
                    for key in single_item.keys():
                        if key !='DOI_link':
                            item[key] = single_item[key]
                    yield item
                else:
                    request = scrapy.Request(single_item['DOI_link'], callback=self.paper_parse,dont_filter=True)
                    for key in single_item.keys():
                        if key !='DOI_link':
                            item[key] = single_item[key]
                    request.meta['item'] = item
                    yield request
            except:
                print('yichang')
                yield None
        elif 'www.ahajournals.org' in response.url:
            try:
                item = get_circulation_keyword(response)
                yield item
            except:
                print('yichang')
                yield None
        elif 'www.science.org' in response.url:
            try:
                item = get_science_keyword(response)
                yield item
            except:
                print('yichang')
                yield None
        elif 'www.cell.com' in response.url:
            try:
                item = get_cell_keyword(response)
                yield item
            except:
                print('yichang')
                yield None
        elif 'pubmed.ncbi.nlm.nih.gov' in response.url:
            try:
                item = get_ncbi_keyword(response)
                yield item
            except:
                print('yichang')
                yield None
    def paper_parse(self, response):
        item = response.meta['item']
        DOI_info = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "c-bibliographic-information__list-item--doi", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "c-bibliographic-information__value", " " ))]/text()').extract_first()
        if not DOI_info:
            DOI_info = response.xpath('//*[@id="content"]/div[1]/article/div[3]/p[2]/em/text()').extract_first()
            if DOI_info:
                item['DOI'] = DOI_info.replace('doi: https://doi.org/', '')
            else:
                item['DOI'] = 'NA'
        else:
            item['DOI'] = DOI_info.replace('https://doi.org/','')
        yield item

