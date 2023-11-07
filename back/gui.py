from PyQt6.QtWidgets import QApplication, QGridLayout, QTabWidget, QWidget, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QObject, QTimer
import sys
import spotipy
import os
import time
import urllib
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

class Worker_Queue(QObject):
    finished = pyqtSignal()

    def run(self):
        from black_list import make_file
        make_file()
        import knn
        knn.queue_recs()
        print('ok')
        self.finished.emit()
        QThread.currentThread().quit()

class Worker_Recs_Top(QObject):
    finished = pyqtSignal()
    
    def run(self):
        from rec_files import pull_top_songs, make_files
        track_ids = pull_top_songs()
        make_files(track_ids)
        self.finished.emit()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("Music Recs")

        self.layout = QGridLayout()
        window_layout = QGridLayout()
        self.setLayout(window_layout)

        tab = QTabWidget()
        window_layout.addWidget(tab)



        settings_tab = QWidget(tab)
        settings_layout = QGridLayout()

        button = QPushButton('Wipe blacklist', self)
        button.clicked.connect(self.delete_black_list)
        settings_layout.addWidget(button, 0, 0)

        settings_tab.setLayout(settings_layout)
        tab.addTab(settings_tab, 'Settings')



        button = QPushButton('Collect last 50 songs', self)
        button.clicked.connect(self.user_data_recent)
        button.setToolTip('Collect your most recent 50 songs to base recs off of')
        self.layout.addWidget(button, 0, 0)
        
        uplay_dropdown = QComboBox()
        uplay_dropdown.setPlaceholderText('Pick a user playlist')
        results = sp.current_user_playlists()
        for idx, item in enumerate(results['items']):
            playlist = item['name']
            uplay_dropdown.addItem(playlist)
        uplay_dropdown.setToolTip('Pick a playlist of yours to base recs off of')
        uplay_dropdown.activated.connect(self.pick_uplay)
        self.layout.addWidget(uplay_dropdown, 0, 1)

        button = QPushButton('Collect top songs', self)
        button.setToolTip('Collect top charters to pic recs from')
        button.clicked.connect(self.rec_files_top)
        self.layout.addWidget(button, 0, 2)

        self.q_box = QLineEdit(self)
        self.q_box.setFixedWidth(70)
        self.layout.addWidget(self.q_box, 0, 3)

        button = QPushButton('enter query', self)
        button.clicked.connect(self.rec_files_q)
        self.layout.addWidget(button, 0, 4)


        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/play.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.play_pause)
        self.layout.addWidget(button, 10, 2, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/ffw.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.ffw)
        self.layout.addWidget(button, 10, 3, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/rew.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.rew)
        self.layout.addWidget(button, 10, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        button = QPushButton('QUEUE RECS', self)
        button.clicked.connect(self.queue_recs)
        self.layout.addWidget(button, 10,0, alignment = Qt.AlignmentFlag.AlignCenter)

        self.cover = QLabel()
        timer = QTimer(self)
        timer.setInterval(2000)
        timer.timeout.connect(self.grab_cover)
        timer.start()     
        self.layout.addWidget(self.cover, 5, 1, 4, 3, Qt.AlignmentFlag.AlignCenter)


        self.name_artist = QLabel()
        timer_2 = QTimer(self)
        timer_2.setInterval(2000)
        timer_2.timeout.connect(self.show_name_artist)
        timer_2.start()
        self.layout.addWidget(self.name_artist, 9, 1, 1, 3, Qt.AlignmentFlag.AlignCenter)

        self.queue = sp.queue()['queue']
        if sp.currently_playing() != None:
            self.label_1 = QLabel(f'{self.queue[0]['name']} - {self.queue[0]['artists'][0]['name']}')
            self.layout.addWidget(self.label_1, 4, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_2 = QLabel(f'{self.queue[1]['name']} - {self.queue[1]['artists'][0]['name']}')
            self.layout.addWidget(self.label_2, 5, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_3 = QLabel(f'{self.queue[2]['name']} - {self.queue[2]['artists'][0]['name']}')
            self.layout.addWidget(self.label_3, 6, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_4 = QLabel(f'{self.queue[3]['name']} - {self.queue[3]['artists'][0]['name']}')
            self.layout.addWidget(self.label_4, 7, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_5 = QLabel(f'{self.queue[4]['name']} - {self.queue[4]['artists'][0]['name']}')
            self.layout.addWidget(self.label_5, 8, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_6 = QLabel(f'{self.queue[5]['name']} - {self.queue[5]['artists'][0]['name']}')
            self.layout.addWidget(self.label_6, 9, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_7 = QLabel(f'{self.queue[6]['name']} - {self.queue[6]['artists'][0]['name']}')
            self.layout.addWidget(self.label_7, 10, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
        timer_3 = QTimer(self)
        timer_3.setInterval(2000)
        timer_3.timeout.connect(self.show_queue)
        timer_3.start()

        button = QPushButton(self)
        button.setGeometry(150,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/dislike.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.dislike_song)
        self.layout.addWidget(button, 9, 3, alignment = Qt.AlignmentFlag.AlignLeft)

        self.layout.setContentsMargins(50,20,50,20)
        self.layout.setSpacing(10)

        main_tab = QWidget(tab)
        main_tab.setLayout(self.layout)
        tab.addTab(main_tab, 'Main')
    
    def delete_black_list(self):
        if os.path.exists('C:/users/racra/desktop/capstone stuff/Capstone/black_list.csv'):
            os.remove('C:/users/racra/desktop/capstone stuff/Capstone/black_list.csv')

    def dislike_song(self):
        import black_list
        if not os.path.exists('black_list.csv'):
            black_list.make_file
        if sp.currently_playing() != None:
            black_list.add(sp.current_user_playing_track()['item']['id'])
            sp.next_track()
        

    def show_queue(self):
        if hasattr(self, 'label_7'):
            if self.queue != sp.queue()['queue']:
                self.label_1.setText(f'{self.queue[1]['name']} - {self.queue[1]['artists'][0]['name']}')
                self.label_2.setText(f'{self.queue[2]['name']} - {self.queue[2]['artists'][0]['name']}')
                self.label_3.setText(f'{self.queue[3]['name']} - {self.queue[3]['artists'][0]['name']}')
                self.label_4.setText(f'{self.queue[4]['name']} - {self.queue[4]['artists'][0]['name']}')
                self.label_5.setText(f'{self.queue[5]['name']} - {self.queue[5]['artists'][0]['name']}')
                self.label_6.setText(f'{self.queue[6]['name']} - {self.queue[6]['artists'][0]['name']}')
                self.label_7.setText(f'{self.queue[7]['name']} - {self.queue[7]['artists'][0]['name']}')
                self.queue = sp.queue()['queue']
        elif sp.currently_playing() != None:
            self.queue = sp.queue()['queue']
            self.label_1 = QLabel(f'{self.queue[0]['name']} - {self.queue[0]['artists'][0]['name']}')
            self.layout.addWidget(self.label_1, 4, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_2 = QLabel(f'{self.queue[1]['name']} - {self.queue[1]['artists'][0]['name']}')
            self.layout.addWidget(self.label_2, 5, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_3 = QLabel(f'{self.queue[2]['name']} - {self.queue[2]['artists'][0]['name']}')
            self.layout.addWidget(self.label_3, 6, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_4 = QLabel(f'{self.queue[3]['name']} - {self.queue[3]['artists'][0]['name']}')
            self.layout.addWidget(self.label_4, 7, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_5 = QLabel(f'{self.queue[4]['name']} - {self.queue[4]['artists'][0]['name']}')
            self.layout.addWidget(self.label_5, 8, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_6 = QLabel(f'{self.queue[5]['name']} - {self.queue[5]['artists'][0]['name']}')
            self.layout.addWidget(self.label_6, 9, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.label_7 = QLabel(f'{self.queue[6]['name']} - {self.queue[6]['artists'][0]['name']}')
            self.layout.addWidget(self.label_7, 10, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            
        
    def show_name_artist(self):
        if sp.currently_playing() != None:
            name = sp.currently_playing()['item']['name']
            artist = sp.currently_playing()['item']['artists'][0]['name']
            self.name_artist.setText(f'{name} - {artist}')

    def grab_cover(self):
        if sp.currently_playing() != None:
            cover_url = sp.currently_playing()['item']['album']['images'][0]['url']
            with urllib.request.urlopen(cover_url) as url:
                data = url.read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            pixmap = pixmap.scaledToWidth(300)
            pixmap = pixmap.scaledToHeight(300)
            self.cover.setPixmap(pixmap)

    def user_data_recent(self):
        from user_files import grab_recent, make_files
        track_ids = grab_recent()
        make_files(track_ids)

    def rec_files_top(self):
        self.thread_top = QThread()
        self.worker_rec_top = Worker_Recs_Top()
        self.worker_rec_top.moveToThread(self.thread_top)

        self.thread_top.started.connect(self.worker_rec_top.run)
        self.worker_rec_top.finished.connect(self.thread_top.quit)
        self.worker_rec_top.finished.connect(self.worker_rec_top.deleteLater)
        self.thread_top.finished.connect(self.thread_top.deleteLater)

        self.thread_top.start()
    def pick_uplay(self, index):
        from user_files import grab_user_playlist, make_files
        track_ids = grab_user_playlist(index)
        make_files(track_ids)
    def rec_files_q(self):
        from rec_files import pull_query_songs_playlist, make_files
        query = self.q_box.text()
        track_ids = pull_query_songs_playlist(query)
        make_files(track_ids)
    def play_pause(self):
        if sp.currently_playing() != None:
            if sp.current_playback()['is_playing'] == False:
                sp.start_playback()
            else:
                sp.pause_playback()
    def ffw(self):
        sp.next_track()
    def rew(self):
        sp.previous_track()
    def queue_recs(self):
        self.thread_queue = QThread()
        self.worker_queue = Worker_Queue()
        self.worker_queue.moveToThread(self.thread_queue)

        self.thread_queue.started.connect(self.worker_queue.run)
        self.worker_queue.finished.connect(self.thread_queue.quit)
        self.worker_queue.finished.connect(self.worker_queue.deleteLater)
        self.thread_queue.finished.connect(self.thread_queue.deleteLater)

        self.thread_queue.start()

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())


