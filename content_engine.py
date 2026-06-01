from openai import OpenAI

client = OpenAI(api_key="YOUR_KEY_HERE")

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
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
