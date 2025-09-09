"""
Add emoji + concise definition + mnemonic to every note tagged `process_with_GPT`.

For each note
    • Field 1 (front) … the word (e.g., “inaugural”)
    • Field 2 (back)  … your existing description

This script
    1. Calls gpt‑4.1‑mini‑2025‑04‑14 to generate:
         • an emoji line
         • a ≤20‑word plain‑English definition
         • a 2‑4‑word mnemonic
    2. Prepends the emoji + definition to Field 2.
    3. Appends the mnemonic (wrapped in _underscores_) to Field 2.
    4. Tracks tokens, prints per‑note and cumulative cost, and shows progress.

──────────────────────────────────────────────────────────────────────────────
Requirements:  pip install openai tiktoken
Set key:       export OPENAI_API_KEY="sk‑…"
──────────────────────────────────────────────────────────────────────────────
"""

import time
import sqlite3
from pathlib import Path
from openai import OpenAI

# ───────────────────────────── Configuration ────────────────────────────────
DB_PATH     = Path("/Users/bochkovoy/Library/Application Support/Anki2/Bochkovoy/collection.anki2")
TAG_FILTER  = "%process_with_GPT%"          # only notes containing this tag
FIELD_SEP   = "\x1f"                             # Anki’s internal field separator

MODEL       = "gpt-4.1-mini-2025-04-14"
MAX_TOKENS  = 100
TEMPERATURE = 0.7
RATE_DELAY  = 1.1                                # stay under the rate limit

# Prices **per 1 000 tokens** (input / output) – cached pricing ignored
PRICES = {
    "gpt-4.1-mini-2025-04-14": {"in": 0.0004, "out": 0.0016},  # 0.40 $/1M | 1.60 $/1M
    "gpt-4o-mini":             {"in": 0.0005, "out": 0.0015},
    "gpt-4o":                  {"in": 0.005,  "out": 0.015},
}
# ─────────────────────────────────────────────────────────────────────────────

client = OpenAI()
conn   = sqlite3.connect(DB_PATH)
cur    = conn.cursor()

SYSTEM_PROMPT = (
    """You are an expert English vocabulary coach building flashcards for learners. Make it fun!

For each word, return the output as three separate lines:

"[EMOJI]
[DESCRIPTION] 
[MNEMONIC]"

EMOJI — represent the word accurately with emojis.
DESCRIPTION (<25 words) — What does it mean? give the common usage of the word in the US. 
(you may accentuate something with <b> </b> tags if you want)
MNEMONIC — Coin a mnemonic or something to memorize it. 

Don't mention the word itself in all of those parts.

Strictly follow the format and don't output anything besides.
"""
)

# ───────────────────────────── DB Helpers ───────────────────────────────────
def fetch_notes():
    """Return (id, flds) for notes whose tags match TAG_FILTER."""
    cur.execute("SELECT id, flds FROM notes WHERE tags LIKE ?", (TAG_FILTER,))
    return cur.fetchall()


def update_note(note_id: int, fields: list[str]):
    """Write updated field list back to the note."""
    cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (FIELD_SEP.join(fields), note_id))


# ───────────────────────────── GPT Helper ───────────────────────────────────
def gpt_parts(term: str):
    """
    Send *term* to GPT and return:
        (emoji_line, definition, mnemonic, prompt_tokens, completion_tokens)
    """
    resp = client.chat.completions.create(
        model       = MODEL,
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f'Term: "{term}"'}
        ],
        max_tokens  = MAX_TOKENS,
        temperature = TEMPERATURE,
    )
    lines = resp.choices[0].message.content.strip().splitlines()
    if len(lines) < 3:
        raise ValueError("Unexpected format from GPT")
    emoji, definition, mnemonic = lines[:3]
    usage = resp.usage
    return emoji.strip(), definition.strip(), mnemonic.strip(), usage.prompt_tokens, usage.completion_tokens


# ───────────────────────────── Main routine ────────────────────────────────
def main():
    notes = fetch_notes()
    total_notes = len(notes)
    print(f"Processing {total_notes} notes…\n")

    total_in = total_out = 0
    cumulative_cost = 0.0

    for idx, (note_id, flds) in enumerate(notes, start=1):
        fields = flds.split(FIELD_SEP)
        if len(fields) < 2:                      # guarantee two fields
            fields.extend([""] * (2 - len(fields)))

        term = fields[0].strip()
        if not term:
            print(f"[{idx}/{total_notes}] [id {note_id}] skipped: empty term")
            continue

        try:
            emoji, definition, mnemonic, tin, tout = gpt_parts(term)
        except Exception as err:
            print(f"[{idx}/{total_notes}] [id {note_id}] error: {err}")
            continue

        # Build new back side
        # fields[1] = f"{emoji} {definition}\n\n{fields[1]}\n\n_{mnemonic}_"
        # Format Field 1 (definition section)
        fields[1] = (
            f"<div>{emoji}  {definition}"
            # f"{fields[1]}"  # keep existing content
        )

        # Format Field 4 (mnemonic section)
        fields[4] = f"<div><i>= {mnemonic}</i></div>"

        # Save to DB
        update_note(note_id, fields)

        # Update totals and costs
        total_in  += tin
        total_out += tout
        inc_cost   = (tin * PRICES[MODEL]['in'] + tout * PRICES[MODEL]['out']) / 1000
        cumulative_cost += inc_cost


        print(
            f"[{idx}/{total_notes}] “{term}” updated | "
            f"in/out {tin}/{tout} | +${inc_cost:.4f} | total ${cumulative_cost:.4f}"
        )

        time.sleep(RATE_DELAY)

    # Commit DB changes and close
    conn.commit()
    cur.close()
    conn.close()

    print("\nDone.")
    print(f"Updated notes: {idx if total_notes else 0}/{total_notes}")
    print(f"Tokens used → in: {total_in}, out: {total_out}")
    print(f"Total estimated cost: ${cumulative_cost:.4f}")


if __name__ == "__main__":
    main()