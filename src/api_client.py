import os
import isodate
from dotenv import load_dotenv
import requests
import urllib.parse

load_dotenv()

API_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = "UC1a2rnuwCw6rEbAxclIHkng"  # @Vedensky
PROXY_WORKER_URL = "https://yt-analytics-proxy.arctiqa-one.workers.dev/"

import time


def _fetch_from_youtube(endpoint, params):
    # Cloudflare прокси
    params["key"] = API_KEY
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    target_url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{query_string}"

    encoded_url = urllib.parse.quote(target_url, safe='')
    proxy_url = f"{PROXY_WORKER_URL}?url={encoded_url}"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(proxy_url, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f" timeout (попытка {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise
            time.sleep(5)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                print(f" Ошибка сервера {e.response.status_code} (попытка {attempt}/{max_retries})")
                if attempt == max_retries:
                    raise
                time.sleep(5)
            else:
                raise


def get_channel_videos():
    channel_data = _fetch_from_youtube("channels", {
        "id": CHANNEL_ID,
        "part": "contentDetails"
    })
    uploads_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page_token = None
    page = 1

    while True:
        print(f"Загрузка страницы {page}...")
        params = {
            "playlistId": uploads_id,
            "part": "contentDetails",
            "maxResults": 50
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        playlist_data = _fetch_from_youtube("playlistItems", params)

        video_ids = [item["contentDetails"]["videoId"] for item in playlist_data["items"]]

        video_data = _fetch_from_youtube("videos", {
            "id": ",".join(video_ids),
            "part": "snippet,statistics,contentDetails"
        })

        for item in video_data["items"]:
            snippet = item["snippet"]
            stats = item["statistics"]
            content = item["contentDetails"]

            # длительность
            duration_iso = content["duration"]
            duration_sec = isodate.parse_duration(duration_iso).total_seconds()

            # теги
            tags = snippet.get("tags", [])
            tags_str = ", ".join(tags) if tags else ""

            videos.append({
                "video_id": item["id"],
                "title": snippet["title"],
                "published_at": snippet["publishedAt"],
                "duration_sec": int(duration_sec),
                "duration_min": round(duration_sec / 60, 2),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "tags": tags_str,
                "description_length": len(snippet.get("description", "")),
                "thumbnail_width": snippet.get("thumbnails", {}).get("maxres", {}).get("width", 0)
            })

        next_page_token = playlist_data.get("nextPageToken")
        if not next_page_token:
            break
        page += 1

    return videos