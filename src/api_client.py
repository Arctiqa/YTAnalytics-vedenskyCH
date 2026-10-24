import os
import isodate
from dotenv import load_dotenv
import requests
import urllib.parse

load_dotenv()

API_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = "UC1a2rnuwCw6rEbAxclIHkng"  # @Vedensky

PROXY_WORKER_URL = "https://yt-analytics-proxy.arctiqa-one.workers.dev/"


def _fetch_from_youtube(endpoint, params):
    """Отправляет запрос к YouTube API через Cloudflare прокси."""
    # Добавляем ключ к параметрам
    params["key"] = API_KEY

    # Собираем параметры в строку формата: key=value&key2=value2
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])

    # Формируем URL к YouTube
    target_url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{query_string}"

    # Кодируем URL и отправляем на наш прокси
    encoded_url = urllib.parse.quote(target_url, safe='')
    proxy_url = f"{PROXY_WORKER_URL}?url={encoded_url}"

    resp = requests.get(proxy_url)
    resp.raise_for_status()
    return resp.json()


def get_channel_info():
    """Возвращает базовую информацию о канале."""
    data = _fetch_from_youtube("channels", {
        "id": CHANNEL_ID,
        "part": "snippet,statistics"
    })
    item = data["items"][0]
    return {
        "title": item["snippet"]["title"],
        "subscribers": int(item["statistics"]["subscriberCount"]),
        "total_views": int(item["statistics"]["viewCount"]),
        "video_count": int(item["statistics"]["videoCount"]),
    }


def get_channel_videos(max_videos=50):
    """Возвращает список видео канала с метриками."""
    # 1. Получаем uploads-плейлист
    channel_data = _fetch_from_youtube("channels", {
        "id": CHANNEL_ID,
        "part": "contentDetails"
    })
    uploads_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page_token = None

    # 2. Получаем видео из плейлиста
    while len(videos) < max_videos:
        params = {
            "playlistId": uploads_id,
            "part": "contentDetails",
            "maxResults": min(50, max_videos - len(videos))
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        playlist_data = _fetch_from_youtube("playlistItems", params)

        video_ids = [item["contentDetails"]["videoId"] for item in playlist_data["items"]]

        # 3. Запрашиваем статистику по каждому видео
        video_data = _fetch_from_youtube("videos", {
            "id": ",".join(video_ids),
            "part": "snippet,statistics,contentDetails"
        })

        for item in video_data["items"]:
            duration_iso = item["contentDetails"]["duration"]
            duration_min = isodate.parse_duration(duration_iso).total_seconds() / 60

            videos.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "duration_min": round(duration_min, 1),
            })

        next_page_token = playlist_data.get("nextPageToken")
        if not next_page_token:
            break

    return videos
