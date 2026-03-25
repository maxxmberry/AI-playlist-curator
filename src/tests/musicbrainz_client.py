import requests

BASE_RECORDING_URL = "https://musicbrainz.org/ws/2/recording"
BASE_ARTIST_URL = "https://musicbrainz.org/ws/2/artist"


HEADERS = {
    "User-Agent": "Music-CurAItor/2.0 (mmb1189@usnh.edu)"
}

def get_artist_genres(artist_id):
    """
    Fetch genres for an artist.
    Args:
        artist_id: MusicBrainz artist ID
    Returns string of top 1-2 genres.
    """

    params = {
        "fmt": "json",
        "inc": "genres"
    }

    response = requests.get(
        f"{BASE_ARTIST_URL}/{artist_id}",
        headers=HEADERS,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        print("Artist genre request failed.")
        return "Unknown"

    data = response.json()

    genres = data.get("genres", [])

    if not genres:
        return "Unknown"

    # Sort by popularity count
    sorted_genres = sorted(
        genres,
        key=lambda g: g.get("count", 0),
        reverse=True
    )

    top_genres = [g["name"] for g in sorted_genres[:2]]

    return ", ".join(top_genres)


def search_musicbrainz_recording(title, artist=None):
    """
    Search for a recording and return raw JSON.
    Args:
        title: title of song
        artist: name of artist; default=None
    Returns JSON data of recording
    """

    query = f'recording:"{title}"'

    if artist:
        query += f' AND artist:"{artist}"'

    params = {
        "query": query,
        "fmt": "json",
        "limit": 1
    }

    response = requests.get(
        BASE_RECORDING_URL,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        print("Recording request failed.")
        return None

    return response.json()

def extract_song_metadata(data):
    """
    Extract title, artist, and genre from data.
    Args:
        data: raw JSON data
    Returns dictionary containing song title, artist, and genre(s)
    """

    if not data:
        return None

    recordings = data.get("recordings", [])

    if not recordings:
        return None

    recording = recordings[0]

    title = recording.get("title")

    artist = None
    artist_id = None

    if recording.get("artist-credit"):

        artist_info = recording["artist-credit"][0]["artist"]

        artist = artist_info.get("name")

        artist_id = artist_info.get("id")

    genre = "Unknown"

    if artist_id:
        genre = get_artist_genres(artist_id)

    return {
        "title": title,
        "artist": artist,
        "genre": genre
    }

def get_song_metadata(title, artist=None):
    """
    Public function used by tools.
    Args:
        title: title of song
        artist: name of artist; default=None
    Returns dictionary containing song title, artist, and genre(s)
    """

    data = search_musicbrainz_recording(title, artist)

    metadata = extract_song_metadata(data)

    return metadata


def search_musicbrainz_artist(artist_name):
    """
    Search for an artist and return raw JSON.
    Args:
        artist_name: name of artist
    Returns JSON data of artist
    """

    query = f'artist:"{artist_name}"'

    params = {
        "query": query,
        "fmt": "json",
        "limit": 1
    }

    response = requests.get(
        BASE_ARTIST_URL,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        print("Artist search request failed.")
        return None

    return response.json()

def extract_artist_metadata(data):
    """
    Extract artist metadata from the MusicBrainz response.
    Args:
        data: raw JSON data
    Returns dictionary containing artist name, MBID, country, type, and genre(s)
    """

    if not data:
        return None

    artists = data.get("artists", [])

    if not artists:
        return None

    artist = artists[0]

    artist_name = artist.get("name")
    artist_id = artist.get("id")
    country = artist.get("country", "Unknown")
    artist_type = artist.get("type", "Unknown")

    genres = "Unknown"

    if artist_id:
        genres = get_artist_genres(artist_id)

    return {
        "name": artist_name,
        "mbid": artist_id,
        "country": country,
        "type": artist_type,
        "genres": genres
    }

def get_artist_metadata(artist_name):
    """
    Public function used by tools.
    Args:
        artist_name: name of artist
    Returns dictionary containing artist name, MBID, country, type, and genre(s)

    """

    data = search_musicbrainz_artist(artist_name)

    metadata = extract_artist_metadata(data)

    return metadata
