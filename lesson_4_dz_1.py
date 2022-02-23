import re
from datetime import datetime as dt
from pprint import pprint

import pymongo
import requests
from fake_useragent import UserAgent
from lxml import etree

from db import CLIENT


# Выдергиваем новости и формируем список словарей с новостями
def get_news(collection):
    for val in collection:
        pattern = "//a[contains(@class,'_topnews')]"  # паттерн для поиска блока с новостью
        pattern_date = r"(?:\d+/\d+/\d+)|(?:\d+-\d+-\d+)"  # паттерн для получения даты новости из url
        title = val.xpath(f"{pattern}//text()")  # заголовок новости
        href = val.xpath(f"{pattern}/@href")  # ссылка на новость
        created_at = [re.search(pattern_date, url).group() for url in href]  # дата создания новости
        news_list = [{
            'source': SOURCE,
            'title': t,
            'url': URL + u if u.find('http') else u,
            'created_at': dt.strftime(dt.strptime(d, ['%Y/%m/%d', '%d-%m-%Y']['-' in d]), '%d.%m.%Y')}
            for t, u, d in zip(title[::2], href, created_at)]
    return news_list


if __name__ == '__main__':
    client = pymongo.MongoClient(CLIENT)  # Подключаемся к MongoDB Atlas
    db = client['lenta']  # база данных
    lenta_news = db.lenta_news  # основные новости с сайта hh.ru

    SOURCE = 'Lenta.ru'
    HEADERS = {"User-Agent": UserAgent().chrome}
    URL = 'https://lenta.ru'

    resp = requests.get(URL, headers=HEADERS)
    dom = etree.HTML(resp.text)

    # находим блок с важными новостями
    main_news = dom.xpath("//div[@class='topnews']")

    # получаем список новостей
    top_news = get_news(main_news)

    # записываем данные в базу (MongoDB Atlas)
    lenta_news.insert_many(top_news)

    pprint(top_news)

# [{'_id': ObjectId('621640c4c397e6a2ac91857c'),
#   'created_at': '23.02.2022',
#   'source': 'Lenta.ru',
#   'title': 'Глава Минобороны Британии пригрозил России словами «можем '
#            'повторить»',
#
#   .............
#
#   {'_id': ObjectId('621640c4c397e6a2ac918587'),
#    'created_at': '23.02.2022',
#    'source': 'Lenta.ru',
#    'title': 'Курс рубля снизился',
#    'url': 'https://lenta.ru/news/2022/02/23/rublkurs/'},
#   {'_id': ObjectId('621640c4c397e6a2ac918588'),
#    'created_at': '23.02.2022',
#    'source': 'Lenta.ru',
#    'title': 'Спрогнозирован ответ НАТО на ввод войск России в Донбасс',
#    'url': 'https://lenta.ru/news/2022/02/23/response/'}]


