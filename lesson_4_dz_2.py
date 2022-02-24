from pprint import pprint
import pymongo
import requests
from fake_useragent import UserAgent
from lxml import etree
from pymongo.errors import DuplicateKeyError
from db import CLIENT


# Выдергиваем новости и формируем список словарей с новостями
def get_news(collection):
    news_list = []
    href = collection.xpath(".//a[@class='list__text']/@href | .//a[contains(@class,'js-topnews__item')]/@href")
    for url in href:
        r = requests.get(url, headers=HEADERS)
        dom_local = etree.HTML(r.text)
        block_news = dom_local.xpath(".//div[contains(@class, 'article js-article')]")[0]
        news_list.append({
            "_id": url.split('/')[-2],
            "source": block_news.xpath('.//span[@class="link__text"]/text()')[0],
            "title": block_news.xpath('.//span[@class="hdr__text"]//text()')[0],
            "url": url,
            "created_at": dom_local.xpath(".//span[@datetime]/@datetime")[0][:10]
            }
        )
    return news_list


if __name__ == '__main__':
    client = pymongo.MongoClient(CLIENT)  # Подключаемся к MongoDB Atlas
    db = client['mail']  # база данных
    mail_news = db.mail_news  # основные новости с сайта mail.ru

    HEADERS = {"User-Agent": UserAgent().chrome}
    URL = 'https://news.mail.ru'

    resp = requests.get(URL, headers=HEADERS)
    dom = etree.HTML(resp.text)

    # находим блок с важными новостями
    main_news = dom.xpath("//div[contains(@class, 'daynews js-topnews')]/..")

    # получаем список новостей
    top_news = get_news(*main_news)

    # записываем данные в базу (MongoDB Atlas)
    for news in top_news:
        try:
            mail_news.insert_one(news)
        except DuplicateKeyError:
            print(f'Новость с ID {news["_id"]} уже есть в базе!')

    pprint(top_news)

# [{'_id': '50182295',
#   'created_at': '2022-02-24',
#   'source': 'Коммерсантъ',
#   'title': 'Путин поручил начать спецоперацию в Донбассе',
#   'url': 'https://news.mail.ru/politics/50182295/'},
#  {'_id': '50182611',
#   'created_at': '2022-02-24',
#   'source': 'Коммерсантъ',
#   'title': 'Онлайн-трансляция: Путин объявил о вводе войск в Донбасс',
#   'url': 'https://news.mail.ru/politics/50182611/'},
#  ............
#  {'_id': '50183872',
#   'created_at': '2022-02-24',
#   'source': 'ТАСС',
#   'title': 'Шольц назвал действия России «вопиющим нарушением международного '
#            'права»',
#   'url': 'https://news.mail.ru/politics/50183872/'}]


