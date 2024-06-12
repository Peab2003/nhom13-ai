import streamlit as st
import tempfile
import os
from model import transcribe_video_to_text, preprocess_text, download_youtube_audio_to_temp, classify_text_with_times

# Page title
st.title('🤖 Kết quả của bạn')

# Initialize transcription variable and processing flag
transcription = ""
start_process = False

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
    
    # Add Start and Reset buttons
    if st.button('Start'):
        start_process = True

    if st.button('Reset'):
        st.experimental_rerun()

# Processing logic
if start_process:
    if selection_method == 'Upload local video file' and uploaded_local_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(uploaded_local_file.read())
            temp_file_path = temp_file.name
        try:
            transcription = transcribe_video_to_text(temp_file_path)
            processed_text = preprocess_text(transcription)
            os.remove(temp_file_path)
        except FileNotFoundError as e:
            st.error(str(e))
    elif selection_method == 'Enter YouTube video URL' and uploaded_file:
        try:
            temp_audio_file = download_youtube_audio_to_temp(uploaded_file)
            transcription = transcribe_video_to_text(temp_audio_file)
            processed_text = preprocess_text(transcription)
            os.remove(temp_audio_file)
        except Exception as e:
            st.error(str(e))

# Display transcription
if transcription:
    st.text_area("Bản chép lại:", transcription, height=300)

# Classification section
keyword_dict = {
"nội dung người lớn và các thuật ngữ tình dục": ["#freethenipple", "18+", "ampland", "anal", "anus", "arse", "ass", "asslick", "ball licking", "ball sucking", "bangbros", "bangbus", "banged", "barely legal", "bastinado", "bdsm", "bestiality", "bigtits", "bitch", "blow job", "blowjob", "blowjobs", "bondage", "boner", "boob", "boobies", "booboooooobs", "boobs", "bosomy", "bra", "brazzers", "buceta", "bukkake", "buttfuck", "butthole", "buttlick", "buttsex", "cam girl", "cameltoe", "censored", "clit", "clit licker", "clitoris", "clits", "cock", "cockhead", "cocksucker", "cocksuckers", "coom", "coomer", "cum", "cumguzzler", "cumming", "cumshot", "cumshots", "cumslut", "cunnilingus", "dildo", "dildos", "doggie style", "doggiestyle", "doggy style", "dominatrix", "dommes", "dry hump", "ecchi", "erotic", "erotica", "fetish", "fetishes", "fingered", "fingerfuck", "fingerfucked", "fingerfucks", "fingering", "fistfuck", "fistfucked", "fistfuckers", "fondle", "fondled", "footjob", "genital", "genitals", "girl on top", "gratis", "gratuit", "grope", "groped", "groping", "hand job", "handjob", "handjobs", "hardcoresex", "hem", "hentai", "horney", "horny", "hot", "hot carl", "hot sex", "hotbox", "hotsex", "hottest", "huge", "humping", "incest", "incl", "intercourse", "interracial", "invisible", "kalergi", "labia", "latex", "lesbians", "lezzie", "licking", "lolicon", "lolita", "masturbate", "masturbating", "masturbation", "masturbators", "milf", "milf hunter", "milfs", "nipple", "nipples", "nude", "nudes", "nudist", "nudity", "oral sex", "orgasim", "orgasm", "orgasms", "orgies", "orgy", "panties", "panty", "pantyhose", "penis", "pervert", "perverted", "perverts", "phonesex", "pingas", "porn", "pornhub", "porno", "pornography", "pornos", "prostitution", "pussies", "pussy", "pussylicking", "r18", "redhead", "reverse cowgirl", "rimjob", "rimming", "seksi", "semen", "sex", "sex work", "sex worker", "sexo", "sexual health", "sexually", "sexy", "sexy time", "shibari", "shoplifter", "slut", "sluts", "spycam", "squirt", "squirting", "strapon", "strip", "strip club", "stripper", "stripping", "succubus", "suck", "sucking", "teens", "thong", "threesome", "throating", "titfuck", "tities", "tits", "titten", "tittie", "titties", "titty", "topless", "tribadism", "twat", "twats", "undress", "undressing", "upskirt", "upskirts", "vagina", "vaginal", "vaginal thrush", "viagra", "voyeur", "vulva", "watch free", "watch online", "webcam", "x-rated", "xxx", "xxx-tentacion"],
"thuyết âm mưu": ["pizzagate", "qanon"],
"tội phạm và bạo lực": ["9-11", "9/11", "abuser", "abusing", "abusive", "accused", "adolescent", "allegation", "allegations", "assaulted", "boko haram", "bullying", "chester bennington", "columbine", "convicted", "crimes", "cruel", "dead body", "deaths", "el chapo", "elliot rodger", "epstein", "epstein didn't kill himself", "execution", "isil", "isis", "iyad el-baghdadi", "kidnap", "murder", "murdered", "punishments", "rape", "raped", "raping", "rapist", "robbery", "sandy hook", "slaughtering", "suspect", "ted bundy", "terrorism", "terrorist", "terrorists", "violence", "violently", "virginia tech shooting", "harass", "harassment", "hazing", "betting", "child pornography", "counterfeit", "gambling", "hacking", "pedophile", "snuff"],
"ma túy và chất kích thích": ["cannabis", "cannabutter", "cocaine", "crack", "crackwhore", "drug", "drugs", "ecstasy", "hemp", "lsd", "marijuana", "meth", "pcp", "salvia", "stoned", "stoner", "thc", "vape", "weed"],
"các tổ chức cực đoan":["ku klux klan", "nazi", "neonazi"],
"dịch bệnh và bệnh tật":["coronavirus", "covid-19", "ebola", "aids", "bladder cancer", "breast cancer", "cancer", "cyst", "erectile dysfunction", "escherichia coli", "gallbladder cancer", "hiv", "lung cancer", "thyroid cancer"],
"các vấn đề chính trị và xã hội": ["#metoo", "8chan", "abortion", "abortions", "al qaeda", "al qaida", "antifa", "blue anon", "democrat", "democratic", "democrats", "election", "election fraud", "elections", "electoral", "hunter biden", "pizzagate", "pro-choice", "qanon", "voter fraud"],
"lời lẽ tục tĩu và xúc phạm": ["asshole", "assholes", "bitches", "blyat", "chuj", "cunt", "dick", "dickhead", "fack", "fag", "fagged", "faggit", "faghag", "fags", "fuck", "fuckboy", "fucked", "fucker", "fuckers", "fuckin", "fuckings", "fucks", "fucky", "fuk", "gayass", "gayfuck", "gaysex", "idiot", "im rick james bitch", "kurwa", "mothafucka", "mothafuckas", "mothafucker", "mothafuckers", "mothafucking", "motherfucka", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "n1gga", "n1gger", "nasty", "nigga", "niggah", "niggas", "niggaz", "nip", "puta", "shit", "shite", "shitfuck", "shitpost", "shits", "shitted", "shitting", "shitty", "sonofabitch", "stfu", "whore", "whores", "yvonne"],
"phân biệt chủng tộc và kỳ thị": ["chingada madre", "chink", "jews", "jigaboo", "jiggaboo", "kike", "nigger", "porch monkey", "porchmonkey", "racist", "white pride", "white supremacists"],
"hành vi nguy hiểm và tự hại": ["anthony bourdain", "bulimia", "cut", "cutting", "eugenia cooney", "momo", "suicide"]
}

if transcription:
    labels, time_positions = classify_text_with_times(transcription, keyword_dict)
    
    # Display results in the sidebar
    with st.sidebar:
        st.header("Kết quả phân loại văn bản")
        if labels:
            st.subheader("Nhãn vi phạm:")
            st.write(labels)
        else:
            st.write("Không tìm thấy từ vi phạm.")
        
        if time_positions:
            st.subheader("Thời gian vi phạm:")
            st.write(time_positions)
        else:
            st.write("Không tìm thấy thời gian vi phạm.")
