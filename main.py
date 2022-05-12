from pprint import pprint
import requests
import datetime
from progress.bar import ChargingBar
import os
from  GoogleDriveUploader import  GDriveUp, upload_to_googleDrive
# from my_logging import My_logging

class YaUploader:

    def __init__(self, token):
        self.token = token
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_dir(self, path: str):
        params = {'path': path}
        res = requests.put(self.url, params=params, headers=self.headers)

    def upload_file(self, url_file: str, path: str):
        params = {'path': path, 'url': url_file, 'disable_redirects': True}
        res = requests.post(self.url + '/upload', params=params, headers=self.headers)
        if res.status_code != 202:
            print(res.status_code)
        # else:
            # print(requests.get(res.json()['href'], headers=self.headers).json()['status'])
            # поставить логгер!!!

def upload_to_yadisk(token: str, folder_name: str, json_photos: list):
    yaUploader = YaUploader(token)
    yaUploader.create_dir(folder_name)
    bar = ChargingBar('Loading to YaDisk ', max=len(json_photos))
    for photos in json_photos:
        bar.next()
        # file = requests.get(photos['url'])
        yaUploader.upload_file(photos['url'], f"{folder_name}/{photos['file_name']}")
    bar.finish()

def vk_get_photos (token: str, owner_id: str, album_name: str, count):
    params = {'owner_id': owner_id, 'album_id': album_name, 'extended': '1', 'photo_size': '1', 'access_token': token, 'v': '5.131'}
    response = requests.get( 'https://api.vk.com/method/photos.get', params=params)
    # pprint(response.json())
    if response.json().get('error'):
        # сюда поставить логгер!!!!!!!!!
        return response.json()['error']['error_msg']
    json_photos = []
    for picture in response.json()['response']['items']:
        date_fromutc = datetime.datetime.fromtimestamp(int(picture['date'])).strftime('%Y_%m_%d')
        file_name = str(int(picture['likes']['count']) + int(picture['likes']['user_likes'])) +  '.jpg'
        for name in json_photos:
            if file_name == name['file_name']: 
                file_name = file_name.rstrip('.jpg') + '_' + date_fromutc + '.jpg'         
        # print(file_name)
        max_size = 0
        # max[x * y for x, y in picture['sizes']]
        for pic in picture['sizes']:
            if pic['height'] * pic['width'] > max_size:
                max_size = pic['height'] * pic['width']
        # print(datetime.utcfromtimestamp(picture['date']).date())
        json_photos.append({'file_name': file_name, 'size': pic['type'], 'url': pic['url'], 'date': date_fromutc})
        if len(json_photos) == count:
            return json_photos 
    return json_photos


if __name__ == '__main__':
    PATH_FILE = os.path.join(os.getcwd(),'input.txt')
    print(PATH_FILE)
    with open(PATH_FILE) as f:
        txt = f.readlines()
        owner_id = txt[1].strip('\n')
        album_name = txt[3].strip('\n')
        count = int(txt[5])
        VK_TOKEN = txt[7].strip('\n')
        YA_TOKEN = txt[9].strip('\n')
    folder_name = f'{album_name.capitalize()}_{owner_id}'
    json_photos = vk_get_photos(VK_TOKEN, owner_id, album_name, count)
    # pprint(json_photos)
    # print(folder_name)
    if type(json_photos) is str:
        print(json_photos)
    else:
        upload_to_yadisk(YA_TOKEN, folder_name, json_photos )
        upload_to_googleDrive(folder_name, json_photos)
  

