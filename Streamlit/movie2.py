import os
import streamlit as st
from pytube import YouTube
import re
import requests
from datetime import datetime, timedelta

# YouTube Data APIキー
API_KEY = st.secrets["YOUTUBE_API_KEY"]

# ページコンフィグ
st.set_page_config(
     page_title="まとめ動画作成アプリ",
     page_icon="📡",
     initial_sidebar_state="collapsed",
     menu_items={
         'About': """
         # まとめ動画作成アプリ
         動画を作れます
         @ 2024 yamazumi
         """
     }
)

# タイトル
st.title('まとめ動画作成アプリ')

# session_stateに動画リストと入力欄の値がなければ初期化
if "videos" not in st.session_state:
    st.session_state.videos = []

# YouTubeの動画IDを抽出する関数
def get_video_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

# 再生リストIDを抽出する関数
def get_playlist_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/playlist\?list=)([a-zA-Z0-9_-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

# 動画情報を取得する関数
def get_video_info(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["items"][0]
    else:
        return None

# 再生リストの動画IDをすべて取得する関数
def get_playlist_video_ids(playlist_id):
    video_ids = []
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={API_KEY}"
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            video_ids.extend([item["contentDetails"]["videoId"] for item in data["items"]])
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&pageToken={data.get('nextPageToken')}&playlistId={playlist_id}&maxResults=50&key={API_KEY}" if "nextPageToken" in data else None
        else:
            st.error("再生リストの動画情報の取得に失敗しました。")
            break
    return video_ids

# ISO 8601の期間を時:分:秒に変換する関数
def parse_duration(iso_duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, iso_duration)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

# 日付フォーマットを変換する関数
def format_date(iso_date):
    date_obj = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    return date_obj.strftime("%Y/%m/%d")

# 動画のURLを入力するセクション
video_url = st.text_input("YouTube動画または再生リストのURLを入力してください")

# 動画を追加
if st.button("動画を追加"):
    # 再生リストIDをチェック
    playlist_id = get_playlist_id(video_url)
    if playlist_id:
        # 再生リストの動画IDリストを取得
        video_ids = get_playlist_video_ids(playlist_id)
        for video_id in video_ids:
            video_info = get_video_info(video_id)
            if video_info:
                title = video_info["snippet"]["title"]
                duration = parse_duration(video_info["contentDetails"]["duration"])
                publish_date = format_date(video_info["snippet"].get("publishedAt", "1970-01-01T00:00:00Z"))
                st.session_state.videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "duration": duration,
                    "publish_date": publish_date
                })
        st.success("再生リストの動画がすべて追加されました。")
    
    else:
        # 単一動画の処理
        video_id = get_video_id(video_url)
        if video_id:
            video_info = get_video_info(video_id)
            if video_info:
                title = video_info["snippet"]["title"]
                duration = parse_duration(video_info["contentDetails"]["duration"])
                publish_date = format_date(video_info["snippet"].get("publishedAt", "1970-01-01T00:00:00Z"))
                st.session_state.videos.append({
                    "title": title,
                    "url": video_url,
                    "duration": duration,
                    "publish_date": publish_date
                })
                st.success(f"'{title}' がリストに追加されました。")
            else:
                st.error("動画情報の取得に失敗しました。")
        else:
            st.error("無効なYouTube URLです。")

# 動画リストの表示と削除機能
if st.session_state.videos:
    st.subheader("追加された動画リスト")
    for idx, video in enumerate(st.session_state.videos):
        st.write(f"{idx + 1}. {video['title']} | {str(video['duration'])} | {video['url']}")
        if st.button(f"{idx + 1}を削除", key=f"delete-{idx}"):
            st.session_state.videos.pop(idx)
            st.experimental_rerun()

    # YouTube概要欄生成機能
    if st.button("作成開始"):
        description_text = ""
        total_duration = timedelta()  # 累積再生時間
        for video in st.session_state.videos:
            description_text += f"{str(total_duration)} | {video['title']} \n{video['url']}\n\n"
            total_duration += video['duration']
        
        st.subheader("生成されたYouTube概要欄")
        st.text_area("概要欄の内容", description_text, height=300)  # コピー可能
