import concurrent.futures
import functools
import io
import sys

import openai
import json
from google.cloud import texttospeech
from dotenv import load_dotenv
from pydub import AudioSegment
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
tts_client = texttospeech.TextToSpeechClient()


def generate_context(pl_word, en_word):
    prompt = f"Podaj przykład kontekstu, w którym mogłoby być użyte słowo '{pl_word}' po polsku oraz jego angielski (brytyjski) odpowiednik '{en_word}' w dwóch naturalnych zdaniach: jedno w języku polskim, a drugie w języku angielskim. Proszę o poprawne tłumaczenie. Oddziel zdania znakiem \"|\", pierwsze zdanie ma być po Polsku."

    response = openai.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "Jesteś tłumaczem mającym za zadanie przetłumaczyć słówka z języka polskiego na angielski, dzięki czemu inni ludzie będę mogli tego słuchać w tle i uczyć się na sprawdziany. Pamiętaj, żeby tłumaczyć w sposób naturalny i zrozumiały dla innych. Zdania powinny być krótkie, ponieważ uczeń będzie odtwarzał około 100 do 200 twoich wypowiedzi przed testem."},
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


def process_single_word(word_pair):
    pl_word = word_pair['pl']
    en_word = word_pair['en']
    pl_context, en_context = generate_context(pl_word, en_word)

    return {
        'pl': pl_word,
        'en': en_word,
        'pl_context': pl_context,
        'en_context': en_context
    }


def process_words_in_parallel(words, max_workers=10):
    total_words = len(words)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_word, word_pair) for word_pair in words]

        # Track progress
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            print(f"Processed: {i + 1}/{total_words}, {(i + 1) / total_words * 100:.2f}%", flush=True)

    return [future.result() for future in futures]

def retry_on_failure(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < 4:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                if attempts == 4:
                    raise e
                print(f"Attempt {attempts} failed: {e}. Retrying...")
    return wrapper

@retry_on_failure
def text_to_speech(text, language_code):
    synthesis_input = texttospeech.SynthesisInput(text=text)

    if language_code == "pl-PL":
        voice = texttospeech.VoiceSelectionParams(
            language_code="pl-PL",
            name="pl-PL-Standard-D",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
    elif language_code == "en-GB":
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
    else:
        raise ValueError("Unsupported language code")

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

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

import functools

def process_single_entry(entry, output_dir, idx):
    # Process the entry and generate audio files
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

    file_path = f'{output_dir}/{idx}.mp3'.replace('//', '/')

    # Save combined audio as mp3
    combined_audio.export(file_path, format="mp3")

    return {
        'en': en_word,
        'pl': pl_word,
        'en_context': en_context,
        'pl_context': pl_context,
        'path': file_path,
    }


def process_entries_in_parallel(entries, output_dir, max_workers=10):
    os.makedirs(output_dir, exist_ok=True)
    total_entries = len(entries)

    all_res_metadata = dict()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_entry, entry, output_dir, idx) for idx, entry in enumerate(entries)]

        # Track progress
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res_metadata = future.result()
            base_path = os.path.basename(res_metadata['path'])

            all_res_metadata[base_path] = {
                'en': res_metadata['en'],
                'pl': res_metadata['pl'],
                'en_context': res_metadata['en_context'],
                'pl_context': res_metadata['pl_context'],
            }

            print(f"Saved: {res_metadata['path']}, {i + 1}/{total_entries}, {(i + 1) / total_entries * 100:.2f}%")

    with open(f'{output_dir}/content.json', 'w') as f:
        json.dump(all_res_metadata, f, indent=4)


if __name__ == '__main__':
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./out"
    json_input = open("input.json").read()

    words = json.loads(json_input)
    process_entries_in_parallel(process_words_in_parallel(words), output_dir)
