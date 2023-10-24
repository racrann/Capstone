import pandas as pd 
import numpy as np 
from dotenv import load_dotenv
import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from random import *

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")
#scope of application: modifying playback, user library, and playlists; read user data; create playlists.
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))

def track_id_helper(tracks, id):
    for track in tracks:
        if not pd.isna(track['track']):
            id.append(track['track']['id'])


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

def flatten_tracks(tracks):
    flat_tracks = []
    for sublist in tracks:
        for item in sublist:
            flat_tracks.append(item)
    return flat_tracks

def grab_genres_uris(uris):
    #this grabs the first listed genre for the artist and assigns
    #it to the song. any unlisted are marked as unknown.
    genres=[]
    genre = []
    for i in range(len(uris)): #implement the page thing here
        track = sp.track(uris['col'][i])
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

def extract_features(track_uris):
    featsl = []
    for i in range(len(track_uris)):
        feat=sp.audio_features(track_uris['col'][i])
        featsl = feat+featsl
    feats = pd.DataFrame(featsl)
    return feats

def clean_features(features):
    features=features.drop_duplicates(subset=['id'])
    return features


#pulls songs based on a search, could be a genre, artist, or year.
def pull_query_songs_playlist(query):
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

'if pulling songs from top lists'
#rec_id = pull_top_songs()

'pulling songs that could be recommended from a search query/genre/artist/years'
rec_id = pull_query_songs_playlist('death metal')
#randomly pick 100 of the songs
temp_list = []
for i in range(100):
    temp_id = rec_id[randrange(0, len(rec_id))]
    temp_list.append(temp_id)
rec_id = pd.DataFrame({'col':temp_list})

time.sleep(4)
rec_feat = extract_features(rec_id)

time.sleep(4)
genres = grab_genres_uris(rec_id)
rec_feat.insert(0,'genre',genres)
rec_feat_w_id = rec_feat.drop(['type','uri','track_href','analysis_url'], axis=1)
rec_feat_w_id = clean_features(rec_feat_w_id)
rec_feat=rec_feat_w_id.drop(['id'], axis=1)
rec_feat

rec_feat_w_id.to_csv('rec_id.csv', index=False)
rec_feat.to_csv('rec.csv', index=False)