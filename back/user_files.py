import pandas as pd 
import numpy as np 
from dotenv import load_dotenv
import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from itertools import chain
from random import *

#load env file that contains the information necessary to access spotify api
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")
#scope of application: modifying playback, user library, and playlists; read user data; create playlists.

#authorize user
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))

#grabs uri of all songs on a playlist
def get_all_playlist_track_uri(playlist_id):
    track_ids = []
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    #get ids which are presented as pages if the amount of songs exceeds 100.
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_id_helper(tracks, track_ids)
    return track_ids

#grabs uris of the 50 most recently played songs.
def get_all_history_track_uri():
    track_ids = []
    results = sp.current_user_recently_played()
    tracks = results['items']
    track_id_helper(tracks, track_ids)
    return track_ids

#removes local tracks. since they are local to the user's machine, there are no spotify metrics for them, causing errors.
def track_id_helper(tracks, id):
    for track in tracks:
        if not pd.isna(track['track']):
            id.append(track['track']['id'])

#?
def flatten_tracks(tracks):
    flat_tracks = []
    for sublist in tracks:
        for item in sublist:
            flat_tracks.append(item)
    return flat_tracks



#currently grabs genres of songs in a playlist. 
def grab_genres_uris(uris): #SWITCH TO TAKE A LIST OF URI
    #this grabs the first listed genre for the artist and assigns
    #it to the song. any unlisted are marked as unknown.
    genres=[]
    genre = []
    for song in uris: #implement the page thing here
        track = sp.track(song)
        #if track['track']['is_local']:
            #genres.append('unknown')
            #continue
        artist = sp.artist(track["artists"][0]["uri"])
        search = sp.search(artist, type = 'artist')
        genre = artist['genres']
        if len(genre)==0:
            genre = 'unknown'
        else:
            genre = genre[0]

        genres.append(genre)
        genres
    return genres

#grabs genres of user history
def grab_genre_recent():
    genres=[]
    genre = []
    for track in sp.current_user_recently_played()['items']:
        if track['track']['is_local']:
            genres.append('unknown')
            continue
        artist = track["track"]["artists"][0]["uri"]
        search = sp.artist(artist)
        genre = search['genres']
        if len(genre)==0:
            genre = 'unknown'
        else:
            genre = genre[0]

        genres.append(genre)
        genres
    return genres
    
#extracts audio features of tracks    
def extract_features(track_uris):
    featsl = []
    for i in track_uris:
        feat=sp.audio_features(i)
        featsl = feat+featsl
    feats = pd.DataFrame(featsl)
    return feats

#removes duplicates from audio feature list
def clean_features(features):
    features=features.drop_duplicates(subset=['id'])
    return features

def grab_recent():
    track_ids = get_all_history_track_uri()
    return(track_ids)


def grab_user_playlist(index):
    results = sp.current_user_playlists()
    id = results['items'][index]['id']
    track_uris = get_all_playlist_track_uri(id)
    return(track_uris)

def make_files(track_uris):
    user_feat = extract_features(track_uris)
    #genres = grab_genre_recent()
    #user_feat.insert(0,'genre', genres)

    user_feat_w_id = user_feat.drop(['type','uri','track_href','analysis_url'], axis=1)
    user_feat_w_id = clean_features(user_feat_w_id)
    user_feat=user_feat_w_id.drop(['id'], axis=1)

    user_feat.to_csv('user.csv', index=False)
    user_feat_w_id.to_csv('user_id.csv', index=False)

grab_recent()

#track_uris=get_all_playlist_track_uri(id)

#track_uris = get_all_history_track_uri()
#for track in track_uris:
#    if track is None:
#        track_uris.remove(track)


#creates a features dataframe and a features+id dataframe for referencing the song id later.
#at this point the features of the chosen playlist have been pulled.
#now we can pull pop songs and analyze user playlist + history.