import os
import streamlit as st
from pytube import YouTube
import re

# YouTube Data APIキー
API_KEY = st.secrets[YOUTUBE_API_KEY]

# スクリプトのディレクトリを取得
current_dir = os.path.dirname(__file__)

# 日本語フォントのパスを指定 (NotoSansCJKjp-Regular.otf などの日本語フォントファイル)
font_path = os.path.join(current_dir, 'SOURCEHANSANSJP-BOLD.OTF')

#ページコンフィグ
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

# 動画情報を保持するリスト
videos = []

# 動画のURLを入力するセクション
st.title("YouTube動画リスト管理アプリ")
video_url = st.text_input("YouTube動画のURLを入力してください")

# YouTubeの動画IDを抽出する関数（改良版）
def get_video_id(url):
    # 標準的なyoutube.comやyoutu.beのURL形式に対応
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

# 動画を追加
if st.button("動画を追加"):
    video_id = get_video_id(video_url)
    if video_id:
        video_info = get_video_info(video_id)
        if video_info:
            title = video_info["snippet"]["title"]
            duration = video_info["contentDetails"]["duration"]
            videos.append({
                "title": title,
                "url": video_url,
                "duration": duration
            })
            st.success(f"動画 '{title}' がリストに追加されました。")
        else:
            st.error("動画情報の取得に失敗しました。")
    else:
        st.error("無効なYouTube URLです。")

# 動画リストの表示
if videos:
    st.subheader("追加された動画リスト")
    for idx, video in enumerate(videos):
        st.write(f"{idx + 1}. {video['title']} | {video['url']}")
        # 削除ボタン
        if st.button(f"削除 {video['title']}", key=f"delete-{idx}"):
            videos.pop(idx)
            st.experimental_rerun()

    # 並び替え機能を実装（ドラッグアンドドロップなど）

    # 概要欄を生成
    if st.button("開始"):
        st.subheader("生成された概要欄")
        total_time = 0
        for idx, video in enumerate(videos):
            minutes, seconds = divmod(total_time, 60)
            start_time = f"{minutes}:{seconds:02d}"
            st.write(f"{start_time} | {video['title']}\n{video['url']}")
            total_time += video['duration']
