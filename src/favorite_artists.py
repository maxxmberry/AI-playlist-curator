import requests
import chromadb

# Connect to local chromaDB directory
client = chromadb.PersistentClient(path="./chroma_db")

# Access favorite_artists collection
collection = client.get_or_create_collection(name="favorite_artists")

# Fetches new artists info from MusicBrainz
# artist_name: name of artist entered from user
def get_artist_info(artist_name):
    # Set variables for arguments in GET request
    headers = {
        "User-Agent": "AI-Playlist-Curator/1.0 (mmb1189@usnh.edu)"
    }
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

    return artist

# Retrieves artist info from cache in chromaDB if present
# artist_name: name of artist entered from user
def get_artist_from_cache(artist_name):
    results = collection.get(
        where={"artist_name": artist_name}
    )

    if results["ids"]:
        return results
    else:
        return None

while True:
    nameInput = input("Please enter an artist name ('Q/q' to quit): ") # prompt for user input for artist name
    if nameInput.lower() == "q":
        # quit loop if user exits
        break

    cached = get_artist_from_cache(nameInput) # case-senstive
    if cached:
        print("Artist found in cache")
        print(cached["documents"][0])
    else:
        print("Artist not found. Fetching from MusicBrainz")
        newArtist = get_artist_info(nameInput) # NOT case-sensitive

        newArtistDoc = f"""
        Artist: {newArtist.get('name')}
        MBID: {newArtist.get('id')}
        Country: {newArtist.get('country')}
        Type: {newArtist.get('type')}
        Tags: {', '.join([t['name'] for t in newArtist.get('tags', [])])}
        """

        print("\nFetched from MusicBrainz:")
        print(newArtistDoc)

        # Add info to "favorite artists" collection in Chroma
        collection.add(
            documents=[newArtistDoc],
            ids=[newArtist.get("id")],
            metadatas=[{
                "artist_name": newArtist.get("name"),
                "type": "artist"
            }]
        )

# Display updated favorite artists
print("\nCurrently Stored Favorite Artists:")

stored = collection.get()

for i in range(len(stored["ids"])):
    print("-", stored["metadatas"][i]["artist_name"])
