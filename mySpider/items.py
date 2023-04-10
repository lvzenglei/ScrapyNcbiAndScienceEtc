import scrapy
class NcbiItem(scrapy.Item):
   url = scrapy.Field()
   title = scrapy.Field()
   author = scrapy.Field()
   PMID = scrapy.Field()
   PMCID = scrapy.Field()
   DOI = scrapy.Field()
   Abstract = scrapy.Field()
   keywords = scrapy.Field()
   conflict = scrapy.Field()
   figure = scrapy.Field()
   references = scrapy.Field()
   referencelink = scrapy.Field()
   substance = scrapy.Field()
   fullresource = scrapy.Field()
   deal_keywords = scrapy.Field()
   MeSH_terms = scrapy.Field()
class NcbiidItem(scrapy.Item):
   # name = scrapy.Field()
   # title = scrapy.Field()
   # info = scrapy.Field()
   ids = scrapy.Field()
   doi = scrapy.Field()

class PageItem(scrapy.Item):
   origin_url = scrapy.Field() #最初三个关键词拼成的url
   related_url = scrapy.Field() #上级衍生的url，这里可以理解为page_url
   url = scrapy.Field() #当前请求的url
   page = scrapy.Field() #原始url的页码数
   date = scrapy.Field()  #插入时的时间
   status = scrapy.Field() # 目前是否已经爬取 (score,submit,success)
   type = scrapy.Field() # 来自哪个网站(Nature,Cell,Science,Circulation,NCBI,Other)

#  20220825 
#  lvzenglei@singleronbio.com
#  为了数据解读组 定期爬取多网站文献信息目的
class  DoiItem(scrapy.Item):
   url = scrapy.Field() # 文献对应链接
   Title = scrapy.Field() # 文献名
   paper_fullspare = scrapy.Field() #杂志名(全称)
   # Impact_Factor = scrapy.Field() # 影响因子
   publictime = scrapy.Field() #发表年份 
   uploadtime = scrapy.Field() #上传日期
   uploaddate = scrapy.Field() #爬取时的日期，为了后续便于筛选
   DOI = scrapy.Field() #DOI
   firstauthor = scrapy.Field() #一作
   Abstract = scrapy.Field() # 摘要
   Website =  scrapy.Field() # 爬取的网站来源
   ifactor = scrapy.Field() # 影响因子

class IPpoolItem(scrapy.Item):
   proxy = scrapy.Field() # 对应的proxy
   add_time = scrapy.Field() # 对应的add_time
   status = scrapy.Field() # 对应的status
   company = scrapy.Field() #proxy的来源厂家