import pandas as pd
import numpy as np
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.cluster import KMeans
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


cluster = KMeans(n_clusters = 5)
cluster.fit(pca_rec)

cluster_pred = cluster.predict(pca_rec)

user_feat_s = scaler.transform(user_feat[feat_names])
pca_user = pca.transform(user_feat_s)

cluster_pred_user = cluster.predict(pca_user)


plt.scatter(pca_rec[cluster_pred==0,0], pca_rec[cluster_pred == 0,1], c = 'red')
plt.scatter(pca_rec[cluster_pred==1,0], pca_rec[cluster_pred == 1,1], c = 'green')
plt.scatter(pca_rec[cluster_pred==2,0], pca_rec[cluster_pred == 2,1], c = 'blue')
plt.scatter(pca_rec[cluster_pred==3,0], pca_rec[cluster_pred == 3,1], c = 'pink')
plt.scatter(pca_rec[cluster_pred==4,0], pca_rec[cluster_pred == 4,1], c = 'orange')

plt.scatter(pca_user[cluster_pred_user==0,0], pca_user[cluster_pred_user==0,1], c = 'purple')
plt.scatter(pca_user[cluster_pred_user==1,0], pca_user[cluster_pred_user==1,1], c = 'purple')
plt.scatter(pca_user[cluster_pred_user==2,0], pca_user[cluster_pred_user==2,1], c = 'purple')
plt.scatter(pca_user[cluster_pred_user==3,0], pca_user[cluster_pred_user==3,1], c = 'purple')
plt.scatter(pca_user[cluster_pred_user==4,0], pca_user[cluster_pred_user==4,1], c = 'purple')

#plt.show()

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

for i in range(5):
    sp.add_to_queue(recs.iloc[random.randint(0,len(recs))])

