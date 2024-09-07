import os
import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import tempfile

# スクリプトのディレクトリを取得
current_dir = os.path.dirname(__file__)

# タイトル
st.title('動画編集アプリ')

# 事前に指定する最初と最後の動画を読み込む
opening_video_path = os.path.join(current_dir, 'opening.mp4')
predefined_video = VideoFileClip(opening_video_path)
ending_video_path = os.path.join(current_dir, 'ending.mp4')
final_video = VideoFileClip(ending_video_path)

# 音声ファイルと動画ファイルをアップロード
audio_file_1 = st.file_uploader("1つ目の音声ファイルをアップロードしてください", type=["mp3", "wav"])
audio_file_2 = st.file_uploader("2つ目の音声ファイルをアップロードしてください", type=["mp3", "wav"])
video_file_1 = st.file_uploader("1つ目の動画ファイルをアップロードしてください", type=["mp4", "mov", "avi"])
video_file_2 = st.file_uploader("2つ目の動画ファイルをアップロードしてください", type=["mp4", "mov", "avi"])


# アップロードされたファイルが全て存在するかチェック
if audio_file_1 and audio_file_2 and video_file_1 and video_file_2:
    
    try:
        # 一時ファイルを作成してアップロードされたファイルを保存
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_1, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_audio_2, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_video_1, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_video_2:
            
            # ファイルを保存
            tmp_audio_1.write(audio_file_1.read())
            tmp_audio_2.write(audio_file_2.read())
            tmp_video_1.write(video_file_1.read())
            tmp_video_2.write(video_file_2.read())

            # 音声ファイルを読み込む
            audio_clip_1 = AudioFileClip(tmp_audio_1.name)
            audio_clip_2 = AudioFileClip(tmp_audio_2.name)
            
            # 動画ファイルを読み込む
            clip_1 = VideoFileClip(tmp_video_1.name)
            clip_2 = VideoFileClip(tmp_video_2.name)
            
             # 動画の長さを取得
            video_duration = predefined_video.duration
            start_time = 4
            
            # 音声1が終了した後に、動画の長さを超えないようにする
            end_time = min(start_time + audio_clip_1.duration, video_duration)  # 動画の長さを超えないように制限
            
            # 音声を動画にセット
            video_with_audio_1 = predefined_video.set_audio(audio_clip_1.set_start(start_time))

            # 音声1が終了した後に、アップロードされた1つ目の動画に切り替え
            video_with_audio_1_cut = video_with_audio_1.subclip(0, start_time + audio_clip_1.duration)
            
            # 1つ目の動画終了後に、2つ目の動画に切り替え
            final_combined_video = concatenate_videoclips([
                video_with_audio_1_cut,  # 最初の動画の一部＋音声1
                clip_1,  # 1つ目のアップロードされた動画
                clip_2,  # 2つ目のアップロードされた動画
                final_video  # 最後に再生する事前指定動画
            ])

            file_name = "final_video"

            # 編集した動画を保存して表示
            final_combined_video.write_videofile(file_name + ".mp4")
            st.video(file_name + ".mp4")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
