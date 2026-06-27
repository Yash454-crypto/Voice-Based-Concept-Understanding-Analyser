# ===========================================
# Requirements: Voice-Based Concept Understanding Analyser
# ===========================================

# --- Audio capture & processing ---
SpeechRecognition==3.10.4
pyaudio==0.2.14
pydub==0.25.1
sounddevice==0.4.7
librosa==0.10.2

# --- Speech-to-Text engines ---
openai-whisper==20240930
vosk==0.3.45

# --- NLP / Concept matching ---
nltk==3.9.1
spacy==3.7.5
scikit-learn==1.5.2
sentence-transformers==3.1.1

# --- Data handling ---
numpy==1.26.4
pandas==2.2.3

# --- Database ---
SQLAlchemy==2.0.35
psycopg2-binary==2.9.9

# --- Web/API layer (optional, for dashboard or backend) ---
flask==3.0.3
fastapi==0.115.0
uvicorn==0.31.0

# --- Visualization / Reporting ---
matplotlib==3.9.2
graphviz==0.20.3

# --- Utilities ---
python-dotenv==1.0.1
tqdm==4.66.5