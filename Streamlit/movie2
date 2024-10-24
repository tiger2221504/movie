import os
import streamlit as st
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, ImageClip
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

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

if st.button("動画を追加"):
    try:
        yt = YouTube(video_url)
        videos.append({
            "title": yt.title,
            "url": video_url,
            "duration": yt.length
        })
        st.success(f"動画 '{yt.title}' がリストに追加されました。")
    except Exception as e:
        st.error("URLが無効です。正しいYouTube URLを入力してください。")

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
