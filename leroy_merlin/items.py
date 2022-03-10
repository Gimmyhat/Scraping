# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, Compose, MapCompose


def clear_price(value):
    try:
        return int(value.replace(' ', ''))
    except:
        return value


def clear_params(value):
    try:
        return {k: v.strip() for (k, v) in value.items()}
    except:
        return value


class LeroyMerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(clear_price))
    url = scrapy.Field(output_processor=TakeFirst())
    params = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(clear_params))


    # {'_id': ObjectId('6229792d180f9dc9d7f0d3de'),
    #  'name': 'Труба полипропиленовая для ГВС Политэк Ø20 мм 2 м',
    #  'params': {'Вес нетто (кг)': '0.3',
    #             'Гарантия (лет)': '1',
    #             'Диаметр (мм)': '20',
    #             'Длина (м)': '2.0',
    #             'Использование': 'Холодная и горячая вода',
    #             'Максимальная температура применения (°C)': '70.0',
    #             'Максимальное давление (бар)': '20.0',
    #             'Марка': 'ПОЛИТЭК',
    #             'Основной материал': 'Полипропилен',
    #             'Страна производства': 'Россия',
    #             'Тип продукта': 'ППР-труба',
    #             'Толщина (мм)': '3.0',
    #             'Цветовая палитра': 'Белый'},
    #  'photos': [{'checksum': '1bb4cfc26e6f1dfc49dd9df0490eb9f4',
    #              'path': 'truba-polipropilenovaya-dlya-gvs-politek-20-mm-2-m-13562934/13562934.jpg',
    #              'status': 'downloaded',
    #              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/13562934.jpg'},
    #             {'checksum': '08becc1c2d6e483148ca73a4f90d6d4b',
    #              'path': 'truba-polipropilenovaya-dlya-gvs-politek-20-mm-2-m-13562934/13562934_01.jpg',
    #              'status': 'downloaded',
    #              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/13562934_01.jpg'}],
    #  'price': 90,
    #  'url': 'https://leroymerlin.ru/product/truba-polipropilenovaya-dlya-gvs-politek-20-mm-2-m-13562934/'}

