import pandas as pd
import numpy as np
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import black_list

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

feat_names = ['danceability','energy','acousticness',
               'instrumentalness','valence','tempo','liveness','mode','loudness','speechiness']
    #'duration_ms','time_signature','key'


#rec_feat_ngen = rec_feat.drop('genre', axis = 1)


from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import plotly.express as px

cluster = KMeans(n_clusters = 3)
cluster.fit(rec_feat[feat_names])
cluster_pred = cluster.predict(rec_feat[feat_names])

rec_feat['label'] = pd.Series(cluster_pred, index=rec_feat.index)


#user_feat_ngen = user_feat.drop('genre', axis=1)
cluster_pred_user = cluster.predict(user_feat[feat_names])

user_feat['label'] = pd.Series(cluster_pred_user, index=user_feat.index)

#tsne = TSNE(n_components=2)
#tsne_results = tsne.fit_transform(rec_feat[feat_names])
#fig = px.scatter(
#    tsne_results, x=0, y=1,
#    color = rec_feat.label
#)
#fig.show()


all_feat = np.concatenate((rec_feat,user_feat), axis = 0)


tree = KDTree(all_feat)
ind = tree.query_radius(all_feat[0:], r=.05)
#ind = tree.query(pcad_all[0:], k=3)
ind = np.array(ind).tolist()  
#ind_df = pd.DataFrame(ind)

neighbor_lists= []
neighbor_list_index = []

for i in range(len(ind[:len(rec_feat)])):
    ind[i].sort()
    for neighb in ind[i]:
        if (neighb>=len(user_feat)-1):
            neighbor_lists.append(ind[i])
            neighbor_list_index.append(i)
            break
    
            
neighbor_lists #so this has all the recommended songs based on what songs its a neighbor to
neighbor_list_index # has the indices of the neighbor songs. so plug these into original w/id dataframe to pull recs

recs = pd.DataFrame()
for i in range(len(neighbor_list_index)):
    recs = pd.concat([recs, rec_feat_w_id.iloc[i]], axis=1)


recs=recs.iloc[11]  

def queue_recs():
    for i in range(int(10)):
        if not black_list.check(recs[i]):
            sp.add_to_queue(recs[i])

#adds songs to user's queue

    

