import os
from openai import OpenAI


def test_openai_api():
    # Make sure your API key is set in your environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is not set. Please export it first.")
        return

    client = OpenAI(api_key=api_key)

    try:
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheaper test model
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say hello in one short sentence."}
            ],
            max_tokens=20
        )
        print("✅ API call succeeded!")
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print("❌ API call failed:")
        print(e)


if __name__ == "__main__":
    test_openai_api()