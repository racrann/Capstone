import pandas as pd
import numpy as np
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

from sklearn.neighbors import KDTree#####


load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")

#auth
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))
user_feat = pd.read_csv('user.csv')
user_feat_w_id = pd.read_csv('user_id.csv')
rec_feat_w_id = pd.read_csv('rec_id.csv')
rec_feat = pd.read_csv('rec.csv')

feat_names = ['danceability','energy','key','loudness','mode','speechiness','acousticness',
               'instrumentalness','liveness','valence','tempo','duration_ms','time_signature']

scaler = MinMaxScaler()
rec_feat_s = scaler.fit_transform(rec_feat[feat_names])

pca = PCA(n_components = .95)
pca_rec = pca.fit_transform(rec_feat_s)

best = 0
cluster_count = 0
for i in range(2, 10):
    temp_cluster = KMeans(n_clusters = i)
    temp_cluster.fit(pca_rec)
    predict = temp_cluster.predict(pca_rec)

    if((silhouette_score(pca_rec, predict)) > best):
        best = silhouette_score(pca_rec, predict)
        cluster_count = i
print(f'{best} {cluster_count}')

cluster = KMeans(n_clusters = cluster_count)
cluster.fit(pca_rec)
cluster_pred = cluster.predict(pca_rec)

user_feat_s = scaler.transform(user_feat[feat_names])
pca_user = pca.transform(user_feat_s)

cluster_pred_user = cluster.predict(pca_user)

all_feat = np.concatenate((rec_feat_s,user_feat_s), axis = 0)
pca_all = pca.transform(all_feat)

pcad_all=pd.DataFrame(pca_all)

tree = KDTree(pcad_all)
ind = tree.query_radius(pcad_all[0:], r=.05)
#ind = tree.query(pcad_all[0:], k=3)
ind = np.array(ind).tolist()  
#ind_df = pd.DataFrame(ind)

neighbor_lists= []
neighbor_list_index = []

for i in range(len(ind[:len(rec_feat_s)])):
    ind[i].sort()
    for neighb in ind[i]:
        if (neighb>=len(user_feat_s)-1):
            neighbor_lists.append(ind[i])
            neighbor_list_index.append(i)
            break
    
            
neighbor_lists #so this has all the recommended songs based on what songs its a neighbor to
neighbor_list_index # has the indices of the neighbor songs. so plug these into original w/id dataframe to pull recs

recs = pd.DataFrame()
for i in range(len(neighbor_list_index)):
    recs = pd.concat([recs, rec_feat_w_id.iloc[i]], axis=1)

recs=recs.iloc[11]
recs #THESE ARE THE RECS!!!!

def queue_recs():
    num_recs = input('How many recommendations would you like? ')
    for i in range(int(num_recs)):
        sp.add_to_queue(recs.iloc[i])

queue_recs()
#adds songs to user's queue

    

