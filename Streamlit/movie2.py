import os
import streamlit as st
from pytube import YouTube
import re
import requests

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
if "video_url" not in st.session_state:
    st.session_state.video_url = ""

# YouTubeの動画IDを抽出する関数
def get_video_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
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

# ISO 8601の期間を時:分:秒に変換する関数
def convert_duration(iso_duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, iso_duration)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return f"{hours}:{minutes:02}:{seconds:02}"

# 動画のURLを入力するセクション
st.text_input("YouTube動画のURLを入力してください", key="video_url")

# 動画を追加
if st.button("動画を追加"):
    video_id = get_video_id(st.session_state.video_url)
    if video_id:
        video_info = get_video_info(video_id)
        if video_info:
            title = video_info["snippet"]["title"]
            duration = video_info["contentDetails"]["duration"]
            readable_duration = convert_duration(duration)
            st.session_state.videos.append({
                "title": title,
                "url": st.session_state.video_url,
                "duration": readable_duration
            })
            st.success(f"'{title}' ({readable_duration}) がリストに追加されました。")
            # 入力欄をクリア
            st.session_state.video_url = ""  # 動画追加後に入力欄をクリア
        else:
            st.error("動画情報の取得に失敗しました。")
    else:
        st.error("無効なYouTube URLです。")

# 動画リストの表示と削除・順序変更機能
if st.session_state.videos:
    st.subheader("追加された動画リスト")
    for idx, video in enumerate(st.session_state.videos):
        st.write(f"{idx + 1}. {video['title']} | {video['duration']} | {video['url']}")
        if st.button(f"{idx + 1}を削除", key=f"delete-{idx}"):
            st.session_state.videos.pop(idx)
            st.experimental_rerun()
