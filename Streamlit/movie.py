import os
import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, ImageClip
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

# スクリプトのディレクトリを取得
current_dir = os.path.dirname(__file__)

# 日本語フォントのパスを指定 (NotoSansCJKjp-Regular.otf などの日本語フォントファイル)
font_path = os.path.join(current_dir, 'SOURCEHANSANSJP-BOLD.OTF')

# タイトル
st.title('ヒグマ速報作成アプリ')

# 地名の入力
text = st.text_input("地名を入力してください", value="")

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

if st.button("決定して動画を作成"):
    progress_bar = st.progress(0)  # プログレスバーの初期値
    
    # アップロードされたファイルが全て存在するかチェック
    if audio_file_1 and audio_file_2 and video_file_1 and video_file_2:
        try:
            progress_bar.progress(10)  # プログレスバーを更新
            
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

                progress_bar.progress(25)  # プログレスバーを更新
    
                # 一時ファイルから読み込み
                audio_clip_1 = AudioFileClip(tmp_audio_1.name)
                audio_clip_2 = AudioFileClip(tmp_audio_2.name)
                clip_1 = VideoFileClip(tmp_video_1.name)
                clip_2 = VideoFileClip(tmp_video_2.name)
    
                # 【前半部分のclip_3を作成】
                # opening_fileのもとの音声とaudio_clip_1を重ねる
                start_time = 4
                original_audio = opening_file.audio  # 元の音声を取得
                combined_audio = CompositeAudioClip([original_audio, audio_clip_1.set_start(start_time)])
                video_with_audio_1 = opening_file.set_audio(combined_audio)

                progress_bar.progress(40)  # プログレスバーを更新
    
                # 音声ファイルが終了した時点で、opening_fileをカット
                end_time = min(start_time + audio_clip_1.duration + 1, opening_file.duration)
                clip_3 = video_with_audio_1.subclip(0, end_time)
    
                # 【1つ目の動画の最後のフレームを取得して2秒間の静止画を作成】
                last_frame_time = clip_1.duration  # 1つ目の動画の最後のフレームの時間
                last_frame = clip_1.get_frame(last_frame_time - 0.04)  # 最後のコマを取得（微調整）
    
                # PILを使って静止画像にテキストを描画
                image = Image.fromarray(last_frame)
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype(font_path, 90)  # フォントサイズ90
                text_bbox = draw.textbbox((0, 0), text, font=font)  # テキストのバウンディングボックスを取得
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]  # 幅と高さを計算
    
                # 右上にテキストを配置（X座標は右端に、Y座標は少し余裕を持たせて上から10ピクセルの位置）
                text_position = (image.width - text_width - 10, 10)
    
                # 黒い縁取りを追加（8方向に黒いテキストを描画）
                offset = 4  # 縁取りの幅
                for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset), (-offset, -offset), (offset, offset), (-offset, offset), (offset, -offset)]:
                    draw.text((text_position[0] + dx, text_position[1] + dy), text, font=font, fill="black")
    
                # 白いテキストを描画
                draw.text(text_position, text, font=font, fill="white")
    
                
                # PILの画像をnumpy配列に変換し、ImageClipに変換して5秒間の静止画を作成
                image_np = np.array(image)  # PIL画像をnumpy配列に変換
                image_clip = ImageClip(image_np).set_duration(5)

                progress_bar.progress(60)  # プログレスバーを更新
    
                # 【後半部分のclip_5を作成】
                # clip_1とclip_2の間に2秒間のテキスト付き静止画像を挿入し、clip_4とする
                clip_4 = concatenate_videoclips([clip_1, image_clip, clip_2])
    
                # clip_4にaudio_clip_2を付け、音声ファイルが終了した時点でclip_4をカット
                clip_4_with_audio = clip_4.set_audio(audio_clip_2)
                end_time_audio_2 = min(audio_clip_2.duration, clip_4_with_audio.duration)
                clip_5 = clip_4_with_audio.subclip(0, end_time_audio_2)
    
                # 【完成版の作成】
                # clip_3とclip_5とending_fileを結合してfinal_combined_videoとする
                final_combined_video = concatenate_videoclips([clip_3, clip_5, ending_file])
    
                file_name = "final_video.mp4"

                progress_bar.progress(70)  # プログレスバーを更新
    
                # 編集した動画を保存して表示
                final_combined_video.write_videofile(file_name)

                progress_bar.progress(100)  # プログレスバーを更新
                st.video(file_name)
    
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
    else:
        st.write("すべてのファイルをアップロードしてください。")
