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


def get_all_favorite_songs():
    """
    Returns dictionary of favorite songs collection.
    """

    results = favorite_songs_collection.get()

    return results["metadatas"]

def get_all_favorite_artists():
    """
    Returns dictionary of favorite artists collection.
    """

    results = favorite_artists_collection.get()

    return results["metadatas"]


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

def remove_favorite_artist(name):
    """
    Remove an artist from the favorite_artists collection by name.
    Returns True if removed, False if not found.
    """

    artist_id = find_artist_id_by_name(name)

    if not artist_id:
        return False

    favorite_artists_collection.delete(ids=[artist_id])

    return True


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

def find_artist_id_by_name(name):
    """
    Find the Chroma ID for a favorite artist by exact name match.
    Helper function for remove_favorite_artist.
    Returns the ID if found, otherwise None.
    """

    results = favorite_artists_collection.get()

    ids = results.get("ids", [])
    metadatas = results.get("metadatas", [])

    for artist_id, metadata in zip(ids, metadatas):
        if metadata.get("name", "").lower() == name.lower():
            return artist_id

    return None


def get_favorite_songs_count():
    """
    Return the number of songs in the favorite_songs collection.
    """

    results = favorite_songs_collection.get()

    ids = results.get("ids", [])

    return len(ids)

def get_favorite_artists_count():
    """
    Return the number of artists in the favorite_artists collection.
    """

    results = favorite_artists_collection.get()

    ids = results.get("ids", [])

    return len(ids)


def search_playlist_context(query, song_k=4, artist_k=3):
    """
    Use semantic similarity search on favorite songs and favorite artists
    to find the strongest matches for a playlist theme/vibe query.

    Returns a dictionary with:
    {
        "songs": [...],
        "artists": [...]
    }
    """

    song_docs = favorite_songs_collection.similarity_search(query, k=song_k)
    artist_docs = favorite_artists_collection.similarity_search(query, k=artist_k)

    song_matches = []
    artist_matches = []

    seen_songs = set()
    seen_artists = set()

    for doc in song_docs:
        metadata = doc.metadata or {}

        title = metadata.get("title", "Unknown")
        artist = metadata.get("artist", "Unknown")
        genre = metadata.get("genre", "Unknown")

        key = (title.lower(), artist.lower())
        if key in seen_songs:
            continue
        seen_songs.add(key)

        song_matches.append({
            "title": title,
            "artist": artist,
            "genre": genre
        })

    for doc in artist_docs:
        metadata = doc.metadata or {}

        name = metadata.get("name", "Unknown")
        genres = metadata.get("genres", "Unknown")
        country = metadata.get("country", "Unknown")
        artist_type = metadata.get("type", "Unknown")

        key = name.lower()
        if key in seen_artists:
            continue
        seen_artists.add(key)

        artist_matches.append({
            "name": name,
            "genres": genres,
            "country": country,
            "type": artist_type
        })

    return {
        "songs": song_matches,
        "artists": artist_matches
    }
