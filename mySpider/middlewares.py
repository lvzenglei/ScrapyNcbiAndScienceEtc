# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import requests
from scrapy import signals
from .settings import IPPOOL
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse, Response, TextResponse
from logging import getLogger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os,re,time,zipfile
from fake_useragent import UserAgent
import json

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
# Chrome代理模板插件(https://github.com/RobinDev/Selenium-Chrome-HTTP-Private-Proxy)目录
CHROME_PROXY_HELPER_DIR = 'chrome-proxy-extensions/Chrome-proxy-helper'
# 存储自定义Chrome代理扩展文件的目录
CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = 'chrome-proxy-extensions'
def get_chrome_proxy_extension(proxy):
    """获取一个Chrome代理扩展,里面配置有指定的代理(带用户名密码认证)
    proxy - 指定的代理,格式: username:password@ip:port
    """
    m = re.compile('([^:]+):([^\@]+)\@([\d\.]+):(\d+)').search(proxy)
    if m:
        # 提取代理的各项参数
        username = m.groups()[0]
        password = m.groups()[1]
        ip = m.groups()[2]
        port = m.groups()[3]
        # print(username,password,ip,port)
        # 创建一个定制Chrome代理扩展(zip文件)
        if not os.path.exists(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR):
            os.mkdir(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR)
        extension_file_path = os.path.join(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR, '{}.zip'.format(proxy.replace(':', '_')))
        if not os.path.exists(extension_file_path):
            # 扩展文件不存在，创建
            zf = zipfile.ZipFile(extension_file_path, mode='w')
            if not os.path.exists(CHROME_PROXY_HELPER_DIR):
                os.mkdir(CHROME_PROXY_HELPER_DIR)
            zf.write(os.path.join(CHROME_PROXY_HELPER_DIR, 'manifest.json'), 'manifest.json')
            # 替换模板中的代理参数
            background_content = open(os.path.join(CHROME_PROXY_HELPER_DIR, 'background.js')).read()
            background_content = background_content.replace('%proxy_host', ip)
            background_content = background_content.replace('%proxy_port', port)
            background_content = background_content.replace('%username', username)
            background_content = background_content.replace('%password', password)
            zf.writestr('background.js', background_content)
            zf.close()
        print(extension_file_path)
        return extension_file_path
    else:
        raise Exception('Invalid proxy format. Should be username:password@ip:port')

class MyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        site_name_list = ['www.science.org', 'www.cell.com', 'pubmed.ncbi', 'resurchify', 'ckb.jax.org', 'www.oncokb.org']
        special_url = 'https://www.oncokb.org/api/v1/utils/cancerGeneList.txt'
        # if 'www.science.org' not in request.url and 'www.cell.com' not in request.url and 'pubmed.ncbi' not in request.url and 'resurchify' not in request.url and 'ckb.jax.org' not in request.url :
        if any([True if site_name not in request.url else False for site_name in site_name_list] ) or special_url in request.url:
        # if True:
            print('middleware is MyspiderDownloaderMiddleware')
            # thisip=get_proxy_smartproxy()

            # thisip=get_proxy_ipidea()
            # thisip=getUsefulIP()
            thisip=random.choice(IPPOOL)
            # request.meta["proxy"]= "http://"+thisip
            # print(thisip)
            # print("this is ip:"+thisip["ipaddr"])
            # 由于代理池中的ip过少，因此暂时关闭IP代理池
            # request.meta["proxy"]="http://"+thisip["ipaddr"]
            print(thisip)
            
            ua = UserAgent()
            single_ua = ua.random
            request.headers['User-Agent'] = single_ua
            request.headers["referer"] = request.url
            # Must either:
            # - return None: continue processing this request
            # - or return a Response object
            # - or return a Request object
            # - or raise IgnoreRequest: process_exception() methods of
            #   installed downloader middleware will be called
            return None


    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        response._set_url(request.url)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        print(str(exception))
        print("Scrapy Single Html Failed")
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class SeleniumMiddleware():
    def __init__(self, timeout=None, chrome_options=[]):
        self.chrome_options = chrome_options
        self.timeout = timeout
        self.browser = ''

        # 等待整个dom树加载完成，即DOMContentLoaded这个事件完成，也就是只要 HTML 完全加载和解析完毕就开始执行操作。放弃等待图片、样式、子帧的加载。
        # normal：等待整个页面加载完毕再开始执行操作
        # eager：等待整个dom树加载完成，即DOMContentLoaded这个事件完成，也就是只要 HTML 完全加载和解析完毕就开始执行操作。放弃等待图片、样式、子帧的加载。
        # none：等待html下载完成，哪怕还没开始解析就开始执行操作
        #options.page_load_strategy = 'eager' #因为我只要DOM 树加载完成, 只需要文字内容，不需要图片样式和子帧(子帧可能不是不确定)

    def process_request(self, request, spider):
        """
        用Chrome抓取页面
        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse
        """
        # if 'science.org' in request.url or 'www.cell.com' in request.url or 'pubmed.ncbi' in request.url or 'resurchify' in request.url or 'ckb.jax.org' in request.url or 'oncokb.org' in request.url:
        site_name_list = ['www.science.org', 'www.cell.com', 'pubmed.ncbi', 'resurchify', 'ckb.jax.org', 'www.oncokb.org']
        special_url = 'https://www.oncokb.org/api/v1/utils/cancerGeneList.txt'
        # if 'www.science.org' not in request.url and 'www.cell.com' not in request.url and 'pubmed.ncbi' not in request.url and 'resurchify' not in request.url and 'ckb.jax.org' not in request.url :
        if any([True if site_name in request.url else False for site_name in site_name_list] ) and  special_url not in request.url:
        # if True:
            print('middleware is SeleniumMiddleware')
            try:
                options = Options()
                print(self.chrome_options)
                for chrome_option in self.chrome_options:
                    options.add_argument(chrome_option)
                # smartproxy proxy前需要设置http://    
                # thisip=get_proxy_smartproxy()
                # options.add_argument(f'--proxy-server=http://{thisip}')
                # thisip=get_proxy_ipidea()
                # thisip=getUsefulIP()
                thisip=random.choice(IPPOOL)
                options.add_argument(f'--proxy-server=http://{thisip}')

                # print(thisip)
                ua = UserAgent()
                single_ua = ua.random
                options.add_argument(f'user-agent={single_ua}')
                options.add_argument(f'referer={request.url}')
                
                options.page_load_strategy = 'eager'
                # print(options.arguments)
                # self.browser =  webdriver.Chrome(executable_path = '/usr/bin/chromedriver',options=options)
                if os.path.exists('/usr/bin/chromedriver'):
                    self.browser =  webdriver.Chrome(executable_path='/usr/bin/chromedriver',options=options)
                elif os.path.exists('/usr/local/bin/chromedriver'):
                    self.browser =  webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
                else:
                    self.browser =  webdriver.Chrome(options=options)
                # self.browser.maximize_window()
                # self.browser.set_window_size(1400, 700)
                # wait = WebDriverWait(self.browser, self.timeout)
                self.browser.get(request.url)
                if 'www.oncokb.org' in request.url:
                    try:
                        WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "rt-tbody"))
                        )
                    except TimeoutException:
                        # 这里如果没有except会直接500 intervar error, 添加处理后,可以正常输出返回内容
                        spider.logger.info(f"Element with class 'rt-tbody' not found within 10 seconds, Maybe Page: {request.url} contains no alteration ~~~")
                # if 'www.science.org' in request.url:
                #     wait.until(EC.presence_of_element_located((By.ID, 'pb-page-content')))
                # elif 'www.cell.com' in request.url:
                #     wait.until(EC.presence_of_element_located((By.ID, 'articleHeader')))
                # if 'www.ahajournals.org' in request.url:
                #     wait.until(EC.presence_of_element_located((By.ID, 'frmIssueItems')))
                # elif 'www.cell.com' in request.url:
                #     wait.until(EC.presence_of_element_located((By.ID, 'pb-page-content')))
                # elif 'www.nature.com' in request.url:
                #     wait.until(EC.presence_of_element_located((By.ID, 'search-article-list')))
                page_source  = self.browser.page_source
                self.browser.close()
                return HtmlResponse(url=request.url, body=page_source, request=request, encoding='utf-8', status=200)
            except TimeoutException:
                return HtmlResponse(url=request.url, status=500, request=request)
    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   chrome_options=crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS'))