import os
import uuid
import chromadb
from langchain_chroma import Chroma
# from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time

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

def add_favorite_artist(artist):

    text = f"""
    Artist: {artist['name']}
    Genres: {artist['genres']}
    """

    favorite_artists_collection.add_texts(
        texts=[text],
        metadatas=[artist],
        ids=[str(uuid.uuid4())]
    )

def get_all_favorite_songs():

    results = favorite_songs_collection.get()

    return results["metadatas"]


def get_all_favorite_artists():

    results = favorite_artists_collection.get()

    return results["metadatas"]

def favorite_songs_collection_empty():
    return favorite_songs_collection._collection.count() == 0

def initialize_favorite_songs(initial_songs):

    if favorite_songs_collection_empty():

        print("Loading initial favorite songs into collection...")

        for song in initial_songs:
            add_favorite_song(song)
            time.sleep(1)

    else:
        print("Favorite songs collection already initialized.")
