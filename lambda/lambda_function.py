import json
import requests
import boto3


ssm = boto3.client('ssm', region_name='us-west-2')

def get_parameter(name):
   parameter = ssm.get_parameter(
       Name=name,
       WithDecryption=True
   )
  
   return parameter['Parameter']['Value']


BASE_YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3'
BASE_NOTION_URL = 'https://api.notion.com/v1'
NOTION_API_KEY = get_parameter('/yt_notion_lambda/notion_api_key')
YOUTUBE_API_KEY = get_parameter('/yt_notion_lambda/youtube_api_key')
NOTION_DB_ID = get_parameter('/yt_notion_lambda/notion_db_id')

NOTION_HEADERS = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",  # Use the latest version supported at your time
        "Content-Type": "application/json",
    }

def get_youtube_id_to_notion_page_map():
    url = f"{BASE_NOTION_URL}/databases/{NOTION_DB_ID}/query"
    yt_to_page_map = {}
    data = {
        "page_size": 100
    }
    has_next_page = True
    while has_next_page:
        response = requests.post(url, json=data, headers=NOTION_HEADERS)
        if response.status_code == 200:
            response_json = response.json()
            has_next_page = bool(response_json.get("has_more"))
            if has_next_page:
                data["start_cursor"] = response_json.get("next_cursor")
            for page in response_json.get("results", []):
                page_id = page.get("id")
                yt_id = page.get("properties", {}).get("YT ID", {}).get("formula", {}).get("string", None)
                yt_to_page_map[yt_id] = page_id
        else:
            raise Exception("Failed to retrieve Notion DB. " + response.text)

    return yt_to_page_map


def get_video_details(video_ids):
    videos_statistics = []
    # YouTube API allows up to 50 IDs in a single request
    max_ids_per_request = 50

    # Split video IDs into chunks of 50
    video_id_chunks = [video_ids[i:i + max_ids_per_request] for i in range(0, len(video_ids), max_ids_per_request)]

    for chunk in video_id_chunks:
        ids = ','.join(chunk)
        url = f"{BASE_YOUTUBE_URL}/videos?key={YOUTUBE_API_KEY}&id={ids}&part=snippet,statistics"
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json().get('items', [])
            for item in items:
                videos_statistics.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0))
                })
    return videos_statistics


def update_notion_db_entry(page_id, comments, likes, views, title):
    url = f"{BASE_NOTION_URL}/pages/{page_id}"
    data = {
        "properties": {
            'Comments': {
                "number": comments,
            },
            'Likes': {
                "number": likes,
            },
            'Views': {
                "number": views,
            },
            'Video Title': {
                "title": [{
                    "text": {
                        "content": title
                    }
                }],
            },
        },
    }
    requests.patch(url, headers=NOTION_HEADERS, data=json.dumps(data))


def lambda_handler(event, context):
    yt_ids_to_notion_pages_map = get_youtube_id_to_notion_page_map()
    yt_details = get_video_details(list(yt_ids_to_notion_pages_map.keys()))
    for detail in yt_details:
        update_notion_db_entry(
            yt_ids_to_notion_pages_map[detail['id']],
            detail['comments'],
            detail['likes'],
            detail['views'],
            detail['title']
        )