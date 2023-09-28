import pandas as pd 
import numpy as np 
from dotenv import load_dotenv
import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from itertools import chain

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

#pulls songs from the top spotify playlists, effectively pulling pop songs.
def pull_top_songs():
    top_lists=[]
    for i in sp.category_playlists(category_id='toplists', country = 'US', limit = 50)['playlists']['items']:
        top_lists.append(i['id'])
    
    top_tracks = []
    for i in range(len(top_lists)):
        results=get_all_playlist_track_uri(top_lists[i])
        results
        top_tracks.append(results)
    top_tracks = flatten_tracks(top_tracks)
    return top_tracks

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

#currently grabs genres of songs in a playlist. 
def grab_genres_pl(pl_id): #SWITCH TO TAKE A LIST OF URI
    #this grabs the first listed genre for the artist and assigns
    #it to the song. any unlisted are marked as unknown.
    genres=[]
    genre = []
    for track in sp.playlist_tracks(pl_id)['items']: #implement the page thing here
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

#removes duplicates
def clean_features(features):
    #temp = pd.DataFrame()
    features=features.drop_duplicates(subset=['id'])
    #temp = temp.drop(['id'], axis=1)
    return features

#RECOMMENDATIONS BASED ON USER'S PLAYLIST
#results = sp.current_user_playlists()
#lists playlists
#for idx, item in enumerate(results['items']):
#    playlist = item['name']
#    print(idx+1, playlist[0:])

#choose which playlist
#ind = int(input("Which playlist (by number)"))
#for idx, item in enumerate(results['items']):
#    if(idx+1 == ind):
#        playlist_name = item['name']
#        id = item['id']

#print playlist name
#print("\n\t",playlist_name)

#get ids and exclude songs with no id
#track_uris=get_all_playlist_track_uri(id)

#BASED ON RECENT SONGS
results=sp.current_user_recently_played()['items']

for i in range(len(results)):
    print(results[i]['track']['name'])


track_uris = get_all_history_track_uri()
for track in track_uris:
    if track is None:
        track_uris.remove(track)


user_feat = extract_features(track_uris)
genres = grab_genre_recent()
user_feat.insert(0,'genre', genres)

#creates a features dataframe and a features+id dataframe for referencing the song id later.
user_feat_w_id = user_feat.drop(['type','uri','track_href','analysis_url'], axis=1)
user_feat_w_id = clean_features(user_feat_w_id)
user_feat=user_feat_w_id.drop(['id'], axis=1)

user_feat
#at this point the features of the chosen playlist have been pulled.
#now we can pull pop songs and analyze user playlist + history.

#sleep to prevent too many calls to the api.
time.sleep(10)
#rec_id = pull_top_songs()
rec_id = pull_query_songs('metal')
rec_id = rec_id[0:180]

rec_feat = extract_features(rec_id)


#genres = grab_genre_pl()
#rec_feat.insert(0,'genre',genres)
rec_feat_w_id = rec_feat.drop(['type','uri','track_href','analysis_url'], axis=1)
rec_feat_w_id = clean_features(rec_feat_w_id)
rec_feat=rec_feat_w_id.drop(['id'], axis=1)
rec_feat

rec_feat.to_csv('rec.csv', index=False)
user_feat.to_csv('user.csv', index=False)
rec_feat_w_id.to_csv('rec_id.csv', index=False)
user_feat_w_id.to_csv('user_id.csv', index=False)