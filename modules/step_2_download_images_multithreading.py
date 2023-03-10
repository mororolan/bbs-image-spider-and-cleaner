# -*- coding: utf-8 -*-
# @File    : step_2_download_images_multithreading.py
# @Author  : Robin Lan
# @Time    : 3/2/23 13:10
# @Software: PyCharm
# @Description: This script is used to download images from a csv file.

import urllib
import pandas as pd
import os
import logging
import threading


def download_image(img_url, index, fail_img):
    try:
        response = urllib.request.urlopen(img_url)
        with open(f"./image/{index}.jpg", "wb") as f:
            f.write(response.read())
        logging.info(f'Image {index} has been downloaded successfully')
    except:
        logging.error(f'Failed to download image {index} from {img_url}')
        fail_img.append(img_url)


def download_images(filename):
    logging.basicConfig(filename='download_images.log', level=logging.INFO, format='%(asctime)s %(message)s')

    os.makedirs('./image', exist_ok=True)

    data = pd.read_csv(filename)

    fail_img = []

    threads = []
    max_threads = 7
    for index, row in data.iterrows():
        if len(threads) == max_threads:
            for thread in threads:
                thread.join()
            threads = []
        thread = threading.Thread(target=download_image, args=(row['img'], index, fail_img))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if fail_img:
        fail_file = pd.DataFrame(fail_img, columns=['img'])
        fail_file.to_csv('./data/fail_img.csv', mode='a', index=False, header=False)
