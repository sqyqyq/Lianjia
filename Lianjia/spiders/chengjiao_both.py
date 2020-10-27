import scrapy
from scrapy import signals
from Lianjia.items import LianjiaItem
import csv
import logging


class Chengjiao_bothSpider(scrapy.Spider):
    name = 'chengjiao_both'
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

    # 获取城市链接及初始化csv文件
    def parse(self, response):
        # 定义价格 和 面积 的初始区间
        bp_price = 0
        ep_price = 10000
        ba_aria = 0
        ea_aria = 5000

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
                # 得到城市名称和链接（ 为了确保匹配才这么写的 其实可以简单点直接获取估计也不会出错）
                for k in range(len(links_city)):
                    link_city = links_city[k]
                    city = response.xpath('.//li/a[@href ="' + link_city + '"]/text()').extract_first()
                    # print(province, city, link_city)
                    # 构建成交网站的链接
                    link_chengjiao = link_city + 'chengjiao/'
                    # 构建host
                    host = link_city.replace("https://", '')
                    host = host.strip("/")
                    # 初始化csv文档（每次运行都会初始化一次）
                    fieldlnames = ['省', '市', '链接', '名称', ' 成交价', '挂牌价（万）', '成交周期（天）', '调价（次）', '带看（次）',
                                   '关注（人）', '浏览（次）', '房屋户型', '所在楼层', '建筑面积', '户型结构', '套内面积', '建筑类型', '房屋朝向',
                                   '建成年代', '装修情况', '建筑结构', '供暖方式', '梯户比例', '配备电梯', '链家编号', '交易权属', '挂牌时间', '房屋用途',
                                   '房屋年限', '房权所属', '成交价', '成交时间']
                    with open(province + '_' + city + ".csv", "a+", encoding='utf-8-sig', newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(fieldlnames)

                    request = scrapy.Request(link_chengjiao,
                                             # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                             headers={'Host': host, 'Referer': link_city + 'ershoufang/'},
                                             callback=self.parse_pagelinks,
                                             cb_kwargs={'province': province, 'city': city,
                                                        'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                        'ep_price': ep_price, 'stl_large': False, 'host': host,
                                                        'ba_aria': ba_aria, 'ea_aria': ea_aria})

                    yield request
            # else:
            #     break

    # 通过面积 价格 用途 来划分尽量得到数量在3000以内的链接
    def parse_pagelinks(self, response, province, city, link_chengjiao, bp_price, ep_price, stl_large, host, ba_aria, ea_aria):
        # 获取title
        total = response.xpath("//div[@class='total fl']//span[1]/text()").extract_first()
        # 检测是否有效
        if total is None:
            n_title = response.xpath("//div[@class='container']/div/h1/text()").get()
            # 如果是人机认证页面则重新请求并log下来
            if '人机认证' in n_title:
                logging.warning("machine test: No page in refresh cache " + response.url)
                request = scrapy.Request(response.url,
                                         # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                         meta={"refresh_cache": True}, dont_filter=True,
                                         headers={'Host': host, 'Referer': link_chengjiao},
                                         callback=self.parse_pagelinks,
                                         cb_kwargs={'province': province, 'city': city,
                                                    'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                    'ep_price': ep_price, 'stl_large': stl_large, 'host': host,
                                                    'ba_area': ba_aria, 'ea_aria': ea_aria})
                yield request
            else:
                # 不是也重新请求
                logging.warning("not machine test: No page in refresh cache " + response.url)
                request = scrapy.Request(response.url,
                                         # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                         meta={"refresh_cache": True}, dont_filter=True,
                                         headers={'Host': host, 'Referer': link_chengjiao},
                                         callback=self.parse_pagelinks,
                                         cb_kwargs={'province': province, 'city': city,
                                                    'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                    'ep_price': ep_price, 'stl_large': stl_large, 'host': host,
                                                    'ba_area': ba_aria, 'ea_aria': ea_aria})
                yield request

        else:
            total_num = int(total)
            # 判断是否大于 0
            if total_num != 0:
                # 判断是否小于3000
                if total_num <= 3000 or stl_large:
                    # 数字写入stat csv 文件（方便测试 可不用）
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
                                                            'link_chengjiao': link_page, 'host': host,})
                        yield request
                else:
                    # 如果大于3000 则开始定义filter 使其小于3000
                    # 这里使用 面积 售价和用途来划分 不容易丢失或者重复数据
                    if (ea_aria - ba_aria) > 1:
                        mid_aria = int((ea_aria + ba_aria) / 2)
                        left_link_page = link_chengjiao + "ba" + str(ba_aria) + "ea" + str(mid_aria) + "/"
                        right_link_page = link_chengjiao + "ba" + str(mid_aria) + "ea" + str(ea_aria) + "/"

                        request_left = scrapy.Request(left_link_page,
                                                      # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                      headers={'Host': host, 'Referer': link_chengjiao},
                                                      callback=self.parse_pagelinks,
                                                      cb_kwargs={'province': province, 'city': city,
                                                                 'link_chengjiao': link_chengjiao,
                                                                 'bp_price': bp_price, 'ep_price': ep_price,
                                                                 'stl_large': stl_large, 'host': host,
                                                                 'ba_area': ba_aria, 'ea_aria': mid_aria})
                        request_right = scrapy.Request(right_link_page,
                                                       # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                       headers={'Host': host, 'Referer': link_chengjiao},
                                                       callback=self.parse_pagelinks,
                                                       cb_kwargs={'province': province, 'city': city,
                                                                  'link_chengjiao': link_chengjiao,
                                                                  'bp_price': bp_price, 'ep_price': ep_price,
                                                                  'stl_large': stl_large, 'host': host,
                                                                  'ba_area': mid_aria, 'ea_aria': ea_aria})
                        yield request_left
                        yield request_right

                    elif (ep_price - bp_price) > 1:
                        mid_price = int((ep_price + bp_price) / 2)
                        left_link_page = link_chengjiao + "bp" + str(bp_price) + "ep" + str(mid_price) + "/"
                        right_link_page = link_chengjiao + "bp" + str(mid_price) + "ep" + str(ep_price) + "/"

                        request_left = scrapy.Request(left_link_page,
                                                      # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                      headers={'Host': host, 'Referer': link_chengjiao},
                                                      callback=self.parse_pagelinks,
                                                      cb_kwargs={'province': province, 'city': city,
                                                                 'link_chengjiao': link_chengjiao,
                                                                 'bp_price': bp_price, 'ep_price': mid_price,
                                                                 'stl_large': stl_large, 'host': host,
                                                                 'ba_area': ba_aria, 'ea_aria': ea_aria})
                        request_right = scrapy.Request(right_link_page,
                                                       # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                       headers={'Host': host, 'Referer': link_chengjiao},
                                                       callback=self.parse_pagelinks,
                                                       cb_kwargs={'province': province, 'city': city,
                                                                  'link_chengjiao': link_chengjiao,
                                                                  'bp_price': mid_price, 'ep_price': ep_price,
                                                                  'stl_large': stl_large, 'host': host,
                                                                  'ba_area': ba_aria, 'ea_aria': ea_aria})
                        yield request_left
                        yield request_right
                    else:
                        # 用用途划分且把stl large 为true 因为要是仍旧大于3000 也没办法了
                        usage = ["sf1", "sf2", "sf3", "sf4", "sf5", "sf6"]
                        for u in usage:
                            new_link_page = link_chengjiao + u + "ba" + str(ba_aria) + "ea" + str(ea_aria) + "bp" + str(bp_price) + "ep" + str(ep_price) + "/"
                            yield scrapy.Request(new_link_page,
                                                 # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                                 callback=self.parse_pagelinks,
                                                 headers={'Host': host, 'Referer': response.url},
                                                 cb_kwargs={'province': province, 'city': city,
                                                            'link_chengjiao': link_chengjiao, 'bp_price': bp_price,
                                                            'ep_price': ep_price, 'stl_large': True, 'host': host,
                                                            'ba_area': ba_aria, 'ea_aria': ea_aria})
            else:
                logging.warning("totol is 0 " + response.url)
        # print(response, response.status, total_num)

    # 获取每个房子的链接
    def parse_itemlinks(self, response, province, city, link_chengjiao, host):
        itemlinks = response.xpath("//div[@class = 'info']/div[@class = 'title']/a/@href").getall()
        # 判断是否有效
        if itemlinks is None or itemlinks == []:
            request = scrapy.Request(response.url,
                                     # meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                     # headers={'Host': host, 'Referer': response.url},
                                     callback=self.parse_itemlinks,
                                     cb_kwargs={'province': province, 'city': city,
                                                'link_chengjiao': link_chengjiao, 'host': host})

            logging.warning("This is a warning: No links" + link_chengjiao)
        # 测试用 把去掉这段代码的注释 然后注释掉这之后的代码 就是单获取房子链接的爬虫（还要修改pipeline）
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

    # 获取房子详细信息
    def parse_getitem(self, response, province, city, link_chengjiao, host):
        title = response.xpath("//h1[@class= 'index_h1']/text()").getall()
        # 检测人机认证
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
            # 获取信息
            price = response.xpath("//span[@class='dealTotalPrice']/i/text()").getall()
            # average = response.xpath("//div[@class='price']//b/text()").getall()
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
            # 拼凑在成list 方便写入csv
            item = [province] + [city] + [link_chengjiao] + title + price + msg + content + record_list

            line = LianjiaItem()
            line['item'] = item
            yield line
