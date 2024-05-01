import sqlite3
from download_utils import get_pronunciation

# The path to the collection.anki2 file, originally it's
# '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.anki2'
DB_PATH = '/Users/bochkovoy/Desktop/collection_test.anki2'


def get_words_from_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT sfld FROM notes WHERE tags LIKE '%to_voice%'"
    cursor.execute(query)
    words = cursor.fetchall()

    conn.close()
    return words  # Here we return a list of words to process


words_to_voice = get_words_from_database(DB_PATH)
print(f"Selected words: {words_to_voice}")
print(f"{len(words_to_voice)} words will be processed.")


def add_audio_to_database(db_path, translations):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for note_id, translation in translations.items():
        cursor.execute("SELECT flds FROM notes WHERE id = ?", (note_id,))
        flds = cursor.fetchone()[0]
        fields = flds.split(chr(31))
        fields[4] = translation  # Replace English definition with Russian translation
        updated_flds = chr(31).join(fields)

        update_query = "UPDATE notes SET flds = ? WHERE id = ?"
        cursor.execute(update_query, (updated_flds, note_id))

    conn.commit()
    conn.close()


# TODO: Use words_to_voice list
# TODO: Each word from words_to_voice should be saved to collection.media
# TODO: Each audio should be recorded into flds with the format [sound:{word}.mp3]
number = 0
for note_id, word in words_to_voice.items():
    audios[note_id] = get_pronunciation(word)
    print(f"{number}: Translation for '{word}' — '{audios[note_id]}'")
    number = number + 1

add_audio_to_database(DB_PATH, audios)
