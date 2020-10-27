# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import logging
from scrapy.exceptions import DropItem
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class LianjiaPipeline:
    def __init__(self):
        self.ids_seen = 0
    #     with open('links_bj2.csv', 'r', encoding='utf-8-sig') as file:
    #         reader = csv.reader(file)
    #         for row in reader:
    #             self.ids_seen.append(row[2])

    def process_item(self, item, spider):
        # self.ids_seen = self.ids_seen + len(item['links'])
        # with open('links_bj2.csv', 'a+', encoding='utf-8-sig', newline="") as csvfile:
        #     for i in item['links']:
        #         # if i in self.ids_seen:
        #         #     raise DropItem("Duplicate item found: %r" % i)
        #         # else:
        #         line = [item['province'], item['city'], i]
        #         writer = csv.writer(csvfile)
        #         writer.writerow(line)
        # return item
        # # if spider.name is 'chengjiao':

        # if item['item'][2] in self.ids_seen:
        #     logging.warning("Duplicate item found: %r" % item[2])
        #     raise DropItem("Duplicate item found: %r" % item[2])
        if len(item['item']) < 20:
            logging.warning("renjiyanzheng: %r" % item['item'][2])
            with open('noItemstat.csv', 'a+', encoding='utf-8-sig', newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(item['item'])
            raise DropItem("renjiyanzheng %r" % item['item'][2])
        elif '车库' in item['item'][28]:
            logging.warning("delete 车库: %r" % item['item'][3])
            raise DropItem("车库: %r" % item['item'][3])
        else:
            with open(item['item'][0] + '_' + item['item'][1] + ".csv", "a+", encoding='utf-8-sig',
                      newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(item['item'])
                self.ids_seen = self.ids_seen + 1
            return item

    def close_spider(self, spider):
        logging.warning("This is a warning: " + str(self.ids_seen))
