from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
import sys
import spotipy
import os
import urllib
import threading
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = ("user-modify-playback-state user-library-modify user-library-read user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public")
#scope of application: modifying playback, user library, and playlists; read user data; create playlists.

#authorize user
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET,
                                            REDIRECT_URI,scope = SCOPE))

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("Music Recs")

        layout = QGridLayout()
        self.setLayout(layout)

        button = QPushButton('Collect last 50 songs', self)
        button.clicked.connect(self.user_data_recent)
        button.setToolTip('Collect your most recent 50 songs to base recs off of')
        layout.addWidget(button, 0, 0)
        
        uplay_dropdown = QComboBox()
        uplay_dropdown.setPlaceholderText('Pick a user playlist')
        results = sp.current_user_playlists()
        for idx, item in enumerate(results['items']):
            playlist = item['name']
            uplay_dropdown.addItem(playlist)
        uplay_dropdown.setToolTip('Pick a playlist of yours to base recs off of')
        uplay_dropdown.activated.connect(self.pick_uplay)
        layout.addWidget(uplay_dropdown, 0, 1)

        button = QPushButton('Collect top songs', self)
        button.setToolTip('Collect top charters to pic recs from')
        button.clicked.connect(self.rec_files_top)
        layout.addWidget(button, 0, 2)

        self.q_box = QLineEdit(self)
        self.q_box.setFixedWidth(70)
        layout.addWidget(self.q_box, 0, 3)

        button = QPushButton('enter query', self)
        button.clicked.connect(self.rec_files_q)
        layout.addWidget(button, 0, 4)


        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/play.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.play_pause)
        layout.addWidget(button, 10, 2, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/ffw.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.ffw)
        layout.addWidget(button, 10, 3, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/rew.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.rew)
        layout.addWidget(button, 10, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton('QUEUE RECS', self)
        button.clicked.connect(self.queue_recs)
        layout.addWidget(button, 10,4, alignment = Qt.AlignmentFlag.AlignCenter)

        def cover_art(): #'DUNNO HOW TO GET TO CHANGE'
            threading.Timer(5.0, cover_art).start()
            cover_url = sp.currently_playing()['item']['album']['images'][0]['url']
            with urllib.request.urlopen(cover_url) as url:
                data = url.read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            pixmap = pixmap.scaledToWidth(300)
            pixmap = pixmap.scaledToHeight(300)
            label = QLabel()
            label.setPixmap(pixmap)
            layout.addWidget(label, 5, 1, 1, 3, Qt.AlignmentFlag.AlignCenter)
        cover_art()

        layout.setContentsMargins(50,20,50,20)
        layout.setSpacing(20)
    

    def user_data_recent(self):
        from user_files import grab_recent, make_files
        track_ids = grab_recent()
        make_files(track_ids)

    def rec_files_top(self):
        from rec_files import pull_top_songs, make_files
        track_ids = pull_top_songs()
        make_files(track_ids)
    def pick_uplay(self, index):
        from user_files import grab_user_playlist, make_files#change user and rec to only be methods that can be executed here.
        track_ids = grab_user_playlist(index)
        make_files(track_ids)
    def rec_files_q(self):
        from rec_files import pull_query_songs_playlist, make_files
        query = self.q_box.text()
        track_ids = pull_query_songs_playlist(query)
        make_files(track_ids)
    def play_pause(self):
        if sp.current_playback()['is_playing'] == False:
            sp.start_playback()
        else:
            sp.pause_playback()
    def ffw(self):
        sp.next_track()
    def rew(self):
        sp.previous_track()
    
    def queue_recs(self):
        import knn

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())


