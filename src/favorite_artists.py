import requests
import chromadb

# Connect to local chromaDB directory
client = chromadb.PersistentClient(path="./chroma_db")

# Access favorite_artists collection
collection = client.get_or_create_collection(name="favorite_artists")

# Set variables for arguments in GET request
headers = {
    "User-Agent": "AI-Playlist-Curator/1.0 (mmb1189@usnh.edu)"
}
artist_name = input("Enter an artist name: ")
url = "https://musicbrainz.org/ws/2/artist/"
params = {
    "query": artist_name,
    "fmt": "json"
}

# GET request to MusicBrainz
response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    print("Error fetching data.")
    exit()

data = response.json()

if not data["artists"]:
    print("No artist found.")
    exit()

artist = data["artists"][0]

artist_doc = f"""
Artist: {artist.get('name')}
MBID: {artist.get('id')}
Country: {artist.get('country')}
Type: {artist.get('type')}
Tags: {', '.join([t['name'] for t in artist.get('tags', [])])}
"""

print("\nFetched from MusicBrainz:")
print(artist_doc)

# Add info to "favorite artists" collection in Chroma
collection.add(
    documents=[artist_doc],
    ids=[artist.get("id")],
    metadatas=[{
        "artist_name": artist.get("name"),
        "type": "artist"
    }]
)

# Display updated favorite artists
print("\nCurrently Stored Favorite Artists:")

stored = collection.get()

for i in range(len(stored["ids"])):
    print("-", stored["metadatas"][i]["artist_name"])