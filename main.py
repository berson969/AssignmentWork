from pprint import pprint
from wsgiref import headers
import requests
from datetime import datetime
from progress.bar import ChargingBar

VK_TOKEN = 'a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd'
YA_TOKEN = 'AQAAAAAAspNaAADLW8ptMO51lU-Ko0Ze0qWmaB4'
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
HEADERS = {'Content-Type': 'application/json', 'Authorization': f'OAuth {YA_TOKEN}'}

def create_dir(path: str):
    # res = requests.put(URL, path, headers=HEADERS)
    res = requests.put(f"{URL}?path={path}", headers=HEADERS)
    # print(res.status_code)


def upload_file_to_yadisk(file_url: str, path_name: str):
    # print(f"{URL}/upload?url={file_url}&path={path_name}")
    # print(path_name)
    params = {'path': path_name, 'overwrite': True, 'fields': 'href'}
    res = requests.post( f"{URL}/upload?url={file_url}&path=disk:{path_name}", headers=HEADERS)
    # upload_link = res.json()['href']
    # print(file_url)
    print(len(file_url))

    print(requests.get(res.json()['href'], headers=HEADERS).json()['status'])
    # response = requests.get(upload_link, params=params, headers=HEADERS)    
    # pprint(response.json())
    if res.status_code != 202:
        print(res.status_code)
    


if __name__ == '__main__':
# owner_id = input('введите имя')
    owner_id = '552934290'
    params = { 'owner_id': owner_id, 'album_id': 'profile', 'extended': '1', 'photo_size': '1', 'access_token': VK_TOKEN, 'v': '5.131' }
    response = requests.get( 'https://api.vk.com/method/photos.get', params=params)
    # pprint(response.json())
    # count_photos = response.json()['response']['count']
    create_dir(f'/Profile_{owner_id}')
    json_photos = []
    for picture in response.json()['response']['items']:
        # pprint(f"{picture['date']}   {picture['likes']['count']}  {picture['likes']['user_likes']} {picture['post_id']}")
        file_name = str(int(picture['likes']['count']) + int(picture['likes']['user_likes'])) +  '.jpg'
        # print(file_name)
        max_size = 0
        for pic in picture['sizes']:
            if pic['height'] * pic['width'] > max_size:
                max_size = pic['height'] * pic['width']
                url_big_pic = pic['url']

        # print(datetime.utcfromtimestamp(picture['date']).date())
        json_photos.append({'file_name': file_name, 'size': max_size, 'url': url_big_pic, 'date': str(datetime.utcfromtimestamp(picture['date']).date()), 'post_id': picture['post_id']})
    # pprint(json_photos)
    bar = ChargingBar('Loading', max=len(json_photos))
    for photos in json_photos:
        bar.next()
        # file = requests.get(photos['url'])
        upload_file_to_yadisk(photos['url'], f"/Profile_{owner_id}/{photos['file_name']}")
    bar.finish()




