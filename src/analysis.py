import os
import pandas as pd
import matplotlib.pyplot as plt
from src.api_client import get_channel_info, get_channel_videos

def run_analysis():
    info = get_channel_info()
    print("Канал:", info["title"])
    print("Подписчиков:", info["subscribers"])
    print("Всего видео:", info["video_count"])

    videos = get_channel_videos(max_videos=50)
    df = pd.DataFrame(videos)

    df["like_ratio"] = df["likes"] / df["views"]
    df["comment_ratio"] = df["comments"] / df["views"]

    def duration_group(m):
        if m < 30:
            return "Короткие (<30 мин)"
        elif m <= 60:
            return "Средние (30–60 мин)"
        else:
            return "Длинные (>60 мин)"

    df["duration_group"] = df["duration_min"].apply(duration_group)

    summary = df.groupby("duration_group").agg(
        count=("video_id", "count"),
        avg_views=("views", "mean"),
        avg_like_ratio=("like_ratio", "mean"),
    ).round(2)

    print("\nСредние показатели по группам длительности:")
    print(summary)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/videos.csv", index=False, encoding="utf-8-sig")
    print("\nДанные сохранены в data/videos.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    summary["avg_like_ratio"].plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("Средний like_ratio по длительности видео")
    ax.set_ylabel("Лайки / Просмотры")
    ax.set_xlabel("Группа длительности")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("data/like_ratio_by_duration.png")
    plt.show()

    return df, summary


if __name__ == "__main__":
    run_analysis()