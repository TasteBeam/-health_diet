import random

from time import sleep

import requests
import lxml
from bs4 import BeautifulSoup
import json
import csv
import os

'''
Url Адрес сайта
'''

url = 'https://health-diet.ru/table_calorie'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'}
project_directory = os.getcwd()
folder_name = "data"

if not os.path.exists(os.path.join(project_directory, folder_name)):
    os.mkdir(os.path.join(project_directory, folder_name))

if not os.path.exists(os.path.join(project_directory, 'index.html')):

    req = requests.get(url, headers=headers)
    src = req.text

    with open("index.html", "w", encoding='utf-8') as file:
        file.write(src)
else:
    print('Файл index.html уже существует, продолжаем')

with open('index.html', encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
all_product_hrefs = soup.find_all(class_='mzr-tc-group-item-href')


#Заполняем словарь с категориями
all_categories = {}
for item in all_product_hrefs:
    item_text = item.text
    item_href = "https://health-diet.ru" + item.get('href')

    all_categories[item_text] = item_href


#Создаем json файл на основе словаря
if not os.path.exists(os.path.join(project_directory, 'all_categories.json')): 
    with open("all_categories.json", "w", encoding="utf-8") as file:
        json.dump(all_categories, file, indent=4, ensure_ascii=False)
else:
    print('Файл all_categories.json уже существует, продолжаем')


with open("all_categories.json", encoding="utf-8") as file:
    all_categories = json.load(file)


iteration_count = int(len(all_categories)) - 1
count = 0

print(f'Всего итераций: {iteration_count}')

for category_name, category_href in all_categories.items():

    rep = [",", " ", "-", "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, '_')
    print(category_name)

    if not os.path.exists(os.path.join(project_directory, f'data/{count}_{category_name}.html')):
        req = requests.get(url=category_href, headers=headers)
        src = req.text

        with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
            file.write(src)
    else:
        print('Файл data/{count}_{category_name}.html уже существует, продолжаем')
        
    with open(f"data/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Проверка страницы на наличие
    alert_block = soup.find(class_='uk-alert-danger')
    if alert_block is not None:
        continue

    # Собираем заголовки таблицы

    table_head = soup.find(class_="mzr-tc-group-table").find('tr').find_all('th')
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbs = table_head[4].text




    if not os.path.exists(os.path.join(project_directory, f'data/{count}_{category_name}.csv')):
        with open(f"data/{count}_{category_name}.csv", "w", encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                product,
                calories,
                proteins,
                fats,
                carbs,
            )
        )
    else:
        print('Файл data/{count}_{category_name}.csv уже существует, продолжаем')

    #Собираем данные продуктов

    products_data = soup.find(class_="mzr-tc-group-table").find('tbody').find_all("tr")

    products_info = []
    for item in products_data:
        product_tds = item.find_all('td')

        title = product_tds[0].find('a').text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbs = product_tds[4].text

        products_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbs": carbs
            }
        )


        with open(f"data/{count}_{category_name}.csv", "a", encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbs,
                )
            )

    with open(f"data/{count}_{category_name}.json", "a", encoding='utf-8-sig') as file:
        json.dump(products_info, file, indent=4, ensure_ascii=False)


    count += 1
    print(f"# Итерация {count}. {category_name} записан ...")
    iteration_count -= 1

    if iteration_count == 0:
        print("Работа завершена")
        break

    print(f"Осталось итераций {iteration_count}")
