from pprint import pprint
import requests
from datetime import datetime
from progress.bar import ChargingBar
import logging

VK_TOKEN = 'a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd'

class YaUploader:

    def __init__(self, token: str):
        self.token = 'AQAAAAAAspNaAADLW8ptMO51lU-Ko0Ze0qWmaB4'
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_dir(self, path: str):
        params = {'path': path}
        res = requests.put(self.url, params=params, headers=self.headers)

    def upload_file(self, url_file: str, path: str):
        params = {'path': path, 'url': url_file}
        res = requests.post(self.url + '/upload', params=params, headers=self.headers)
        if res.status_code != 202:
            print(res.status_code)
        else:
            print(requests.get(res.json()['href'], headers=self.headers).json()['status'])


if __name__ == '__main__':
# owner_id = input('введите имя')
    owner_id = '552934290'
    params = { 'owner_id': owner_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1', 'access_token': VK_TOKEN, 'v': '5.131' }
    response = requests.get( 'https://api.vk.com/method/photos.get', params=params)
    # pprint(response.json())
    # count_photos = response.json()['response']['count']
    yaUploader = YaUploader(token)
    yaUploader.create_dir(f'/Profile_{owner_id}')
    json_photos = []
    for picture in response.json()['response']['items']:
        # pprint(f"{picture['date']}   {picture['likes']['count']}  {picture['likes']['user_likes']} {picture['post_id']}")
        file_name = str(int(picture['likes']['count']) + int(picture['likes']['user_likes'])) +  '.jpg'
        for name in json_photos:
            if file_name == name['file_name']:
                file_name = file_name.rstrip('.jpg') + picture['data'] + '.jpg'
        # print(file_name)
        max_size = 0
        for pic in picture['sizes']:
            if pic['height'] * pic['width'] > max_size:
                max_size = pic['height'] * pic['width']
                url_big_pic = pic['url']
                type_size = pic['type']
        # print(datetime.utcfromtimestamp(picture['date']).date())
        json_photos.append({'file_name': file_name, 'size': type_size, 'url': url_big_pic, 'date': str(datetime.utcfromtimestamp(picture['date']).date()), 'post_id': picture['post_id']})
    # pprint(json_photos)
    bar = ChargingBar('Loading', max=len(json_photos))
    for photos in json_photos:
        bar.next()
        # file = requests.get(photos['url'])
        yaUploader.upload_file(photos['url'], f"Profile_{owner_id}/{photos['file_name']}")
    bar.finish()




