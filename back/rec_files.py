import pandas as pd 
import numpy as np 
from dotenv import load_dotenv
import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from itertools import chain
from random import *
from user_files import track_id_helper, flatten_tracks, grab_genres_uris, extract_features,clean_features,get_all_playlist_track_uri

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")
#scope of application: modifying playback, user library, and playlists; read user data; create playlists.
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))

#pulls songs based on a search, could be a genre, artist, or year.
def pull_query_songs(query):
    lists = []

    #grabs ids of each playlist
    for i in sp.search(q= query, type='playlist', limit = 10)['playlists']['items']:
        lists.append(i['id'])

    #calls method to grab track uris
    top_tracks = []
    for i in range(len(lists)):
        results=get_all_playlist_track_uri(lists[i])
        results
        #if song isnt local then append!!!!!!!!!!
        top_tracks.append(results)
    top_tracks = flatten_tracks(top_tracks)
    return top_tracks

    #pulls songs from the top spotify playlists, effectively pulling pop songs.
def pull_top_songs():
    top_lists=[]
    for i in sp.category_playlists(category_id='toplists', country = 'US', limit = 25)['playlists']['items']:
        top_lists.append(i['id'])
    
    top_tracks = []
    for i in range(len(top_lists)):
        results=get_all_playlist_track_uri(top_lists[i])
        results
        top_tracks.append(results)
    top_tracks = flatten_tracks(top_tracks)
    return top_tracks


rec_id = pull_top_songs()

rec_feat = extract_features(rec_id)

#pulling songs that could be recommended from a search query
#rec_id = pull_query_songs('metal')
#randomly pick 100 of the songs
#for i in range(100):
#    temp_id = rec_id[randrange(0, len(rec_id))]
#    temp_frame = pd.DataFrame()
#    temp_frame = pd.concat([temp_frame, temp_id], ignore_index=True)
#rec_id = temp_frame

genres = grab_genres_uris(rec_id)
rec_feat.insert(0,'genre',genres)
rec_feat_w_id = rec_feat.drop(['type','uri','track_href','analysis_url'], axis=1)
rec_feat_w_id = clean_features(rec_feat_w_id)
rec_feat=rec_feat_w_id.drop(['id'], axis=1)
rec_feat

rec_feat_w_id.to_csv('rec_id.csv', index=False)
rec_feat.to_csv('rec.csv', index=False)