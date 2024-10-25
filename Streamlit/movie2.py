import os
import streamlit as st
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from yt_dlp import YoutubeDL
import re
import requests
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips

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

# ISO 8601の期間をtimedeltaに変換する関数
def convert_duration(iso_duration):
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

# 動画をDLする関数
def download_video(url, filename="temp_video.mp4"):
    ydl_opts = {
        'format': 'best[height<=720]',  # 720p以下の最高画質を取得
        'outtmpl': filename,
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info




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
                duration = video_info["contentDetails"]["duration"]
                delta_duration = convert_duration(duration)
                published_at = video_info["snippet"]["publishedAt"]
                formatted_date = format_date(published_at)  # 日付を読みやすい形式に変換
                st.session_state.videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "duration": delta_duration,
                    "published_date": formatted_date
                })
        st.success("再生リストの動画がすべて追加されました。")
    
    else:
        # 単一動画の処理
        video_id = get_video_id(video_url)
        if video_id:
            video_info = get_video_info(video_id)
            if video_info:
                title = video_info["snippet"]["title"]
                duration = video_info["contentDetails"]["duration"]
                delta_duration = convert_duration(duration)
                published_at = video_info["snippet"]["publishedAt"]
                formatted_date = format_date(published_at)  # 日付を読みやすい形式に変換
                st.session_state.videos.append({
                    "title": title,
                    "url": video_url,
                    "duration": delta_duration,
                    "published_date": formatted_date
                })
                st.success(f"'{title}' ({delta_duration}) がリストに追加されました。")
            else:
                st.error("動画情報の取得に失敗しました。")
        else:
            st.error("無効なYouTube URLです。")

# 動画リストの表示と削除機能
if st.session_state.videos:
    st.subheader("追加された動画リスト")
    for idx, video in enumerate(st.session_state.videos):
        st.write(f"{idx + 1}. {video['title']} ({video['duration']}) | {video['url']}")
        if st.button(f"{idx + 1}を削除", key=f"delete-{idx}"):
            st.session_state.videos.pop(idx)
            # 再描画を強制
            st.experimental_set_query_params()


   # 生成開始
    if st.button("作成開始"):
        # 概要欄文章の生成
        description_text = ""
        cumulative_time = timedelta()
        for video in st.session_state.videos:
            description_text += f"{str(cumulative_time)} | {video['title']} \n{video['url']}\n\n"
            cumulative_time += video["duration"]
        
        st.subheader("YouTube概要欄")


        st.text_area("概要欄の内容", description_text, height=300)
        # JavaScriptを使ってクリップボードにコピーするボタンを作成
        copy_button = """
        <button onclick="copyText()">クリップボードにコピー</button>
        <p id="copy-message" style="color:green; display:none;">☑コピーしました</p>

        <script>
        function copyText() {
            navigator.clipboard.writeText(document.getElementById('text-area').value).then(function() {
                document.getElementById('copy-message').style.display = 'block';
                setTimeout(function() {
                    document.getElementById('copy-message').style.display = 'none';
                }, 2000);  // 2秒間表示
            });
        }
        </script>
        """
        # ボタンとテキストエリアをID付きで表示
        st.components.v1.html(
            f"""
            <textarea id="text-area" style="display:none;">{description_text}</textarea>
            {copy_button}
            """,
            height=100,
        )



        # まとめ動画の作成
        st.subheader("動画の出力")
        clips = []
        progress_bar = st.progress(0)  # プログレスバーの初期値
        for video in st.session_state.videos:
            try:
                # 動画をYouTubeからダウンロード
                info = download_video(video["url"], filename="temp_video.mp4")
                title = info.get("title", "Untitled")
                published_date = datetime.strptime(info["upload_date"], "%Y%m%d").strftime("%Y/%m/%d")
                
                # 動画クリップを1280x720にリサイズ
                clip = VideoFileClip("temp_video.mp4").resize((1280, 720))
                
                # 公開日をテキストクリップとして生成し、動画の左上に配置
                text = TextClip(
                    video["published_date"],
                    fontsize=90,
                    color="white",
                    font="Arial"
                ).set_position(("left", 10)).set_duration(clip.duration)
                
                # テキストクリップと動画クリップを重ねる
                clip = clip.set_duration(clip.duration)
                composite = VideoFileClip("temp_video.mp4").resize((1280, 720))
                composite = composite.set_duration(clip.duration).set_position("center")
                combined = concatenate_videoclips([clip, composite])
                
                # クリップをリストに追加
                clips.append(combined)

            except VideoUnavailable:
                st.warning(f"{video['title']}はダウンロードできません。スキップします。")
            except Exception as e:
                st.warning(f"{video['title']}の処理中にエラーが発生しました: \n{e}")
            
            finally:
                if os.path.exists("temp_video.mp4"):
                    # 一時ファイルを削除
                    os.remove("temp_video.mp4")

            progress_bar.progress(int(100/(len(st.session_state.videos)+1)))  # プログレスバーを更新
        
        # すべての動画クリップを結合
        if clips:
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile("summary_video.mp4", codec="libx264")
            progress_bar.progress(100)  # プログレスバーを更新
            st.video("summary_video.mp4")
        else:
            progress_bar.progress(100)  # プログレスバーを更新
            st.error("利用可能な動画がありませんでした。")
        

        
        
