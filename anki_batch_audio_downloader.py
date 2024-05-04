import sqlite3
from download_utils import get_pronunciation

# The path to the collection.anki2 file, originally it's
# '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.anki2'
DB_PATH = '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.anki2'
# Path to the collection.media directory
# The real directory: '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.media'
MEDIA_DIRECTORY_PATH = '/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.media'


def get_words_from_database(db_path):
    # Manage the database connection with a context manager
    with sqlite3.connect(db_path) as conn:
        # Create the cursor object without a context manager
        cursor = conn.cursor()
        try:
            query = "SELECT sfld FROM notes WHERE tags LIKE '%to_voice%'"
            cursor.execute(query)
            words = cursor.fetchall()
            # Convert from list of tuples to a list of strings
            words = [item[0] for item in words]
        finally:
            # Ensure the cursor is closed after use
            cursor.close()

    return words  # Return the list of words to process


words_to_voice = get_words_from_database(DB_PATH)
number_of_words_to_voice = len(words_to_voice)
print(f"Selected words: {words_to_voice}")
print(f"{number_of_words_to_voice} words will be processed.")


def add_audio_to_database(db_path, words):
    try:
        # Automatically manage the database connection
        with sqlite3.connect(db_path) as conn:
            # Manually create and manage the cursor
            cursor = conn.cursor()
            try:
                for word in words:
                    cursor.execute("SELECT flds FROM notes WHERE sfld = ?", (word,))
                    result = cursor.fetchone()
                    if result is None:
                        print(f"No entry found for the word: {word}")
                        continue  # Skip to the next word if not found

                    flds = result[0]
                    fields = flds.split(chr(31))  # Splits the string on the Unit Separator

                    if len(fields) < 3:
                        print(f"Not enough fields to update for word: {word}")
                        continue  # Ensure there are enough fields to avoid IndexError

                    fields[2] = f"[sound:{word}.mp3]"  # Replace specific field with new audio link
                    updated_flds = chr(31).join(fields)

                    update_query = "UPDATE notes SET flds = ? WHERE sfld = ?"
                    cursor.execute(update_query, (updated_flds, word))

                conn.commit()
                print("The database was modified successfully!")
            finally:
                # Ensure the cursor is closed after use
                cursor.close()

    except sqlite3.DatabaseError as e:
        print(f"Database error occurred: {e}")
        # No need to explicitly call rollback; it is handled by the context manager

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        print("Database connection closed.")


for number, word in enumerate(words_to_voice):
    if get_pronunciation(word, MEDIA_DIRECTORY_PATH):
        print(f"{number + 1} out of {number_of_words_to_voice}: '{word}' downloaded")
    else:
        print(f"Error downloading {number} out of {number_of_words_to_voice} word: '{word}'!")

add_audio_to_database(DB_PATH, words_to_voice)
