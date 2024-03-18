# Scrapy settings for mySpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from collections import defaultdict
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

with open (f'{BASE_DIR}/.env','r') as env_file:
    env_list = env_file.readlines()
env = defaultdict()

for env_f in env_list:
    if env_f.startswith('#'):
        continue
    env_f = re.sub(r"#.*", "", env_f)
    single_list = list(filter(None,env_f.strip().split('=',1)))
    key = single_list[0].strip()
    value = single_list[1].strip()
    if "'" in value:
        value = value.strip("'")
    else:
        value = int(value)
    env[key] = value

ONCOKB_FINAL_DIR=env.get('OncoKB_Final_Dir','/nfs/disk1/user/training/519_xlsx/database/Regular_update_database/oncokb/')
ONCOKB_SHEET_NAME=env.get('ONCOKB_SHEET_NAME','OncoKB')
# print('Loading config file successfully')
# PROXYUSENAME = env['PROXYUSENAME']
# PROXYPASSWORD = env['PROXYPASSWORD']
# KUAI_ORDERID = env['KUAI_ORDERID']
# KUAI_SIGNATURE = env['KUAI_SIGNATURE']
# KUAI_Default_Num = env['KUAI_Default_Num']
# # SMARTPROXY
# SMARTPROXYAPPKEY = env['SMARTPROXYAPPKEY']
MONGO_URI=env['MONGO_URI']
ScrapyProxy=env["ScrapyProxy"]
# MONGO_URL = 'localhost'
MONGO_DATABASE = env['MONGO_DATABASE']  # 数据库的名字(无法设置成docmanage，因此暂时设置成admin).

BOT_NAME = 'mySpider'

SPIDER_MODULES = [
    # 'mySpider.spiders.docpapercell',
    # 'mySpider.spiders.docpapercirculation',
    # 'mySpider.spiders.docpapernature',
    # 'mySpider.spiders.docpaperncbi',
    # 'mySpider.spiders.docpaperscience',
    # 'mySpider.spiders.docpaperdoi',
    'mySpider.spiders.ckbScrapyFirstStep',
    'mySpider.spiders.ckbScrapySecondStep',
    'mySpider.spiders.oncokbScrapyFirstStep',
    'mySpider.spiders.oncokbScrapySecondStep',
    'mySpider.spiders.oncokbScrapyThirdStepExport',
    ]
NEWSPIDER_MODULE = 'mySpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'

IPPOOL=[
    ScrapyProxy
]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'mySpider.middlewares.MyspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'mySpider.middlewares.MyspiderDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'mySpider.pipelines.MyspiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
LOG_ENABLED = True
LOG_FILE='./logs/scrapy.log'
LOG_LEVEL = 'INFO' 
RETRY_ENABLED = True
RETRY_TIMES = 1
# DNS_TIMEOUT = 20
# REDIRECT_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    #  'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware':543,
    'mySpider.middlewares.MyspiderDownloaderMiddleware':544,
    'mySpider.middlewares.SeleniumMiddleware': 543
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

ITEM_PIPELINES = {
    'mySpider.pipelines_mongo.DocpaperPipeline': 300
}

# IMAGES_STORE = '/root/repo/mySpider/figure/'

# MONGO_URI='mongodb://admin:admin@192.168.3.222:11111/portal?authSource=admin&tz_aware=true'
# # MONGO_URL = 'localhost'
# MONGO_DATABASE = 'admin'  # 数据库的名字(无法设置成docmanage，因此暂时设置成admin).

# selenium config
SELENIUM_TIMEOUT = 20
SELENIUM_DRIVER_ARGUMENTS=['--headless','--disable-dev-shm-usage','--no-sandbox'] 

# print('load all config info successfully!!!')