# Simple agent with simple tool

import os
from langchain.tools import tool
# from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import get_all_favorite_songs, get_all_favorite_artists, initialize_favorite_songs

api_key = os.getenv("GEMINI_API_KEY") # change accordingly

# Mock data
favorite_songs = [
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

initialize_favorite_songs(favorite_songs)

# Sample tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return "It's sunny."

# NEW TOOL
@tool(description="Get all of the user's favorite songs")
def get_all_favorite_songs_tool() -> str:

    songs = get_all_favorite_songs()

    if not songs:
        return "No favorite songs found."

    return "\n".join(
        [
            f"{s['title']} by {s['artist']} ({s['genre']})"
            for s in songs
        ]
    )

@tool(description="Show all favorite songs in the database")
def show_all_favorites() -> str:

    songs = get_all_favorite_songs()

    if not songs:
        return "No songs found."

    return "\n".join(
        [
            f"{s['title']} by {s['artist']}"
            for s in songs
        ]
    )

# Initialize LLM with 3.1 Pro (for tools use) and bind required tools
model_with_tools = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.6,
    google_api_key=api_key
    ).bind_tools([get_all_favorite_songs_tool, show_all_favorites])

messages = [
    SystemMessage(
        content="""
You are a music recommendation assistant.

Your job is to recommend new songs and artists based on the user's preferences.

You have access to tools that store and retrieve the user's favorite music.

Use the tools to understand the user's taste before making recommendations.

Guidelines:

- The user's favorite songs and artists define their music taste
- You may recommend songs using your own knowledge
- Do NOT repeat songs already in the user's favorites
"""
    )
]

tools = {
    "get_all_favorite_songs_tool": get_all_favorite_songs_tool,
    "show_all_favorites": show_all_favorites
}

def extract_text(response):

    if hasattr(response, "content"):
        if isinstance(response.content, list):
            if len(response.content) > 0:
                item = response.content[0]
                if isinstance(item, dict) and "text" in item:
                    return item["text"]
                return str(item)
        return str(response.content)
    return str(response)

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["quit", "exit"]:
        break

    messages.append(HumanMessage(user_input))

    ai_msg = model_with_tools.invoke(messages)
    messages.append(ai_msg)

    print(ai_msg.tool_calls)

    # Only run tools if they exist
    if ai_msg.tool_calls:

        for tool_call in ai_msg.tool_calls:

            tool_name = tool_call["name"]

            selected_tool = tools[tool_name]

            tool_result = selected_tool.invoke(tool_call)

            messages.append(tool_result)

        # Get final response AFTER tool execution
        final_response = model_with_tools.invoke(messages)

    else:

        # Use the original response directly
        final_response = ai_msg

    messages.append(final_response)

    print("\nAgent:", extract_text(final_response))
