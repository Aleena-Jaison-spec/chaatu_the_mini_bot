from main import chat_with_gpt

print("Chatbot (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    bot_reply = chat_with_gpt(user_input)
    print("Bot:", bot_reply)
