import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_posts():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Generate 10 short, funny, biting political satire posts for X (Twitter). Topic: current US politics and geopolitics. Each post max 280 characters. Numbered list. Dry humor, punchy, shareable."
        }]
    )
    print(response.choices[0].message.content)

generate_posts()
