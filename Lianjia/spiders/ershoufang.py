import scrapy
from scrapy import signals
from Lianjia.items import LianjiaItem
import csv
import logging


class ErshoufangSpider(scrapy.Spider):
    name = 'ershoufang'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://www.lianjia.com/city/']
    stat = 0

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(ErshoufangSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    #     return spider
    #
    # def spider_closed(self, spider):
    #     spider.logger.info('Spider closed: %s', spider.name)

    def parse(self, response):
        bp_price = 0
        ep_price = 10000
        # 读取每行 因为一个省一行
        lines = response.xpath('//div[@class="city_province"]')
        i = 0
        for line in lines:
            i = i + 1
            if i == 2:
                # 得到省名
                province = line.xpath('.//div/text()').extract_first()
                # cities = []
                # 得到城市链接
                links_city = line.xpath('.//li/a/@href').extract()
                # 得到城市名称（ 为了确保匹配才这么写的 其实可以简单点直接获取估计也不会出错）
                for k in range(len(links_city)):
                    link_city = links_city[k]
                    city = response.xpath('.//li/a[@href ="' + link_city + '"]/text()').extract_first()
                    # print(province, city, link_city)
                    # 构建成交网站的链接
                    link_chengjiao = link_city + 'chengjiao/'
                    host = link_city.replace("https://", '')
                    host = host.strip("/")

                    fieldlnames = ['省', '市', '链接', '名称', ' 成交价', '均价', '挂牌价（万）', '成交周期（天）', '调价（次）', '带看（次）',
                                   '关注（人）', '浏览（次）', '房屋户型', '所在楼层', '建筑面积', '户型结构', '套内面积', '建筑类型', '房屋朝向',
                                   '建成年代', '装修情况', '建筑结构', '供暖方式', '梯户比例', '配备电梯', '链家编号', '交易权属', '挂牌时间', '房屋用途',
                                   '房屋年限', '房权所属', '成交价', '单价', '成交时间']
                    with open(province + '_' + city + ".csv", "a+", encoding='utf-8-sig', newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(fieldlnames)

                    request = scrapy.Request(link_chengjiao,
                                             # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                             headers={'Host': host, 'Referer': link_city + 'ershoufang/'},
                                             callback=self.parse_pagelinks,
                                             cb_kwargs={'province': province, 'city': city,
                                                        'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                        'ep_price': ep_price, 'stl_large': False, 'host': host})

                    yield request
            # else:
            #     break

    def parse_pagelinks(self, response, province, city, link_chengjiao, bp_price, ep_price, stl_large, host):
        total = response.xpath("//div[@class='total fl']//span[1]/text()").extract_first()
        if total is None:
            n_title = response.xpath("//div[@class='container']/div/h1/text()").get()
            if '人机认证' in n_title:
                logging.warning("人机认证: No page in refresh cache " + response.url)
                request = scrapy.Request(response.url,
                                         # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                         meta={"refresh_cache": True}, dont_filter=True,
                                         headers={'Host': host, 'Referer': link_chengjiao},
                                         callback=self.parse_pagelinks,
                                         cb_kwargs={'province': province, 'city': city,
                                                    'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                    'ep_price': ep_price, 'stl_large': stl_large, 'host': host})
                yield request
            else:
                request = scrapy.Request(response.url,
                                         # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                         meta={"refresh_cache": True}, dont_filter=True,
                                         headers={'Host': host, 'Referer': link_chengjiao},
                                         callback=self.parse_pagelinks,
                                         cb_kwargs={'province': province, 'city': city,
                                                    'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                    'ep_price': ep_price, 'stl_large': stl_large, 'host': host})
                yield request

        else:
            total_num = int(total)
            if total_num != 0:
                if total_num <= 3000 or stl_large:
                    self.stat = self.stat + total_num
                    line = [response.url, total, self.stat]
                    with open('stat.csv', 'a+', encoding='utf-8-sig', newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(line)
                    if total_num > 3000:
                        logging.warning("仍旧大于3000: " + province + city + response.url + str(total_num))
                    # 提取每页的链接
                    page_data = eval(response.xpath("//div[@class='page-box house-lst-page-box']/@page-data").get())
                    total_page = page_data.get('totalPage')
                    for x in range(total_page):
                        link_page = response.url + "pg" + str(x + 1) + "/"
                        request = scrapy.Request(link_page,
                                                 # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                 headers={'Host': host, 'Referer': response.url},
                                                 callback=self.parse_itemlinks,
                                                 cb_kwargs={'province': province, 'city': city,
                                                            'link_chengjiao': link_page, 'host': host})
                        yield request
                else:
                    # 如果大于3000 则开始定义filter 使其小于3000
                    # 这里使用 售价和用途来划分 不容易丢失或者重复数据
                    if (ep_price - bp_price) > 1:
                        mid_price = int((ep_price + bp_price) / 2)
                        left_link_page = link_chengjiao + "bp" + str(bp_price) + "ep" + str(mid_price) + "/"
                        right_link_page = link_chengjiao + "bp" + str(mid_price) + "ep" + str(ep_price) + "/"

                        request_left = scrapy.Request(left_link_page,
                                                      # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                      headers={'Host': host, 'Referer': link_chengjiao},
                                                      callback=self.parse_pagelinks,
                                                      cb_kwargs={'province': province, 'city': city,
                                                                 'link_chengjiao': link_chengjiao,
                                                                 'bp_price': bp_price,
                                                                 'ep_price': mid_price, 'stl_large': stl_large,
                                                                 'host': host})
                        request_right = scrapy.Request(right_link_page,
                                                       # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                       headers={'Host': host, 'Referer': link_chengjiao},
                                                       callback=self.parse_pagelinks,
                                                       cb_kwargs={'province': province, 'city': city,
                                                                  'link_chengjiao': link_chengjiao,
                                                                  'bp_price': mid_price,
                                                                  'ep_price': ep_price, 'stl_large': stl_large,
                                                                  'host': host})
                        yield request_left
                        yield request_right
                    else:
                        usage = ["sf1", "sf2", "sf3", "sf4", "sf5", "sf6"]
                        for u in usage:
                            new_link_page = link_chengjiao + u + "bp" + str(bp_price) + "ep" + str(ep_price) + "/"
                            yield scrapy.Request(new_link_page,
                                                 # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                 callback=self.parse_pagelinks,
                                                 headers={'Host': host, 'Referer': response.url},
                                                 cb_kwargs={'province': province, 'city': city,
                                                            'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                            'ep_price': ep_price, 'stl_large': True, 'host': host})
            else:
                logging.warning("totol is 0 " + response.url)
        # print(response, response.status, total_num)

    def parse_itemlinks(self, response, province, city, link_chengjiao, host):
        itemlinks = response.xpath("//div[@class = 'info']/div[@class = 'title']/a/@href").getall()
        if itemlinks is None or itemlinks == []:
            request = scrapy.Request(response.url,
                                     # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                     # headers={'Host': host, 'Referer': response.url},
                                     callback=self.parse_itemlinks,
                                     cb_kwargs={'province': province, 'city': city,
                                                'link_chengjiao': link_chengjiao, 'host': host})

            logging.warning("This is a warning: No links" + link_chengjiao)
        # line = LianjiaItem()
        # line['links'] = itemlinks
        # line['province'] = province
        # line['city'] = city
        # yield line

        for link in itemlinks:
            # yield link
            request = scrapy.Request(link,
                                     # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                     headers={'Host': host, 'Referer': response.url},
                                     callback=self.parse_getitem,
                                     cb_kwargs={'province': province, 'city': city, 'link_chengjiao': link,
                                                'host': host})
            yield request

    def parse_getitem(self, response, province, city, link_chengjiao, host):
        title = response.xpath("//h1[@class= 'index_h1']/text()").getall()
        if not title:
            n_title = response.xpath("//div[@class='container']/div/h1/text()").get()
            if '人机认证' in n_title:
                logging.warning("人机认证: No title in refresh cache" + link_chengjiao)
                request = scrapy.Request(link_chengjiao,
                                         # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                         meta={"refresh_cache": True}, dont_filter=True,
                                         headers={'Host': host, 'Referer': link_chengjiao},
                                         callback=self.parse_getitem,
                                         cb_kwargs={'province': province, 'city': city,
                                                    'link_chengjiao': link_chengjiao, 'host': host})
                yield request
            else:
                logging.warning("This is a warning: No title" + link_chengjiao)
        else:
            price = response.xpath("//span[@class='dealTotalPrice']/i/text()").getall()
            average = response.xpath("//div[@class='price']//b/text()").getall()
            msg = response.xpath("//div[@class='msg']//label/text()").getall()
            content_temp = response.xpath("//div[@class = 'content']//li/text()").getall()
            content = []
            for c in content_temp:
                content.append(c.strip())
            if title is None or '':
                logging.warning('warning there is no Title' + link_chengjiao)

            record_list = []
            record_price = response.xpath("//ul[@class = 'record_list']//span[@class = 'record_price']/text()").getall()
            record_detail = response.xpath("//ul[@class = 'record_list']//p[@class = 'record_detail']/text()").getall()
            for r in range(len(record_price)):
                record_list.append(record_price[r])
                record_list.extend(record_detail[r].split(","))

            item = [province] + [city] + [link_chengjiao] + title + price + average + msg + content + record_list

            line = LianjiaItem()
            line['item'] = item
            yield line
