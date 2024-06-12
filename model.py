import os
import whisper
from pytube import YouTube
import datetime
import tempfile
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Load Whisper model
model = whisper.load_model('base')

def transcribe_video_to_text(file_path):
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The video {file_path} does not exist.")
    
    # Transcribe audio to text
    result = model.transcribe(file_path)
    
    # Create a string to store the results
    transcription = ""
    for indx, segment in enumerate(result['segments']):
        start_time = str(datetime.timedelta(seconds=int(segment['start'])))
        end_time = str(datetime.timedelta(seconds=int(segment['end'])))
        transcription += f"{indx + 1}\n{start_time} --> {end_time}\n{segment['text']}\n\n"
    
    return transcription

def download_youtube_audio_to_temp(youtube_link):
    yt = YouTube(youtube_link)
    stream = yt.streams.filter(only_audio=True).first()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    stream.download(filename=temp_file.name)
    return temp_file.name

def get_wordnet_pos(word_tag):
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }
    return tag_dict.get(word_tag[0].upper(), wordnet.NOUN)

def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove common contractions
    abbreviations = {
        r"(\w+)'s": r"\1",
        r"(\w+)'m": r"\1",
        r"(\w+)'ve": r"\1",
        r"(\w+)'t": r"\1",
        r"(\w+)'re": r"\1",
        r"(\w+)'d": r"\1",
        r"(\w+)'ll": r"\1",
        r"n't": "",
    }

    for pattern, repl in abbreviations.items():
        text = re.sub(pattern, repl, text)

    # Tokenize words and POS tagging
    words = word_tokenize(text)
    pos_tags = nltk.pos_tag(words)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word, tag in pos_tags if word not in stop_words]

    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags if word not in stop_words]

    # Join words into processed text
    processed_text = ' '.join(words)

    return processed_text

def classify_text_with_times(split_text, keyword_dict):
    labels = set()
    time_positions = {}
    
    lines = split_text.strip().split("\n")
    
    for i, line in enumerate(lines):
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) == 2:
                time_range = parts[0].strip() + " --> " + parts[1].strip()
                if i + 1 < len(lines):
                    transcript = lines[i + 1].strip()
                    cleaned_transcript = re.sub(r'[^\w\s]', '', transcript.lower())
                    
                    # Debugging output
                    print(f"Processing line: {transcript}")
                    print(f"Cleaned transcript: {cleaned_transcript}")
                    
                    for label, phrases in keyword_dict.items():
                        for phrase in phrases:
                            escaped_phrase = re.escape(phrase)
                            if re.search(r'\b' + escaped_phrase + r'\b', cleaned_transcript):
                                labels.add(label)
                                if label in time_positions:
                                    time_positions[label].append(time_range)
                                else:
                                    time_positions[label] = [time_range]
                                # Debugging output
                                print(f"Found phrase '{phrase}' for label '{label}' at time {time_range}")
    
    return list(labels), time_positions
