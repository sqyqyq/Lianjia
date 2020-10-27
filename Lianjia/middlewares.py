# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
from collections import defaultdict
import requests
from lxml import etree
import logging
import json
import datetime
import time

from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet import defer
# from twisted.web._newclient import ResponseFailed
from twisted.web._newclient import ResponseFailed

from Lianjia.Freeproxypool import proxy_pool
from twisted.internet.defer import DeferredLock

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twisted.internet.error import TCPTimedOutError, TimeoutError, DNSLookupError, ConnectionDone, ConnectError, \
    ConnectionLost

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class LianjiaSpiderMiddleware:
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


class LianjiaDownloaderMiddleware:
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
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


#
class IPProxyDownloadMiddleware:
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      TunnelError)

    PROXIES = ["173.82.202.9:8878", "204.13.155.240:8878", "129.213.119.234:8878", "129.213.215.126:8878", None]

    # PROXIES = ["173.82.202.9:8878"]
    def process_request(self, request, spider):
        pass
        if not request.meta.get('proxy'):
            proxy = random.choice(self.PROXIES)
            request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        n_title = response.xpath("//div[@class='container']/div/h1/text()").get()
        if int(response.status) >= 400 or n_title is not None:
            if int(response.status) != 404:
                print(n_title)
                if '人机认证' in n_title:
                    print(response)
                    print(request.headers)
                    print(request.meta)
                    logging.warning(request.headers)
                    logging.warning(request.meta)
                    del request.meta['proxy']
                    request.meta['refresh_cache'] = True
                    request.dont_filter = True
                    return request
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        cur_proxy = request.meta.get('proxy')
        # 如果本次请求使用了代理，并且网络请求报错，认为该IP出现问题了
        if cur_proxy and isinstance(exception, self.ALL_EXCEPTIONS):
            # print('error (%s) occur when use proxy %s' % (exception, cur_proxy))
            # print(request.url)
            logging.warning(request.url + 'error (%s) occur when use proxy %s' % (exception, cur_proxy))
            logging.warning(request.headers['User-Agent'])
            print('error (%s) occur when use proxy %s' % (exception, cur_proxy))
            # self.stats[cur_proxy] += 1
            # print(self.stats[cur_proxy])
            # if self.stats[cur_proxy] > 5:
            #     print(cur_proxy)
            #     print('lianjiaip:D123456d@' + cur_proxy.strip('//') in self.proxies)
            #     print(exception)
            #     print(str(time.time() - self.time))
            # print('%s got wrong code %s times' % (cur_proxy, self.stats[cur_proxy]))
            # logging.warning('%s got wrong exception %s times' % (cur_proxy, self.stats[cur_proxy]))
            del request.meta['proxy']
            request.meta['refresh_cache'] = True
            request.dont_filter = True
            return request

        # every 5 sec request the ip ippool
        # before assign proxy to the request check it expire in more than 3 sec else remove the proxy form list


class RandomProxyMiddleware:
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      TunnelError)

    def __init__(self):
        # 2. 初始化配置及相关变量
        # self.proxies = settings.getlist('PROXIES')
        self.lock = DeferredLock()
        self.lockproxy = DeferredLock()
        self.proxies = {}
        self.api = 'http://lianjiaip.v4.dailiyun.com/query.txt?key=NP7CE43238&word=&count=50&rand=false&detail=true'
        self.stats = defaultdict(int)
        self.max_failed = 10
        self.time = time.time()

    # @classmethod
    # def from_crawler(cls, crawler):
    #     # 1. 创建中间件对象
    #     if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
    #         raise NotConfigured
    #
    #     return cls(crawler.settings)

    def process_request(self, request, spider):
        # 3. 为每个request对象分配一个随机的IP代理
        # 上锁 以防多次获取无效ip
        self.lockproxy.acquire()
        if time.time() - self.time > 6 or len(self.proxies) < 15:
            # 更新ip池
            self.get_proxy()
        # 给ip
        if self.proxies and not request.meta.get('proxy'):
            # and request.url not in spider.start_urls:
            proxy = random.choice(list(self.proxies))
            # logging.warning('get proxy %s //' % proxy + str(int(self.proxies[proxy]) - time.time())+ "///"+
            # str(self.time))
            request.meta['proxy'] = proxy
        self.lockproxy.release()

    def process_response(self, request, response, spider):
        # 4. 请求成功则调用process_response
        # cur_proxy = request.meta.get('proxy')
        cur_proxy = request.meta.get('proxy').replace('http://', 'http://lianjiaip:D123456d@')
        # 判断是否被对方封禁
        n_title = response.xpath("//div[@class='container']/div/h1/text()").get()
        # 判断人机认证
        if n_title is not None:
            if '人机认证' in n_title:
                print(n_title)
                self.stats[cur_proxy] += 1
                logging.warning('%s 人机认证 %s times' % (cur_proxy, self.stats[cur_proxy]))
                if self.stats[cur_proxy] >= self.max_failed:
                    # print('delete wrong http code (%s) when use %s' % (response.status, cur_proxy))
                    logging.warning('delete wrong http code (%s) when use %s' % (response.status, cur_proxy))
                    # 可以认为该IP被对方封禁了，从代理池中将该IP删除
                    self.remove_proxy(cur_proxy)
                del request.meta['proxy']
                # del request.meta['retry_times']
                # 将该请求重新安排调度下载
                request.meta['refresh_cache'] = True
                request.dont_filter = True
                return request
            else:
                logging.warning('%s 取到n_title但人机认证不在 %s ' % (response.url, cur_proxy))
        # cur_proxy not in self.proxies or
        # 判断是否 错误代码
        if response.status in [401, 403]:
            # print(n_title is not None)
            # print(self.proxies)
            # print(cur_proxy not in self.proxies)
            # print(type(response.status))
            # print(int(response.status) > 400)
            # print(cur_proxy not in self.proxies)
            # print(response.status)
            # logging.warning('%s got wrong code %s times' % (cur_proxy, self.stats[cur_proxy]))
            # print('%s got wrong code %s times' % (cur_proxy, self.stats[cur_proxy]))
            # 给相应的IP失败次数+1
            self.stats[cur_proxy] += 1
            if self.stats[cur_proxy] >= self.max_failed:
                # print('delete wrong http code (%s) when use %s' % (response.status, cur_proxy))
                # logging.warning('delete wrong http code (%s) when use %s' % (response.status, cur_proxy))
                # 可以认为该IP被对方封禁了，从代理池中将该IP删除
                self.remove_proxy(cur_proxy)
            del request.meta['proxy']
            # del request.meta['retry_times']
            # 将该请求重新安排调度下载
            request.meta['refresh_cache'] = True
            request.dont_filter = True
            return request
        return response

    def process_exception(self, request, exception, spider):
        # 4. 请求失败则调用process_exception
        cur_proxy = request.meta.get('proxy').replace('http://', 'http://lianjiaip:D123456d@')
        # 如果本次请求使用了代理，并且网络请求报错，认为该IP出现问题了
        if cur_proxy and isinstance(exception, self.ALL_EXCEPTIONS):
            # print('error (%s) occur when use proxy %s' % (exception, cur_proxy))
            # print(request.url)
            logging.warning(request.url + 'error (%s) occur when use proxy %s' % (exception, cur_proxy))
            # logging.warning(request.headers['User-Agent'])
            # print('error (%s) occur when use proxy %s' % (exception, cur_proxy))
            self.stats[cur_proxy] += 1
            # print(self.stats[cur_proxy])
            # if self.stats[cur_proxy] > 5:
            #     print(cur_proxy)
            #     print('lianjiaip:D123456d@' + cur_proxy.strip('//') in self.proxies)
            #     print(exception)
            #     print(str(time.time() - self.time))
            # print('%s got wrong code %s times' % (cur_proxy, self.stats[cur_proxy]))
            # logging.warning('%s got wrong exception %s times' % (cur_proxy, self.stats[cur_proxy]))
            del request.meta['proxy']
            if self.stats[cur_proxy] >= self.max_failed:
                # print('delete wrong http code () when use')
                # logging.warning('delete wrong http code () when use')
                # 可以认为该IP被对方封禁了，从代理池中将该IP删除
                # print(self.stats[cur_proxy])
                self.remove_proxy(cur_proxy)
                # print(len(self.proxies))
            # 如果使用这一行代码，则下次还会retry 反之下次不会retry
            # del request.meta['retry_times']
            request.meta['refresh_cache'] = True
            request.dont_filter = True
            return request

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.pop(proxy)
            print('remove %s from proxy list' % proxy)

    def get_proxy(self):
        # self.lock.acquire()
        # 通过链接获取 ip （偶尔发现爬虫卡住，好像就是这的问题）
        intime = time.time() - self.time
        if intime > 6 or len(self.proxies) < 15:
            response = requests.get(self.api)
            text = response.text
            result = text.split('\r\n')
            result.remove('')
            ip = {}
            for i in result:
                ii = i.split(',')
                ip.update({'http://lianjiaip:D123456d@' + ii[0]: ii[4]})

            # print('get ip')
            # print(intime)
            print(str(len(ip)))
            self.proxies = ip
            self.time = time.time()

        # if len(self.proxies) < 30:
        #     print(min)
        #     response = requests.get(self.api)
        #     text = response.text
        #     result = text.split('\r\n')
        #     result.remove('')
        #     ip = []
        #     for i in result:
        #         ip.append('lianjiaip:D123456d@' + i)
        #
        #     print('get ip')
        #     print(ip)
        #     print(str(len(ip)))
        #     logging.warning('get ip' % ip)
        #     self.proxies.extend(ip)

        # self.lock.release()

