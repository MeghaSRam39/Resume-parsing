from groq import Groq
import os
from dotenv import load_dotenv

def generate(text):
    load_dotenv(override=True)
    api = os.getenv('groq_api')

    client = Groq(api_key=api)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant."
            },
            {
                "role": "user",
                "content":f"{text}",
            }
        ],

        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return chat_completion.choices[0].message.content