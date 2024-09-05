import streamlit as st
import yt_dlp
import subprocess
import os

# Function to download YouTube audio
@st.cache_data
def download_audio(url: str) -> str:
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
        return f'{audio_file}.mp3'

# Function to transcribe audio
def transcribe(audio_file: str) -> str:
    folder = 'data'
    transcription_file = f'{folder}/{audio_file}.txt'

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
    # Streamlit app
    st.title("YouTube Audio Downloader and Transcript Generator")

    # Input field for YouTube URL
    url = st.text_input("Enter YouTube URL:")

    # Button to download the audio
    if st.button("Download Audio") and url:
        st.session_state.audio_file = download_audio(url)
        st.audio(st.session_state.audio_file)
        st.success("Audio downloaded successfully!")

    # Button to generate transcript
    if 'audio_file' in st.session_state:
        if st.button("Generate Transcript"):
            st.session_state.transcription_text = transcribe(st.session_state.audio_file)
            if st.session_state.transcription_text != "Transcription failed or audio not found.":
                st.success("Transcription successful!")

                # Delete audio file
                os.remove(st.session_state.audio_file)

            else:
                st.error(st.session_state.transcription_text)

    # Display the transcription if available
    if 'transcription_text' in st.session_state and st.session_state.transcription_text:
        st.text_area("Transcript", st.session_state.transcription_text, height=300)
        st.download_button(
            label="Download Transcript",
            data=st.session_state.transcription_text,
            file_name='transcription.txt',
            mime='text/plain'
        )

if __name__ == "__main__":
    main()
