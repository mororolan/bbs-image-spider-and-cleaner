# -*- coding: utf-8 -*-
# @File    : main.py
# @Author  : Robin Lan
# @Time    : 1/2/23
# @Software: PyCharm

from modules.step_1_fetch_unique_image_links import fetch_unique_image_links
from modules.step_2_download_images_multiprocessing import download_images
from modules.step_3_delete_similar_images import delete_similar_images

headers = {
    'Cookie': ''}

url = ''

image = []
if __name__ == '__main__':

    # step 1

    save_file = fetch_unique_image_links(headers, url, 707, 708)
    print("Finished step 1")

    # step 2

    download_images(save_file)
    print("Finished step 2")

    # step 3

    delete_similar_images()


