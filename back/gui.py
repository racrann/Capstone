from PyQt6.QtWidgets import QApplication, QHBoxLayout,QVBoxLayout, QWidget, QLabel, QPushButton, QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sys
import spotipy
import os
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
        self.resize(600,600)
        self.setWindowTitle("Music Recs")

        layout = QHBoxLayout()
        self.setLayout(layout)

        button = QPushButton('Collect last 50 songs', self)
        button.clicked.connect(self.user_data_recent)
        layout.addWidget(button)
        
        uplay_dropdown = QComboBox()
        results = sp.current_user_playlists()
        for idx, item in enumerate(results['items']):
            playlist = item['name']
            uplay_dropdown.addItem(playlist)
        uplay_dropdown.activated.connect(self.pick_uplay)
        layout.addWidget(uplay_dropdown)

        button = QPushButton('Collect top songs', self)
        button.clicked.connect(self.rec_files_top)
        layout.addWidget(button)

        layout.setContentsMargins(50,20,50,20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    def user_data_recent(self):
        from user_files import grab_recent, make_files
        track_ids = grab_recent()
        make_files(track_ids)

    def rec_files_top(self):
        import rec_files
    def pick_uplay(self, index):
        from user_files import grab_user_playlist, make_files#change user and rec to only be methods that can be executed here.
        track_ids = grab_user_playlist(index)
        make_files(track_ids)
    def rec_files_q(self, q):
        'make it so it takes in a query and does everything in the rec_files'

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())


