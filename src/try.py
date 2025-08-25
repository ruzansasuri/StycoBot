import openai
import os

openai.api_key = os.getenv("GPT_API_KEY")

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)