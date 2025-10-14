from openai import OpenAI

# initialize client
client = OpenAI()

# simple test query
response = client.chat.completions.create(
    model="gpt-4o-mini",   # or "gpt-4.1" if you have access
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, can you read resumes?"}
    ]
)

print(response.choices[0].message.content)
