# -*- coding: utf-8 -*-
# @File    : step_1_fetch_unique_image_links.py
# @Author  : Robin Lan
# @Time    : 2/2/23
# @Software: PyCharm

import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import numpy as np


def fetch_unique_image_links(headers, url, start_page, end_page):
    image = []
    time_cnt = 0
    save_name = f"./data/image_links{start_page}-{end_page}.csv"

    for i in range(start_page, end_page + 1):
        new_url = url + '&page=' + str(i)
        response = requests.get(new_url, headers=headers)
        response.encoding = 'gbk'
        response = response.text
        soup = BeautifulSoup(response, 'html5lib')
        table_node = soup.find_all('table')

        for table in table_node:
            img_url = table.img.get('src') if table.img else ''
            if not img_url or img_url[0] == '/':
                continue
            image.append(img_url)
        if not image:
            continue

        save_data = pd.DataFrame(columns=['img'], data=image)

        save_data.drop_duplicates(subset='img', keep='first', inplace=True)

        os.makedirs('./data', exist_ok=True)

        save_data.to_csv(save_name, encoding='utf-8', index=False, header=True)

        sleep_time = np.random.randint(10, 20)
        time.sleep(sleep_time)
        time_cnt += sleep_time

        print(time.strftime('Now：%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print('The script slept for {b} seconds and crawled to page {a}. Total time used is {c} seconds.'.format(
            a=i, b=sleep_time, c=time_cnt))

    return save_name
