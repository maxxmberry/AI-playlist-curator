import os
import uuid
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PERSIST_DIRECTORY = "./chroma_db"

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

favorite_songs_collection = Chroma(
    collection_name="favorite_songs",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

favorite_artists_collection = Chroma(
    collection_name="favorite_artists",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

def song_already_exists(title, artist):
    """
    Check if a song already exists in the favorite_songs collection.
    """

    results = favorite_songs_collection.get()

    metadatas = results.get("metadatas", [])

    for song in metadatas:

        if (
            song.get("title", "").lower() == title.lower()
            and song.get("artist", "").lower() == artist.lower()
        ):
            return True

    return False

def add_favorite_song(song):
    """
    Add a song and it's metadata to the favorite_songs collection.
    """

    text = f"""
    Title: {song['title']}
    Artist: {song['artist']}
    Genre: {song['genre']}
    """

    favorite_songs_collection.add_texts(
        texts=[text],
        metadatas=[song],
        ids=[str(uuid.uuid4())]
    )

def find_song_id(title, artist):
    """
    Find the Chroma ID of a song using title and artist to search.
    Helper function for remove_favorite_song
    Returns the ID if found, otherwise None.
    """

    results = favorite_songs_collection.get()

    ids = results.get("ids", [])
    metadatas = results.get("metadatas", [])

    for song_id, metadata in zip(ids, metadatas):
        if (
            metadata.get("title", "").lower() == title.lower()
            and metadata.get("artist", "").lower() == artist.lower()
        ):
            return song_id

    return None

def remove_favorite_song(title, artist):
    """
    Remove a song from the favorite_songs collection by ID.
    Returns True if removed, False if not found.
    """

    song_id = find_song_id(title, artist)

    if not song_id:
        return False

    favorite_songs_collection.delete(ids=[song_id])

    return True


def artist_already_exists(name):
    """
    Check if an artist already exists in the favorite_artists collection.
    """

    results = favorite_artists_collection.get()

    metadatas = results.get("metadatas", [])

    for artist in metadatas:
        if artist.get("name", "").lower() == name.lower():
            return True

    return False

def add_favorite_artist(artist):

    text = f"""
    Artist: {artist['name']}
    Genres: {artist['genres']}
    Country: {artist.get('country', 'Unknown')}
    Type: {artist.get('type', 'Unknown')}
    """

    favorite_artists_collection.add_texts(
        texts=[text],
        metadatas=[artist],
        ids=[str(uuid.uuid4())]
    )


def get_all_favorite_songs():
    """
    Returns dictionary of favorite songs collection.
    """

    results = favorite_songs_collection.get()

    return results["metadatas"]

def get_favorite_songs_count():
    """
    Return the number of songs in the favorite_songs collection.
    """

    results = favorite_songs_collection.get()

    ids = results.get("ids", [])

    return len(ids)

def get_all_favorite_artists():
    """
    Returns dictionary of favorite artists collection.
    """

    results = favorite_artists_collection.get()

    return results["metadatas"]
