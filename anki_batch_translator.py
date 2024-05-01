import sqlite3
import os
from download_utils import get_pronunciation


# TODO: Change to extract the right column with words to voice
def get_words_from_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT id, flds FROM notes"
    cursor.execute(query)
    notes = cursor.fetchall()

    words = {note_id: flds.split(chr(31))[1] for note_id, flds in notes}

    conn.close()
    return words


# TODO: Design something better for handling the database path
# Replace with the path to your Anki database
db_path = '/Users/bochkovoy/Downloads/1000 Basic English Words - Type Answer/collection.anki21'
words_to_translate = get_words_from_database(db_path)

print(words_to_translate)


def update_database_with_translations(db_path, translations):
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


# TODO: Use the get_pronunciation() instead of queries to GPT
translations = {}
number = 0
for note_id, word in words_to_translate.items():
    # Here you would get the translation from ChatGPT
    # Example: translations[note_id] = get_translation_from_chatgpt(word)
    # For demonstration, let's say the translation function is called `get_translation_from_chatgpt`
    translations[note_id] = get_translation_from_chatgpt(word)
    print(f"{number}: Translation for '{word}' — '{translations[note_id]}'")
    number = number + 1

print(translations)

update_database_with_translations(db_path, translations)
