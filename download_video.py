import streamlit as st
import yt_dlp
import subprocess
import os

# Function to download YouTube audio and generate a transcript
@st.cache_data
def download_and_transcribe(url: str) -> str:
    audio_file = 'downloaded_audio'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{audio_file}''.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Download the audio using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    folder = 'data'
    transcription_file = f'{folder}/{audio_file}.mp3.txt'

    if os.path.exists('downloaded_audio.mp3'):
        # Transcribe using Whisper CLI
        subprocess.run(
            ['whisper', 'downloaded_audio.mp3', '--model', 'base', '--output', folder],
            capture_output=True,
            text=True
        )

        # Read the transcription file
        if os.path.exists(transcription_file):
            with open(transcription_file, 'r') as f:
                transcription_text = f.read()
            return transcription_text
    return "Transcription failed or audio not found."

# Streamlit app
st.title("YouTube Transcript Generator")

# Input field for YouTube URL
url = st.text_input("Enter YouTube URL:")

# Button to generate transcript
if st.button("Generate Transcript") and url:
    st.session_state.transcription_text = download_and_transcribe(url)
    if st.session_state.transcription_text != "Transcription failed or audio not found.":
        st.success("Transcription successful!")
    else:
        st.error(st.session_state.transcription_text)

# Display the transcription
if 'transcription_text' in st.session_state and st.session_state.transcription_text:
    st.text_area("Transcript", st.session_state.transcription_text, height=300)
    st.download_button(
        label="Download Transcript",
        data=st.session_state.transcription_text,
        file_name='transcription.txt',
        mime='text/plain'
    )