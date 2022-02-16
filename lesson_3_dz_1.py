import re
import time
from math import ceil
import fake_useragent
import pymongo
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from db import db_client
import datetime
from pycbrf.toolbox import ExchangeRates


# Находим номер последней страницы с вакансиями
def get_last_page():
    try:
        resp = requests.get(f'{url}&page={0}', headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        paginator = soup.find('div', {'class': 'pager'})  # находим блок пагинации
        return [int(page.find('a').text) for page in paginator if page.find('a')][-1]
    except:
        return 1


# разбиваем текст с данными по зарплате на минимальную и максимальную + тип валюты
def get_salary(text):
    s_min, s_max, currency = None, None, None
    if text:
        s = text.text.strip().replace('\u202f', '').replace('–', '').split()
        for i in range(len(s)):
            s_min = int(s[0]) if s[0].isdigit() else [None, int(s[1])][s[0] == 'от']
            s_max = int(s[1]) if s[1].isdigit() else [None, int(s[1])][s[0] == 'до']
            currency = s[-1]
    return s_min, s_max, currency


# создаем список вакансий по указанному запросу
def get_jobs(all_pages):
    vacancy_list = []
    trigger = 0  # ограничивает количество поиска согласно заданному FIND_ITEMS
    for page in tqdm(range(all_pages)):  # tqdm библиотека для отображения индикатора прогресса
        resp = requests.get(f'{url}&page={page}', headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        # находим отдельные блоки с вакансиями и выдергиваем нужные данные
        results = soup.find_all('div', {'class': 'vacancy-serp-item'})
        for res in results:
            salary = get_salary(res.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}))
            vacancy_list.append(
                {'title': res.find('a').text,
                 'url': res.find('a')['href'],
                 'salary min': salary[0],
                 'salary max': salary[1],
                 'currency': salary[2],
                 'site': SITE
                 }
            )
            trigger += 1
            # прекращает парсинг, достигнув требуемого количества вакансий (согласно FIND_ITEMS)
            if trigger == FIND_ITEMS:
                break
        time.sleep(1)
    return vacancy_list


# добавляем вакансии в базу и проверяем на уникальность (если есть в базе, то пропускаем)
def insert_job_db(collection, data, id_):
    duplicates = collection.find_one(id_)
    if not duplicates:
        data['_id'] = id_
        return collection.insert_one(data)


if __name__ == '__main__':

    client = pymongo.MongoClient(db_client)  # Подключаемся к MongoDB Atlas
    db = client['jobs']  # база данных
    hh_jobs = db.hh_jobs  # вакансии с сайта hh.ru

    FIND_TEXT = input('Введите наименование вакансии: ')  # критерий поиска
    FIND_ITEMS = int(input('Введите максимальное количество для поиска (0 - будут найдены все вакансии): '))
    SALARY = int(input('Введите минимальный размер зарплаты в рублях: '))
    ITEMS_ON_PAGE = 20
    AREA = 113
    SITE = 'HH.ru'
    ORDER_BY = 'publication_time'
    BASE_URL = 'https://hh.ru/search/vacancy'
    HEADERS = {"User-Agent": fake_useragent.UserAgent().chrome}
    url = f'{BASE_URL}?area={AREA}&items_on_page={ITEMS_ON_PAGE}&order_by={ORDER_BY}&text={FIND_TEXT}'

    # находим все страницы по запросу
    last_page = get_last_page()
    pages = last_page if FIND_ITEMS == 0 else ceil(FIND_ITEMS / ITEMS_ON_PAGE)

    # собираем вакансии согласно запросу
    jobs = get_jobs(pages)

    # регулярка для выдергивания из URL уникального номера вакансии
    pattern = r'(?<=b=)(?:\d+)(?=\&)|(?<=/)(?:\d+)'

    # записываем данные в базу (MongoDB Atlas)
    for job in jobs:
        id_db = re.search(pattern, job['url'])
        insert_job_db(hh_jobs, job, id_db.group())

    # получаем текущие курсы ЦБРФ
    dt_now = datetime.datetime.now()
    rates = ExchangeRates(dt_now)
    r_usd = rates['USD'].value
    r_eur = rates['EUR'].value

    # выводим на экран только вакансии с зарплатой выше, указанной в запросе
    # (USD и EUR конвертируется по текущему курсу ЦБ)
    df = pd.DataFrame(hh_jobs.find(
        {'$or':
            [{'currency': 'руб.', '$or':
                [{'salary min': {'$gt': SALARY}}, {'salar max': {'$gt': SALARY}}]},
            {'currency': 'USD', '$or':
                [{'salary min': {'$gt': int(SALARY/r_usd)}}, {'salar max': {'$gt': int(SALARY/r_usd)}}]},
            {'currency': 'EUR', '$or':
                [{'salary min': {'$gt': int(SALARY/r_eur)}}, {'salar max': {'$gt': int(SALARY/r_eur)}}]}
            ]
        }
    ))
    print(df.to_string(max_rows=10, max_colwidth=40, max_cols=8))
