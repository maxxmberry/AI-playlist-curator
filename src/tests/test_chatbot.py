# Functioning script that invokes a simple chatbot that runs until quit

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

api_key = os.getenv("GEMINI_API_KEY") # change accordingly

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=api_key
)

# Store conversation history
chat_history = []

print("Chatbot is running. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # Add user message to history
    chat_history.append(HumanMessage(content=user_input))

    # Send entire conversation history to model
    response = llm.invoke(chat_history)

    # Print response
    print("Bot:", response.content)

    # Add model response to history
    chat_history.append(AIMessage(content=response.content))