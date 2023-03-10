# -*- coding: utf-8 -*-
# @File    : step_3_delete_similar_images.py
# @Author  : Robin Lan
# @Time    : 4/2/23 00:53
# @Software: PyCharm
# @Description: This script is used to delete similar images.

import os
import hashlib
import re
import shutil
import time
import imagehash
from PIL import Image
import pandas as pd

image_path = "./image"
remove_path = "./remove_image"


def delete_similar_images():
    remove_list = remove_to_folder_by_md5()
    print(f'duplicate images by md5 are {len(remove_list)} in total,'
          f'here is the remove list:'
          f' {remove_list}')
    cnt = add_suffix(image_path)
    print(f'Finished add suffix process, the count is {cnt}')
    calculate_image_hash()
    print(f'Finished calculate images\' hash')
    check_hash_file()
    print("Finish checking")
    calculate_similarity(threshold=0.87)
    simi_remove_to_folder()


def remove_to_folder_by_md5():
    os.makedirs(remove_path, exist_ok=True)

    all_file = []
    md5_dict = {}
    remove_list = []

    for filepath, dir, filelist in os.walk(image_path):
        for filename in filelist:
            all_file.append(os.path.join(filepath, filename))

    for image in all_file:
        md5 = get_md5(image)
        if md5 is None:
            continue
        if md5 not in md5_dict:
            md5_dict[md5] = image
        else:
            remove_list.append(image)

    remove_image(remove_list)

    return remove_list


def calculate_image_hash(highfreq_factor=4, hash_size=32, image_scale=64):
    hash_data = {
        'list_file': [],
        'list_phash': [],
        'list_ahash': [],
        'list_dhash': [],
        'list_whash': []
    }

    image_files = [f for f in os.listdir(image_path) if os.path.splitext(f)[1] in ['.jpg', '.png', '.gif', '.webp']]
    image_files_path = [os.path.join(image_path, f) for f in image_files]
    images = []
    tmp = 0
    for i in range(len(image_files_path)):
        try:
            images.append(Image.open(image_files_path[i]))
        except Exception:
            if os.path.exists(os.path.join(remove_path, image_files[i - tmp])):
                os.remove(os.path.join(remove_path, image_files[i]))
                tmp += 1
            shutil.move(image_files_path[i - tmp], remove_path)
            del image_files[i - tmp]
            del image_files_path[i - tmp]

    phash = [imagehash.phash(img, hash_size=hash_size, highfreq_factor=highfreq_factor) for img in images]
    ahash = [imagehash.average_hash(img, hash_size=hash_size) for img in images]
    dhash = [imagehash.dhash(img, hash_size=hash_size) for img in images]
    whash = [imagehash.whash(img, image_scale=image_scale, hash_size=hash_size, mode='db4') for img in images]

    hash_data['list_file'] = image_files
    hash_data['list_phash'] = phash
    hash_data['list_ahash'] = ahash
    hash_data['list_dhash'] = dhash
    hash_data['list_whash'] = whash

    hash_file = pd.DataFrame(hash_data)
    hash_file.to_csv('./data/hash_file.csv', encoding='utf-8', index=False, header=True)


def calculate_similarity(threshold):
    similarity_data = []
    hash_file = pd.read_csv('./data/hash_file.csv', encoding='utf-8')

    for i in range(len(hash_file) - 1):
        print(f"This is the #{i} image")
        print(time.strftime('The current time is: %Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        for j in range(i + 1, len(hash_file)):
            phash_value = calculate_image_similarity(hash_file.at[i, 'list_phash'], hash_file.at[j, 'list_phash'])
            ahash_value = calculate_image_similarity(hash_file.at[i, 'list_ahash'], hash_file.at[j, 'list_ahash'])
            dhash_value = calculate_image_similarity(hash_file.at[i, 'list_dhash'], hash_file.at[j, 'list_dhash'])
            whash_value = calculate_image_similarity(hash_file.at[i, 'list_whash'], hash_file.at[j, 'list_whash'])
            value_hash = max(phash_value, ahash_value, dhash_value, whash_value)
            if value_hash >= threshold:
                size_i = os.path.getsize(os.path.join(image_path, hash_file.at[i, 'list_file']))
                size_j = os.path.getsize(os.path.join(image_path, hash_file.at[j, 'list_file']))
                if size_i > size_j:
                    larger_file = (hash_file.at[i, 'list_file'], size_i)
                    smaller_file = (hash_file.at[j, 'list_file'], size_j)
                else:
                    larger_file = (hash_file.at[j, 'list_file'], size_j)
                    smaller_file = (hash_file.at[i, 'list_file'], size_i)
                similarity_data.append([larger_file[0], larger_file[1] / 1024,
                                        smaller_file[0], smaller_file[1] / 1024, value_hash])
    similarity = pd.DataFrame(similarity_data,
                              columns=['similar_list_large', 'similar_list_large_size', 'similar_list_small',
                                       'similar_list_small_size', 'similar_list_similarity'])
    similarity.to_csv('./data/simi_pic.csv', encoding='utf-8', index=False, header=True)


def simi_remove_to_folder():
    simi_pic = pd.read_csv('./data/simi_pic.csv', encoding='utf-8')

    small_pics = simi_pic['similar_list_small'].tolist()
    large_pics = simi_pic['similar_list_large'].tolist()
    small_pics_paths = [os.path.join(image_path, pic) for pic in small_pics]
    large_pics_paths = [os.path.join(image_path, pic) for pic in large_pics]
    remove_paths_small = [os.path.join(remove_path, pic) for pic in small_pics]
    remove_paths_large = [os.path.join(remove_path, pic) for pic in large_pics]

    for small_pic_path, large_pic_path, remove_path_small, \
        remove_path_large in zip(small_pics_paths,
                                 large_pics_paths, remove_paths_small, remove_paths_large):
        if os.path.isfile(small_pic_path):
            if os.path.isfile(remove_path_small):
                if os.path.isfile(remove_path_large):
                    continue
                else:
                    shutil.move(large_pic_path, remove_path)
            else:
                shutil.move(small_pic_path, remove_path)


def hamming_distance(hash1, hash2):
    distance = 0
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]:
            distance += 1
    return distance


def calculate_image_similarity(hash1, hash2):
    hash_length = len(hash1)
    distance = hamming_distance(hash1, hash2)
    return 1 - distance / hash_length


def get_md5(file):
    try:
        with open(file, 'rb') as open_file:
            md5 = hashlib.sha256()
            md5.update(open_file.read())
            return md5.hexdigest()  # 16,Hexadecimal
    except FileNotFoundError:
        print(f'File {file} not found')
        return
    except Exception as e:
        print(f'An error occurred while processing the file {file}: {e}')
        return


def remove_image(remove_list: list[str]):
    for i in range(len(remove_list)):
        print(remove_list[i])
        pattern = re.compile(r'.*\/(.*)')
        tmp = re.findall(pattern, remove_list[i])[0]
        if os.path.isfile(os.path.join(remove_path, tmp)):
            os.remove(os.path.join(remove_path, tmp))
        shutil.move(remove_list[i], remove_path)


def check_hash_file():
    hash_file = pd.read_csv('./data/hash_file.csv', encoding='utf-8')
    for i in range(len(hash_file)):
        if os.path.isfile(os.path.join(image_path, hash_file['list_file'][i])):
            continue
        else:
            hash_file = hash_file[hash_file.list_file != hash_file['list_file'][i]]
    hash_file.to_csv('./data/hash_file.csv', encoding='utf-8', index=False, header=True)


def add_suffix(folder_path):
    cnt = 0
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and '.' not in filename:
            new_file_path = file_path + '.gif'
            os.rename(file_path, new_file_path)
            cnt += 1
    return cnt
