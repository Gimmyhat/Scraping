import time
from math import ceil
import fake_useragent
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re


# Находим номер последней страницы с вакансиями
def get_last_page():
    resp = requests.get(f'{url}&page={0}', headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')
    # находим информацию по результату поиска ('Найдено XXXX вакансий')
    vacancy_all = soup.find('div', {'class': '_2G0xv _8kBN3 _2Jaon _2X1PV'}).text
    # преобразуем результат в число и находим количество страниц с результатом запроса
    return ceil(int(re.search(r'\d+', vacancy_all).group()) // ITEMS_ON_PAGE)


# разбиваем текст с данными по зарплате на минимальную и максимальную + тип валюты
def get_salary(text):
    s = re.sub(r'\s', '', text.text.strip())
    s_min, s_max, currency = '-',  '-', 'руб'
    pattern = r"\d+"
    if re.search(pattern, s):
        num = re.findall(pattern, s)
        if len(num) == 1:
            if 'от' in s or 'до' in s:
                s_min = ['-', int(num[0])]['от' in s]
                s_max = ['-', int(num[0])]['до' in s]
            else:
                s_min, s_max = [int(num[0])] * 2
        elif len(num) == 2:
            s_min = int(num[0])
            s_max = int(num[1])
    return s_min, s_max, currency


# создаем список вакансий по указанному запросу
def get_jobs(max_page):
    vacancy_list = []
    trigger = 0  # ограничивает количество поиска согласно заданному FIND_ITEMS
    for page in tqdm(range(1, max_page)):  # tqdm библиотека для отображения индикатора прогресса
        resp = requests.get(f'{url}&page={page}', headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        # находим отдельные блоки с вакансиями и выдергиваем нужные данные
        results = soup.find_all('div', {'class': 'jNMYr GPKTZ _1tH7S'})
        for res in results:
            salary = get_salary(res.find('span', {'class': '_1OuF_ _1qw9T f-test-text-company-item-salary'}))
            vacancy_list.append(
                {'title': res.find('a').text,
                 'url': f"{BASE_URL}{res.find('a')['href']}",
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


if __name__ == '__main__':
    FIND_TEXT = 'python'  # критерий поиска
    FIND_ITEMS = 100  # сколько вакансий искать (если 0, то все совпадения)
    SITE = 'SuperJob.ru'
    ORDER_BY = 'updated_at'
    ITEMS_ON_PAGE = 20
    BASE_URL = 'https://russia.superjob.ru'
    HEADERS = {
        "User-Agent": fake_useragent.UserAgent().chrome,
        "Connection": "keep-alive"
    }
    url = f'{BASE_URL}/vacancy/search/?keywords={FIND_TEXT}&order_by%5B{ORDER_BY}%5D=desc'

    last_page = get_last_page()
    pages = last_page + 1 if FIND_ITEMS == 0 else ceil(FIND_ITEMS / ITEMS_ON_PAGE) + 1
    df = pd.DataFrame(get_jobs(pages))
    df.to_excel(f'./sj_{FIND_ITEMS}.xlsx')
