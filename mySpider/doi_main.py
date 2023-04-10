from scrapy.cmdline import execute   #调用此函数可以执行scrapy的脚本
from scrapy.crawler import CrawlerProcess
from collections import defaultdict
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

import subprocess
import datetime
import pymongo
import requests
import json
import sys
import os

setting = get_project_settings()
crawler = CrawlerProcess(setting)
crawler.crawl('docpaperdoi')
d = crawler.join()
d.addBoth(lambda _: reactor.stop())
reactor.run() # the script will block here until all crawling jobs are finished