from pprint import pprint
import pymongo
import requests
from fake_useragent import UserAgent
from lxml import etree
from pymongo.errors import DuplicateKeyError
from db import CLIENT
from datetime import date
import re


# Выдергиваем новости и формируем список словарей с новостями
def get_news(collection):
    news_list = []
    block_news = collection.xpath(".//div[contains(@class, 'mg-grid__col_xs')]")
    for val in block_news:
        url = val.xpath('.//a[@href]/@href')[0]
        news_list.append({
            "_id": re.search(r"(?<=_id=)(?:\d+)", url).group(),
            "source": val.xpath('.//a[@href]/text()')[0],
            "title": val.xpath('.//h2[@class="mg-card__title"]//text()')[0].replace('\xa0', ' '),
            "url": url,
            "created_at": f'''{date.today()} {val.xpath(".//span[@class='mg-card-source__time']/text()")[0]}'''
            }
        )
    return news_list


if __name__ == '__main__':
    client = pymongo.MongoClient(CLIENT)  # Подключаемся к MongoDB Atlas
    db = client['yandex']  # база данных
    yandex_news = db.yandex_news  # основные новости с сайта mail.ru

    HEADERS = {"User-Agent": UserAgent().random}
    URL = 'https://yandex.ru/news'

    resp = requests.get(URL, headers=HEADERS)
    dom = etree.HTML(resp.text)

    # находим блок с важными новостями
    main_news = dom.xpath("//div[contains(@class, 'news-top-flexible-stories')]")

    # получаем список новостей
    top_news = get_news(*main_news)

    # записываем данные в базу (MongoDB Atlas)
    for news in top_news:
        try:
            yandex_news.insert_one(news)
        except DuplicateKeyError:
            print(f'Новость с ID {news["_id"]} уже есть в базе!')

    pprint(top_news)

# [{'_id': '182272030',
#   'created_at': '2022-02-24 19:17',
#   'source': 'Интерфакс',
#   'title': 'Путин заявил о проведении специальной военной операции в связи с '
#            'ситуацией в Донбассе',
#   'url': 'https://yandex.ru/news/story/Putin_zayavil_oprovedenii_specialnoj_voennoj_operacii_vsvyazi_ssituaciej_vDonbasse--71f00e0352fa36fcef38978c3826f3ff?lang=ru&rubric=index&fan=1&stid=aeY-5YW5lBmpaqjwDqsd&t=1645703198&tt=true&persistent_id=182272030&story=18cfcd57-9012-5525-b06a-8b0d3086bfbe'},
#  {'_id': '182290832',
#   'created_at': '2022-02-24 19:41',
#   'source': 'Lenta.ru',
#   'title': 'МИД России заявил, что разрыв отношений с Киевом не был выбором '
#            'Москвы',
#   'url': 'https://yandex.ru/news/story/MID_Rossii_zayavil_chto_razryv_otnoshenij_sKievom_ne_byl_vyborom_Moskvy--c5ab08de26ed5e8a2df03755736020f1?lang=ru&rubric=index&fan=1&stid=6YxbFgm57x4bbAaF0t_g&t=1645703198&tt=true&persistent_id=182290832&story=a664c7fd-4040-5738-a4f0-58657a9522e4'},
#  {'_id': '182292301',
#   'created_at': '2022-02-24 19:47',
#   'source': 'RT на русском',
#   'title': 'Два грузовых судна подверглись ракетному обстрелу ВСУ в Азовском '
#            'море',
#   'url': 'https://yandex.ru/news/story/Dva_gruzovykh_sudna_podverglis_raketnomu_obstrelu_VSU_vAzovskom_more--a362f565d41b8c486153d88b5cf5f446?lang=ru&rubric=index&fan=1&stid=w8GYI_w0vspNz_4BWzcX&t=1645703198&tt=true&persistent_id=182292301&story=78be5872-c3e7-538a-b314-8ad400e2f7f5'},
#  {'_id': '182289305',
#   'created_at': '2022-02-24 19:43',
#   'source': 'РИА Новости',
#   'title': 'Президент Чехии Земан призвал отключить Россию от системы SWIFT',
#   'url': 'https://yandex.ru/news/story/Prezident_CHekhii_Zeman_prizval_otklyuchit_Rossiyu_otsistemy_SWIFT--579e7e8f1da798b95d37d21129b298c7?lang=ru&rubric=index&fan=1&stid=eJ5W2jAcR8i6SxJKYMLx&t=1645703198&tt=true&persistent_id=182289305&story=1e0a6bc9-8bcc-5b92-9542-f43f8bc97d12'},
#  {'_id': '182290838',
#   'created_at': '2022-02-24 19:42',
#   'source': 'RT на русском',
#   'title': 'НАТО намерено развернуть дополнительные оборонительные силы на '
#            'восточном направлении',
#   'url': 'https://yandex.ru/news/story/NATO_namereno_razvernut_dopolnitelnye_oboronitelnye_sily_navostochnom_napravlenii--c4ad3525462db086ec84121a7f0a8ee7?lang=ru&rubric=index&fan=1&stid=HMzIJhzc1a3S0HST1NC-&t=1645703198&tt=true&persistent_id=182290838&story=523d71f3-21db-5731-9d68-fd400f88c2b7'}]

