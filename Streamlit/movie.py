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

            # 【前半部分のclip_3を作成】
            # opening_fileのもとの音声とaudio_clip_1を重ねる
            start_time = 4
            original_audio = opening_file.audio  # 元の音声を取得
            combined_audio = CompositeAudioClip([original_audio, audio_clip_1.set_start(start_time)])
            video_with_audio_1 = opening_file.set_audio(combined_audio)

            # 音声ファイルが終了した時点で、opening_fileをカット
            end_time = min(start_time + audio_clip_1.duration, opening_file.duration)
            clip_3 = video_with_audio_1.subclip(0, end_time)

            # 【後半部分のclip_5を作成】
            # clip_1とclip_2を連結させてclip_4とする
            clip_4 = concatenate_videoclips([clip_1, clip_2])

            # clip_4にaudio_clip_2を付け、音声ファイルが終了した時点でclip_4をカット
            clip_4_with_audio = clip_4.set_audio(audio_clip_2)
            end_time_audio_2 = min(audio_clip_2.duration, clip_4_with_audio.duration)
            clip_5 = clip_4_with_audio.subclip(0, end_time_audio_2)

            # 【完成版の作成】
            # clip_3とclip_5とending_fileを結合してfinal_combined_videoとする
            final_combined_video = concatenate_videoclips([clip_3, clip_5, ending_file])

            file_name = "final_video.mp4"

            # 編集した動画を保存して表示
            final_combined_video.write_videofile(file_name)
            st.video(file_name)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
else:
    st.write("すべてのファイルをアップロードしてください。")
