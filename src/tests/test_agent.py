# Simple agent with simple tool

import os
from langchain.tools import tool
# from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GEMINI_API_KEY") # change accordingly

# Mock data
songs = [
        {"title": "It Ain't Like That", "artist": "Alice in Chains", "genre": "grunge"},
        {"title": "Interstate Love Song", "artist": "Stone Temple Pilots", "genre": "grunge"},
        {"title": "Down in a Hole", "artist": "Alice in Chains", "genre": "grunge"},
        {"title": "Blue in Green", "artist": "Miles Davis", "genre": "jazz"},
        {"title": "Parisienne Walkway", "artist": "Gary Moore", "genre": "rock"},
        {"title": "Say You Love Me", "artist": "Fleetwood Mac", "genre": "rock"},
        {"title": "Subterranean Homesick Blues", "artist": "Bob Dylan", "genre": "rock"},
        {"title": "Don't Think Twice, It's Alright", "artist": "Bob Dylan", "genre": "folk"},
        {"title": "Cannock Chase", "artist": "Labi Siffre", "genre": "folk"},
    ]

# Helper function for get_songs_by_genre tool
def find_songs_by_genre(genre):
    return [song for song in songs if song["genre"] == genre]

# Sample tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return "It's sunny."

# My tool
@tool(description="Get songs from a specific genre")
def get_songs_by_genre(genre: str) -> str:

    results = find_songs_by_genre(genre)

    if not results:
        return "No songs found."
    return "\n".join(
        [f"{song['title']} by {song['artist']}" for song in results]
    )

# Initialize LLM with 3.1 Pro (for tools use) and bind required tools
model_with_tools = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.6,
    google_api_key=api_key
    ).bind_tools([get_songs_by_genre, get_weather])

messages = []

tools = {
    "get_weather": get_weather,
    "get_songs_by_genre": get_songs_by_genre
}

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["quit", "exit"]:
        break

    messages.append(HumanMessage(user_input))

    ai_msg = model_with_tools.invoke(messages)
    messages.append(ai_msg)

    print(ai_msg.tool_calls)

    for tool_call in ai_msg.tool_calls:
        tool_name = tool_call["name"]
        selected_tool = tools[tool_name]

        tool_result = selected_tool.invoke(tool_call)
        messages.append(tool_result)

    final_response = model_with_tools.invoke(messages)
    messages.append(final_response)

    print("\nAgent:", final_response.content[0]["text"])
