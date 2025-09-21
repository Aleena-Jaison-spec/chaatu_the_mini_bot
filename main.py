import requests

API_KEY = "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"

def chat_with_gpt(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error {response.status_code}: {response.text}"

# Example usage
user_input = input("You: ")
print("Bot:", chat_with_gpt(user_input))

