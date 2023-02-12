import json
import time
from datetime import datetime
import os

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': '*/*'
}


def collect_data() -> str:
    """
    Collect info about photos from API and add it to json-file
    :return: path to json file with collected data
    """
    photos_dict = []
    photo_number = 1
    page_number = 0
    print(f'Start parsing links... ')
    while True:
        start_time = datetime.now()
        url = f'https://unsplash.com/napi/landing_pages/images/stock?page={page_number}&per_page=20'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            break

        for photo in response.json()['photos']:  # collect data to list with dicts

            try:  # check regular size photo link in API
                url_reg = photo['urls']['regular']
            except Exception as ex:
                url_reg = 'None'
                print(ex)

            try:  # check small size photo link in API
                url_small = photo['urls']['small']
            except Exception as ex:
                url_small = 'None'
                print(ex)

            try:  # check full size photo link in API
                url_full = photo['urls']['full']
            except Exception as ex:
                url_full = 'None'
                print(ex)

            photos_dict.append({
                'number': str(photo_number),
                'url-regular': url_reg,
                'url-small': url_small,
                'url-full': url_full
            })
            photo_number += 1

        print(f'Page {page_number + 1} complete! --- Time: {datetime.now() - start_time}')
        page_number += 1
        time.sleep(1)  # rest between requests
    current_time = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):  # Check data dir, if not exists - make it
        os.mkdir(os.path.join(os.getcwd(), 'data'))

    data_json_path = os.path.join(os.getcwd(), 'data', f'{current_time}_content.json')  # Path to json file in data dir

    with open(data_json_path, 'a') as file:  # add collected data to json
        json.dump(photos_dict, file, indent=4, ensure_ascii=False)

    return data_json_path


def download_images(json_path) -> None:
    """
    Download photos and save it to data/images.
    Photo title = photo number
    :return: None
    """
    with open(json_path, 'r') as file:  # exact info from json
        photos_info = json.load(file)
    print(f'Start downloading photos. Count - {len(photos_info)}')

    if not os.path.exists(os.path.join(os.getcwd(), 'data', 'images')):  # Check data dir, if not exists - make it
        os.mkdir(os.path.join(os.getcwd(), 'data', 'images'))

    count = 1
    for photo in photos_info:
        photo_response = requests.get(url=photo['url-regular'],
                                      headers=headers)  # Get photo download link from data dict
        photo_content = photo_response.content

        photo_path = os.path.join(os.getcwd(), 'data', 'images', f'{photo["number"]}.jpg')  # Path to the current photo

        with open(photo_path, 'wb') as file:  # Save photo
            file.write(photo_content)

        print(f'Download {count}/{len(photos_info)}!')
        count += 1
        time.sleep(0.5)  # rest between requests


def main() -> None:
    path_to_data = collect_data()
    download_images(json_path=path_to_data)


if __name__ == '__main__':
    start_collection = datetime.now()
    main()
    print(f'Complete. Time in process: {datetime.now()-start_collection}')
