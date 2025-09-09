import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = OpenAI()
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )


def get_words_from_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT id, flds FROM notes"
    cursor.execute(query)
    notes = cursor.fetchall()

    words = {note_id: flds.split(chr(31))[1] for note_id, flds in notes}

    conn.close()
    return words


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

def get_translation_from_chatgpt(word):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system",
             "content": "I give you an English word, you explain the word in Russian conscisely."
                        "Assume that Russian speaker speaks Russian well so you do not need to explain russian words, "
                        "so with request 'smile' answer just 'Улыбка / Улыбаться', insead of 'Улыбка - выражение радости или дружелюбия уголками губ.'"
                        "Remember to start with upper case, The response should be not more than 10-15 words."},
            {"role": "user", "content": f"{word}"}
        ]
    )

    return completion.choices[0].message.content


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
