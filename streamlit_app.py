import os
import tempfile
import streamlit as st
from model import transcribe_video_to_text, download_youtube_audio_to_temp


# Page title
st.title('🤖 Kết quả của bạn')

with st.expander('Xem kết quả'):
    # Display the transcription
    if transcription:
        st.subheader("Transcription")
        st.text(transcription)
  



# Sidebar for accepting input parameters
with st.sidebar:
    # Load data
    st.header('Kiểm tra video của bạn')
    
    # Add radio buttons for the selection method
    selection_method = st.radio(
        "Chọn phương thức tải lên video:",
        ('Upload local video file', 'Enter YouTube video URL')
    )
    
    uploaded_local_file = None
    uploaded_file = None

    if selection_method == 'Upload local video file':
        uploaded_local_file = st.file_uploader("Đăng tải lên video")
    
    if selection_method == 'Enter YouTube video URL':
        uploaded_file = st.text_input("Nhập URL video youtube")

# Initialize transcription variable
transcription = ""

if selection_method == 'Upload local video file' and uploaded_local_file is not None:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp:
        temp.write(uploaded_local_file.read())
        temp_file_path = temp.name
    try:
        transcription = transcribe_video_to_text(temp_file_path)
        os.remove(temp_file_path)  # Xóa tệp tạm thời sau khi hoàn tất
    except FileNotFoundError as e:
        st.error(e)

if selection_method == 'Enter YouTube video URL' and uploaded_file:
    try:
        temp_audio_file = download_youtube_audio_to_temp(uploaded_file)
        transcription = transcribe_video_to_text(temp_audio_file)
        os.remove(temp_audio_file)  # Xóa tệp tạm thời sau khi hoàn tất
    except FileNotFoundError as e:
        st.error(e)


   
