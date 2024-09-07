import os
import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import tempfile

# スクリプトのディレクトリを取得
current_dir = os.path.dirname(__file__)

# タイトル
st.title('動画編集アプリ')

# 事前に指定する最初と最後の動画を読み込む
opening_video_path = os.path.join(current_dir, 'opening.mp4')
opening_file = VideoFileClip(opening_video_path)
ending_video_path = os.path.join(current_dir, 'ending.mp4')
ending_file = VideoFileClip(ending_video_path)

# 音声ファイルと動画ファイルをアップロード
audio_file_1 = st.file_uploader("1つ目の音声ファイルをアップロードしてください", type=["mp3", "wav"])
audio_file_2 = st.file_uploader("2つ目の音声ファイルをアップロードしてください", type=["mp3", "wav"])
video_file_1 = st.file_uploader("1つ目の動画ファイルをアップロードしてください", type=["mp4", "mov", "avi"])
video_file_2 = st.file_uploader("2つ目の動画ファイルをアップロードしてください", type=["mp4", "mov", "avi"])

# アップロードされたファイルが全て存在するかチェック
if audio_file_1 and audio_file_2 and video_file_1 and video_file_2:
    try:
        # 一時ファイルを作成してアップロードされたファイルを保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio_1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio_2, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video_1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video_2:
            
            # ファイルを保存
            tmp_audio_1.write(audio_file_1.read())
            tmp_audio_2.write(audio_file_2.read())
            tmp_video_1.write(video_file_1.read())
            tmp_video_2.write(video_file_2.read())

            # 一時ファイルから読み込み
            audio_clip_1 = AudioFileClip(tmp_audio_1.name)
            audio_clip_2 = AudioFileClip(tmp_audio_2.name)
            clip_1 = VideoFileClip(tmp_video_1.name)
            clip_2 = VideoFileClip(tmp_video_2.name)

            # 1つ目と2つ目のアップロードされた動画を連結して clip_3 を作成
            clip_3 = concatenate_videoclips([clip_1, clip_2])

            # 動画の長さを取得
            video_duration = opening_file.duration
            start_time = 4  # 最初の動画の再生時間の途中で音声1を再生（スタートから4秒後に再生開始）

            # 音声1を4秒後にセットし、動画を音声と同期
            # CompositeAudioClipを使って音声を4秒後にセットする
            new_audio = CompositeAudioClip([audio_clip_1.set_start(start_time)])
            video_with_audio_1 = opening_file.set_audio(new_audio)

            # 音声1の終了後に、最初の動画をカット
            end_time = min(start_time + audio_clip_1.duration, video_duration)
            video_with_audio_1_cut = video_with_audio_1.subclip(0, end_time)

            # 最初の動画の後に clip_3 を連結
            video_combined_with_clip_3 = concatenate_videoclips([video_with_audio_1_cut, clip_3])

            # clip_3 の再生開始と同時に、2つ目の音声ファイルを再生開始
            video_with_audio_2 = video_combined_with_clip_3.set_audio(audio_clip_2)

            # 2つ目の音声の終了後に clip_3 をカット
            end_time_audio_2 = min(audio_clip_2.duration, video_with_audio_2.duration)
            video_with_audio_2_cut = video_with_audio_2.subclip(0, end_time_audio_2)

            # 最後に事前指定の動画を連結
            final_combined_video = concatenate_videoclips([
                video_with_audio_2_cut,  # 最初の動画＋clip_3
                ending_file  # 最後に再生する事前指定動画
            ])

            file_name = "final_video.mp4"

            # 編集した動画を保存して表示
            final_combined_video.write_videofile(file_name)
            st.video(file_name)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
else:
    st.write("すべてのファイルをアップロードしてください。")
