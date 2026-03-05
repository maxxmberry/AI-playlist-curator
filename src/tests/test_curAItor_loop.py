import random

# My tool
def get_songs_by_genre(genre):
    """Tool that fetches songs of a specific genre."""
    return [song for song in songs if song["genre"] == genre]

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

threshold=0.60

# Agent Memory
agent_state = {
    "genre_scores": {
        "grunge": 1.0,
        "jazz": 1.0,
        "rock": 1.0,
        "folk": 1.0
    },
    # "artist_scores": {}
    "liked_songs": []
    # "disliked_songs": []
}


# Loop
for iteration in range(3):
    print(f"\n--- Iteration {iteration + 1} ---")
    
    # show current genre scores
    print("Current genre scores:", agent_state["genre_scores"])

    # randomly decide to recommend a song from favorite genre or from random genre in list
    # with bias toward favorite genre
    rand_num = random.random()
    if rand_num < threshold:
        selected_genre = max(agent_state["genre_scores"],
                             key=agent_state["genre_scores"].get)
    else:
        selected_genre = random.choice(list(agent_state["genre_scores"].keys()))

        
    recommended_songs = get_songs_by_genre(selected_genre)
    
    # Choose a random song from that genre
    recommended_song = random.choice(recommended_songs)
    
    print("Recommended song:",
          f"'{recommended_song['title']}' by {recommended_song['artist']}")
    
    # Check if song is already liked, pass rest of loop if yes
    if recommended_song in agent_state["liked_songs"]:
        print("Song already liked.")
        continue
    
    # Get feedback from user
    user_feedback = input("User feedback (like/dislike): ")
    
    # Learning step
    if user_feedback.lower() == "like":
        agent_state["genre_scores"][selected_genre] += 0.5
        agent_state["liked_songs"].append(recommended_song)

    else:
        agent_state["genre_scores"][selected_genre] -= 0.35
    
    print("\nUpdated genre scores:", agent_state["genre_scores"])
    print("Liked songs memory:", [song["title"] for song in agent_state["liked_songs"]])
