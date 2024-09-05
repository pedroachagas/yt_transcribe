import streamlit as st
import yt_dlp
import subprocess
import os
from streamlit_lottie import st_lottie
import requests
import time

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Function to download YouTube audio
@st.cache_data(show_spinner=False)
def download_audio(url: str) -> str:
    audio_file = 'downloaded_audio'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{audio_file}''.%(ext)s',
        'geo_verification_proxy': '128.106.14.228',
        # ' 'vU --'downloader aria2c -N 10
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Download the audio using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return f'{audio_file}.mp3'

# Function to transcribe audio
def transcribe(audio_file: str) -> str:
    folder = 'data'
    transcription_file = f'{folder}/{audio_file.split(".")[0]}.txt'

    if os.path.exists(audio_file):
        # Transcribe using Whisper CLI
        print("Transcribing audio...")
        subprocess.run(
            ['whisper', audio_file, '-o', folder],
            text=True
        )

        # Read the transcription file
        if os.path.exists(transcription_file):
            with open(transcription_file, 'r') as f:
                transcription_text = f.read()
            return transcription_text
    return "Transcription failed or audio not found."

def main():
    # Page config
    st.set_page_config(page_title="YT Audio Transcriber", page_icon="🎵", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    # Streamlit app
    st.title("🎵 YouTube Audio Transcriber")
    st.write("Download audio from YouTube videos and generate transcripts with ease!")

    # Sidebar
    st.sidebar.header("About")
    with st.sidebar:

        # Instructions
        st.subheader("How to use:")
        st.markdown("""
        1. Paste a YouTube URL in the input field
        2. Click "Download Audio" to fetch the audio
        3. Click "Generate Transcript" to create a transcript
        4. Download the transcript or copy it from the text area
        """)

    # Input field for YouTube URL
    url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

    # Button to download the audio
    if st.button("🔊 Download Audio", key="download_button"):
        if url:
            with st.spinner("Downloading audio..."):
                st.session_state.audio_file = download_audio(url)
            st.success("Audio downloaded successfully!")
        else:
            st.warning("Please enter a valid YouTube URL.")

    # Show the audio file path
    if 'audio_file' in st.session_state:
        st.audio(st.session_state.audio_file, format='audio/mp3')

    # Button to generate transcript
    if 'audio_file' in st.session_state:
        if st.button("📝 Generate Transcript", key="transcript_button"):
            with st.spinner("Generating transcript... This may take a few minutes."):
                st.session_state.transcription_text = transcribe(st.session_state.audio_file)
            if st.session_state.transcription_text != "Transcription failed or audio not found.":
                st.success("Transcription successful!")
            else:
                st.error(st.session_state.transcription_text)

    # Display the transcription if available
    if 'transcription_text' in st.session_state and st.session_state.transcription_text:
        st.subheader("Transcript")
        st.text_area("", st.session_state.transcription_text, height=300)
        st.download_button(
            label="📥 Download Transcript",
            data=st.session_state.transcription_text,
            file_name='transcription.txt',
            mime='text/plain'
        )

if __name__ == "__main__":
    main()