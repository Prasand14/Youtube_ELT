import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('./.env')
YOUR_API_KEY = os.getenv('YOUR_API_KEY')
CHANNEL_HANDLE = 'MrBeast'

def get_playlist_id():
    url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={YOUR_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        # print(response)

        data = response.json()
        # print(json.dumps(data, indent=4))

        channel_items = data['items'][0]
        channel_playlist_Id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlist_Id)
        return channel_playlist_Id
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == '__main__':
    get_playlist_id()