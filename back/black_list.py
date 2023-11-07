import pandas as pd 
import numpy as np 
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")
#scope of application: modifying playback, user library, and playlists; read user data; create playlists.
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))

black_list = pd.DataFrame(columns = ['id'])
black_list.to_csv('black_list.csv', index=False)

def add(track_id):
    black_list.loc[len(black_list)] = track_id
    make_file()

def check(track_id):
    if track_id in black_list:
        return True
    else:
        return False
    
def make_file():
    black_list.to_csv('black_list.csv', index=False)