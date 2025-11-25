import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv('./.env')
YOUR_API_KEY = os.getenv('YOUR_API_KEY')
CHANNEL_HANDLE = 'MrBeast'
maxResults = 50

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
        # print(channel_playlist_Id)
        return channel_playlist_Id
    except requests.exceptions.RequestException as e:
        raise e


def get_video_id(playlist_id):
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_id}&key={YOUR_API_KEY}'
    video_ids = []
    pageToken = None
    
    try:
        while True:
            url = base_url
            if pageToken:
                url += f'&pageToken={pageToken}'
            
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            for videoItem in data.get('items', []):
                video_ids.append(videoItem['contentDetails']['videoId'])

            pageToken = data.get('nextPageToken')
            if not pageToken:
                break
        return video_ids
    except requests.exceptions.RequestException as e:
        raise e


def extract_video_data(video_ids):
    extracted_data = []
    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id : video_id + batch_size]
    
    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ','.join(batch)

            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={video_ids_str}&key={YOUR_API_KEY}'

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):   
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {'video_id' : video_id ,
                'title' : item['snippet']['title'],
                'publishedAt' : snippet['publishedAt'],
                'duration' : contentDetails['duration'],
                'viewCount' : statistics.get('viewCount', None),
                'likeCount' : statistics.get('likeCount', None),
                'comments' : statistics.get('commentCount', None),
                }

                extracted_data.append(video_data)
        return extracted_data
    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):
    file_path = f'./data/YT_data_{date.today()}.json'
    with open(file_path, mode='w', encoding='utf-8') as json_outfile:
        json.dump(extracted_data, json_outfile, indent = 4, ensure_ascii = False)

if __name__ == '__main__':
    playlist_id = get_playlist_id()
    video_id_list = get_video_id(playlist_id)
    video_data = extract_video_data(video_id_list)
    save_to_json(video_data)
