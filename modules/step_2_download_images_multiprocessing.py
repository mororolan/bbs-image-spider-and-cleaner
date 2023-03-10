# -*- coding: utf-8 -*-
# @File    : step_2_download_images_multiprocessing.py
# @Author  : Robin Lan
# @Time    : 3/2/23 17:08
# @Software: PyCharm
# @Description: This script is used to download images from a csv file.

import signal
import urllib
import pandas as pd
import os
import logging
import multiprocessing

def handler(signum, frame):
    raise Exception("The request took too long.")

def download_image(img_url, index, fail_img):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)
    try:
        response = urllib.request.urlopen(img_url)
        with open(f"./image/{index}.jpg", "wb") as f:
            f.write(response.read())
        signal.alarm(0)
        logging.info(f'Image {index} has been downloaded successfully')
        print(f'Image {index} has been downloaded successfully')
    except:
        signal.alarm(0)
        logging.error(f'Failed to download image {index} from {img_url}')
        fail_img.append(img_url)


def download_images(filename):
    logging.basicConfig(filename='./data/download_images.log', level=logging.INFO, format='%(asctime)s %(message)s')

    os.makedirs('./image', exist_ok=True)

    data = pd.read_csv(filename)

    fail_img = []

    processes = []
    max_processes = 7
    for index, row in data.iterrows():
        if len(processes) == max_processes:
            for process in processes:
                process.join()
            processes = []
        process = multiprocessing.Process(target=download_image, args=(row['img'], index, fail_img))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    if fail_img:
        fail_file = pd.DataFrame(fail_img, columns=['img'])
        fail_file.to_csv('./data/fail_img.csv', mode='a', index=False, header=False)
