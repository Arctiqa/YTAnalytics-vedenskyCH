import pandas as pd
import os
from src.api_client import get_channel_videos


def export_to_csv():
    videos = get_channel_videos()
    df = pd.DataFrame(videos)

    df["like_ratio"] = df["likes"] / df["views"]
    df["comment_ratio"] = df["comments"] / df["views"]

    df["published_at"] = pd.to_datetime(df["published_at"])

    os.makedirs("data", exist_ok=True)
    output_path = "data/videos.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nСохранено в {output_path}, количество видео: {len(df)}")


if __name__ == "__main__":
    export_to_csv()