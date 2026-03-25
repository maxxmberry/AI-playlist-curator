import os
from langchain.tools import tool
from langchain.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import (
    get_all_favorite_songs,
    add_favorite_song,
    song_already_exists,
    remove_favorite_song,
    get_favorite_songs_count,
    add_favorite_artist,
    artist_already_exists,
    get_all_favorite_artists,
    remove_favorite_artist,
    get_favorite_artists_count
)
from musicbrainz_client import get_song_metadata, get_artist_metadata

api_key = os.getenv("GEMINI_API_KEY") # change accordingly
system_prompt = """
You are a music recommendation assistant.

Your job is to recommend new songs and artists based on the user's preferences.

You have access to tools that store and retrieve the user's favorite music.

Use the tools to understand the user's taste before making recommendations.

Before recommending anything, check how many favorite songs the user has.

If the user has fewer than 3 favorite songs, do NOT make personalized recommendations yet.
Instead, explain that you need at least 3 favorite songs to learn their taste better, and ask them to add more songs.

If the user has 3 or more favorite songs, you may recommend songs based on their taste.

You have access to additional tools to fetch music information/metadata.

When you print out lists, please number them instead of using bullet points (asterisks)

Guidelines:

- The user's favorite songs and artists define their music taste
- You may recommend songs using your own knowledge
- Do NOT rely on your own knowledge when fetching music info/metadata; only rely on tools
- Do NOT recommend songs already in the user's favorites
- Add new songs to the user's favorites only when they explicitly say so
- If the user appears to make a spelling error, check with them to see what they meant before acting
"""

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

@tool(description="Fetch song metadata from MusicBrainz")
def fetch_song_metadata_tool(title: str, artist: str) -> str:

    metadata = get_song_metadata(title, artist)

    if not metadata:
        return "No song metadata found."

    return (
        f"Title: {metadata['title']}\n"
        f"Artist: {metadata['artist']}\n"
        f"Genre: {metadata['genre']}"
    )

@tool(description="Add a song to the user's favorite songs collection. Always check for duplicates before adding.")
def add_song_to_favorites_tool(title: str, artist: str) -> str:

    metadata = get_song_metadata(title, artist)

    if not metadata:
        return "Could not find metadata for that song."

    title_clean = metadata["title"]
    artist_clean = metadata["artist"]

    if song_already_exists(title_clean, artist_clean):

        return (
            f'"{title_clean}" by {artist_clean} '
            "is already in your favorite songs."
        )

    add_favorite_song(metadata)

    return (
        f'Successfully added "{title_clean}" '
        f'by {artist_clean} to your favorites.'
    )

@tool(description="Remove a song from the user's favorite songs collection using the song title and artist name.")
def remove_song_from_favorites_tool(title: str, artist: str) -> str:

    removed = remove_favorite_song(title, artist)

    if not removed:
        return f'"{title}" by {artist} was not found in your favorite songs.'

    return f'Successfully removed "{title}" by {artist} from your favorites.'

@tool(description="Get the number of songs in the user's favorite songs collection.")
def get_favorite_songs_count_tool() -> str:
    count = get_favorite_songs_count()
    return str(count)

@tool(description="Add an artist to the user's favorite artists collection. Fetch artist metadata from MusicBrainz and check for duplicates before adding.")
def add_artist_to_favorites_tool(artist_name: str) -> str:

    metadata = get_artist_metadata(artist_name)

    if not metadata:
        return "Could not find metadata for that artist."

    artist_name_clean = metadata["name"]

    if artist_already_exists(artist_name_clean):
        return f'{artist_name_clean} is already in your favorite artists.'

    add_favorite_artist(metadata)

    return (
        f'Successfully added {artist_name_clean} to your favorite artists.\n'
        f'Genres: {metadata["genres"]}\n'
        f'Country: {metadata["country"]}\n'
        f'Type: {metadata["type"]}'
    )

@tool(description="Get all of the user's favorite artists")
def get_all_favorite_artists_tool() -> str:

    artists = get_all_favorite_artists()

    if not artists:
        return "No favorite artists found."

    return "\n".join(
        [
            f"{a['name']} | Genres: {a.get('genres', 'Unknown')} | Country: {a.get('country', 'Unknown')} | Type: {a.get('type', 'Unknown')}"
            for a in artists
        ]
    )

@tool(description="Remove an artist from the user's favorite artists collection by artist name.")
def remove_artist_from_favorites_tool(artist_name: str) -> str:

    removed = remove_favorite_artist(artist_name)

    if not removed:
        return f'{artist_name} was not found in your favorite artists.'

    return f'Successfully removed {artist_name} from your favorite artists.'

@tool(description="Get the number of artists in the user's favorite artists collection.")
def get_favorite_artists_count_tool() -> str:
    count = get_favorite_artists_count()
    return str(count)

# Initialize LLM with 3.1 Pro (for tools use) and bind required tools
model_with_tools = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.6,
    google_api_key=api_key
    ).bind_tools([
        get_all_favorite_songs_tool,
        fetch_song_metadata_tool,
        add_song_to_favorites_tool,
        remove_song_from_favorites_tool,
        get_favorite_songs_count_tool,
        add_artist_to_favorites_tool,
        get_all_favorite_artists_tool,
        remove_artist_from_favorites_tool,
        get_favorite_artists_count_tool
        ])

messages = [SystemMessage(content=system_prompt)]

tools = {
    "get_all_favorite_songs_tool": get_all_favorite_songs_tool,
    "fetch_song_metadata_tool": fetch_song_metadata_tool,
    "add_song_to_favorites_tool": add_song_to_favorites_tool,
    "remove_song_from_favorites_tool": remove_song_from_favorites_tool,
    "get_favorite_songs_count_tool": get_favorite_songs_count_tool,
    "add_artist_to_favorites_tool": add_artist_to_favorites_tool,
    "get_all_favorite_artists_tool": get_all_favorite_artists_tool,
    "remove_artist_from_favorites_tool": remove_artist_from_favorites_tool,
    "get_favorite_artists_count_tool": get_favorite_artists_count_tool
}

# Function to safely extract text from agent message
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

            tool_result = selected_tool.invoke(tool_call) # ["args"]

            messages.append(tool_result)

        # Get final response AFTER tool execution
        final_response = model_with_tools.invoke(messages)

    else:

        # Use the original response directly
        final_response = ai_msg

    messages.append(final_response)

    print("\nAgent:", extract_text(final_response))
