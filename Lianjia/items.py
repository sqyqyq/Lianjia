# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LianjiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    item = scrapy.Field()
    links = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
