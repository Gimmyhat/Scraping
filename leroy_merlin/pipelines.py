# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from db import CLIENT
import os
from urllib.parse import urlparse


class LeroyMerlinPipeline:
    def __init__(self):
        client = MongoClient(CLIENT)
        self.mongo_base = client['leroy_products']

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeroyMerlinPhotosPipeline(ImagesPipeline):

    # Раскидывает фотографии в папки по названию товара
    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['url'].split('/')[-2]}/" + os.path.basename(urlparse(request.url).path)

    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
