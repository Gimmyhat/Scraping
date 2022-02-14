import time
from math import ceil
import fake_useragent
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# Находим номер последней страницы с вакансиями
def get_last_page():
    resp = requests.get(f'{url}&page={0}', headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')
    paginator = soup.find('div', {'class': 'pager'})  # находим блок пагинации
    return [int(page.find('a').text) for page in paginator if page.find('a')][-1]


# разбиваем текст с данными по зарплате на минимальную и максимальную + тип валюты
def get_salary(text):
    if text:
        s = text.text.strip().replace('\u202f', '').replace('–', '').split()
        for i in range(len(s)):
            s_min = int(s[0]) if s[0].isdigit() else ['-', int(s[1])][s[0] == 'от']
            s_max = int(s[1]) if s[1].isdigit() else ['-', int(s[1])][s[0] == 'до']
            currency = s[-1]
        return s_min, s_max, currency
    return ['-'] * 3


# создаем список вакансий по указанному запросу
def get_jobs(pages):
    vacancy_list = []
    trigger = 0  # ограничивает количество поиска согласно заданному FIND_ITEMS
    for page in tqdm(range(pages)):  # tqdm библиотека для отображения индикатора прогресса
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
                 'site': 'HH.ru'
                 }
            )
            trigger += 1
            # прекращает парсинг, достигнув требуемого количества вакансий (согласно FIND_ITEMS)
            if trigger == FIND_ITEMS:
                break
        time.sleep(1)
    return vacancy_list


if __name__ == '__main__':
    FIND_TEXT = 'Django'  # критерий поиска
    FIND_ITEMS = 70  # сколько вакансий искать (если 0, то все совпадения)
    ITEMS_ON_PAGE = 20
    AREA = 113
    SITE = 'HH.ru'
    ORDER_BY = 'publication_time'
    BASE_URL = 'https://hh.ru/search/vacancy'
    HEADERS = {
        "User-Agent": fake_useragent.UserAgent().chrome,
        "Connection": "keep-alive"
    }
    url = f'{BASE_URL}?area={AREA}&items_on_page={ITEMS_ON_PAGE}&order_by={ORDER_BY}&text={FIND_TEXT}'

    last_page = get_last_page()
    pages = last_page if FIND_ITEMS == 0 else ceil(FIND_ITEMS / ITEMS_ON_PAGE)
    df = pd.DataFrame(get_jobs(pages))
    df.to_excel(f'./hh_{FIND_ITEMS}.xlsx')
