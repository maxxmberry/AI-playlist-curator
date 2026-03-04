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
        "User-Agent": "Music-CurAItor/1.0 (mmb1189@usnh.edu)"
    }
    url = "https://musicbrainz.org/ws/2/artist/"
    params = {
        "query": artist_name,
        "fmt": "json"
    }

    # try GET request to MusicBrainz
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        # Raise HTTP errors (like 429, 503, etc.)
        response.raise_for_status()

        data = response.json()

        if not data.get("artists"):
            # print("No artist found.")
            return None

        return data["artists"][0]

    except requests.exceptions.RequestException:
        print("Network/API error occurred. Please try again.")
        return None

    except ValueError:
        print("Invalid JSON response received.")
        return None


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

# Adds a new artist to favorite artists list
# artist_name: name of artist entered from user
def add_artist(artist_name):
    cached = get_artist_from_cache(artist_name)
    if cached:
        print(f"{artist_name} already in your favorites.")
        return
    
    print("Fetching artist info from MusicBrainz...")
    newArtist = get_artist_info(artist_name)
    if newArtist is None:
        print("Could not retrieve artist.")
        return

    newArtistDoc = f"""
    Artist: {newArtist.get('name')}
    MBID: {newArtist.get('id')}
    Country: {newArtist.get('country')}
    Type: {newArtist.get('type')}
    Tags: {', '.join([t['name'] for t in newArtist.get('tags', [])])}
    """

    collection.add(
        documents=[newArtistDoc],
        ids=[newArtist.get("id")],
        metadatas=[{
            "artist_name": newArtist.get("name"),
            "type": "artist"
        }]
    )

    print(f"{newArtist.get('name')} added to favorites!")

# Removes artist from favorite artists list
# artist_name: name of artist entered from user
def remove_artist(artist_name):
    results = collection.get(where={"artist_name": artist_name})
    if not results["ids"]:
        print(f"{artist_name} not found in favorites...")
        return
    
    collection.delete(ids=results["ids"])
    print(f"{artist_name} removed from favorites.")

# Prints list of favorite artists
def list_artists():
    stored = collection.get()
    if not stored["ids"]:
        print("You don't have any favorite artists saved")
        return
    print("\nFavorite Artists:")
    for meta in stored["metadatas"]:
        print(f"- {meta["artist_name"]}")

while True:
    command = input("\nEnter a command (add/remove/list/quit/help): ").strip()

    if command.lower() == "quit":
        break
    elif command.lower() == "help":
        print(f"""
add <name>: type 'add' followed by the artist name to add them to your favorites
remove <name>: type 'remove' followed by the artist name to remove them from your favorites
list: displays all artists in your favorites
quit: exit the program""")
        
    elif command.lower().startswith("add "):
        artistName = command[4:]
        add_artist(artistName)
    elif command.lower().startswith("remove "):
        artistName = command[7:]
        remove_artist(artistName)
    elif command.lower() == "list":
        list_artists()
    else:
        print("Invalid command.")

# Display updated favorite artists after program ends
print("\nCurrently Stored Favorite Artists:")

stored = collection.get()

count = 0
for i in range(len(stored["ids"])):
    count += 1
    print(f"{count}. {stored["metadatas"][i]["artist_name"]}")