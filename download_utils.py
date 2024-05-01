import json
from gtts import gTTS
import requests
from bs4 import BeautifulSoup

from requests import HTTPError


# Path to the collection.media directory
# The real directory: '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.media'
MEDIA_DIRECTORY_PATH = '/Users/bochkovoy/Downloads'


def fetch_with_merriam_webster(word):
    # print(f'Looking for the word "{word}" in Merriam-Webster...')
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    with requests.session() as session:
        try:
            translation_page = session.get(url, headers=headers)
            translation_page.raise_for_status()
            soup = BeautifulSoup(translation_page.content, 'html.parser')
            json_str = json.loads(soup.find(type="application/ld+json").contents[0])

            audio_download_url = json_str[4]['contentURL']
            audio_file = session.get(audio_download_url, headers=headers)
            audio_file.raise_for_status()  # Check if the audio file was retrieved successfully

            # Saving the audio file
            with open(f"{MEDIA_DIRECTORY_PATH}/{word}.mp3", 'wb') as file:
                file.write(audio_file.content)
                print(f"{word}.mp3 downloaded from Merriam-Webster and saved successfully!")
            return True

        except (HTTPError, IndexError, KeyError, AttributeError) as e:
            print(f"Failed to fetch from Merriam-Webster due to: {e}. Falling back to gTTS.")
            fetch_with_gTTS(word)  # Fallback to gTTS
            return False


def fetch_with_gTTS(word):
    try:
        tts = gTTS(text=word, lang='en')  # Create a gTTS object
        tts.save(f"{MEDIA_DIRECTORY_PATH}/{word}.mp3")  # Save the audio to a file
        print(f"{word}.mp3 generated with gTTS and saved successfully!")
        return True
    except Exception as e:
        # General exception catch, which might include file I/O errors, etc.
        print(f"An unexpected error occurred while generating audio for '{word}' with gTTS: {e}")
        return False


def get_pronunciation(word):
    # First, try to fetch the pronunciation with Merriam-Webster
    if fetch_with_merriam_webster(word):
        return True  # Returns True if successful
    else:
        # If Merriam-Webster fails, try with gTTS
        if fetch_with_gTTS(word):
            return True  # Returns True if gTTS is successful
        else:
            return False  # Returns False if both methods fail

    return False  # Explicitly state the default return value