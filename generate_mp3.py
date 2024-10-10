import io

import openai
import json
from google.cloud import texttospeech
from dotenv import load_dotenv
from pydub import AudioSegment
import hashlib
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
tts_client = texttospeech.TextToSpeechClient()

def generate_context(pl_word, en_word):
    prompt = f"Podaj przykład kontekstu, w którym mogłoby być użyte słowo '{pl_word}' po polsku oraz jego angielski (brytyjski) odpowiednik '{en_word}' w dwóch naturalnych zdaniach: jedno w języku polskim, a drugie w języku angielskim. Proszę o poprawne tłumaczenie. Oddziel zdania znakiem \"|\", pierwsze zdanie ma być po Polsku."
    
    response = openai.chat.completions.create(
    messages=[
        {"role": "system", "content": "Jesteś tłumaczem mającym za zadanie przetłumaczyć słówka z języka polskiego na angielski, dzięki czemu inni ludzie będę mogli tego słuchać w tle tak jak podcastu i uczyć się na sprawdziany. Pamiętaj, żeby tłumaczyć w sposób naturalny i zrozumiały dla innych. Zdania powinny być zrozumiałe, krótkie i wzięte z życia codziennego."},
        {"role": "user", "content": prompt},
    ],
        model="gpt-3.5-turbo",
    )

    context = response.choices[0].message.content
    
    try:
        pl_context, en_context = context.split('|', 1)
    except ValueError:
        pl_context = context
        en_context = "Brak kontekstu po angielsku."
    
    return pl_context.strip(), en_context.strip()

def process_words(words):
    result = []
    for word_pair in words:
        pl_word = word_pair['pl']
        en_word = word_pair['en']
        
        pl_context, en_context = generate_context(pl_word, en_word)
        
        result.append({
            'pl': pl_word,
            'en': en_word,
            'pl_context': pl_context,
            'en_context': en_context
        })
    
    return result

def text_to_speech(text, language_code):
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Setting voice type
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Setting audio format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Generating audio
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content

def combine_audio_segments(audio_segments, separator_duration_ms=500):
    combined = AudioSegment.silent(duration=0)
    separator = AudioSegment.silent(duration=separator_duration_ms)

    for segment in audio_segments:
        combined += segment + separator

    return combined


def get_hash(text, length=5):
    return hashlib.md5(text.encode()).hexdigest()[:length]

json_input = '''
[
    {"pl": "kot", "en": "cat"},
    {"pl": "wyrobić nawyk", "en": "develop a habit"}
]
'''

words = json.loads(json_input)
result = process_words(words)

print(result)

os.makedirs("./out", exist_ok=True)
for i, entry in enumerate(result):
    pl_word = entry['pl']
    en_word = entry['en']
    pl_context = entry['pl_context']
    en_context = entry['en_context']

    # Generate audio segments
    pl_word_mp3 = AudioSegment.from_file(io.BytesIO(text_to_speech(pl_word, 'pl-PL')), format="mp3")
    en_word_mp3 = AudioSegment.from_file(io.BytesIO(text_to_speech(en_word, 'en-GB')), format="mp3")
    pl_context_mp3 = AudioSegment.from_file(io.BytesIO(text_to_speech(pl_context, 'pl-PL')), format="mp3")
    en_context_mp3 = AudioSegment.from_file(io.BytesIO(text_to_speech(en_context, 'en-GB')), format="mp3")

    # Combine audio
    combined_audio = combine_audio_segments([pl_word_mp3, en_word_mp3, pl_context_mp3, en_context_mp3])

    # Generate hash-based filename
    file_hash = get_hash(pl_word + en_word)
    file_path = f'./out/{en_word}-{file_hash}.mp3'

    # Save combined audio as mp3
    combined_audio.export(file_path, format="mp3")

    print(f"Saved: {file_path}")
