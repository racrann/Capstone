from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QDialog
from PyQt6.QtGui import QIcon, QPixmap, QMovie, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, pyqtSlot, QObject, QTimer, QRect
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
                                            REDIRECT_URI,scope = SCOPE, requests_session= False))

class Worker_Queue(QObject):
    finished = pyqtSignal()
    def run(self):
        import black_list
        black_list.make_file()
        import knn
        knn.queue_recs()
        self.finished.emit()

class Worker_Recs_Top(QObject):
    finished = pyqtSignal()
    
    def run(self):
        from rec_files import pull_top_songs, make_files
        track_ids = pull_top_songs()
        make_files(track_ids)
        self.finished.emit()

class Worker_Recs_Playlist(QObject):
    finished = pyqtSignal()

    @pyqtSlot(int)
    def run(self, value):
        from user_files import grab_user_playlist, make_files
        track_ids = grab_user_playlist(value)
        make_files(track_ids)
        self.finished.emit()

class Worker_Recs_Q(QObject):
    finished = pyqtSignal()

    def run(self):
        from rec_files import pull_query_songs_playlist, make_files
        track_ids = pull_query_songs_playlist(self.get_query)
        make_files(track_ids)
        self.finished.emit()

    @pyqtSlot(str)
    def get_query(string):
        return string

class Worker_Recent(QObject):
    finished = pyqtSignal()

    def run(self):
        from user_files import grab_recent, make_files
        track_ids = grab_recent()
        make_files(track_ids)
        self.finished.emit()

class GraphicButton(QPushButton):
    pass
class MovieLabel(QLabel):
    pass

class Window(QWidget):
    ind = pyqtSignal(int)
    q_sig = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("Music Recommendation System")

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        

        button = QPushButton('COLLECT RECENT LISTENING', self)
        button.clicked.connect(self.user_data_recent)
        button.setToolTip('COLLECT YOUR MOST RECENT 50 SONGS TO BASE RECS OFF OF')
        self.layout.addWidget(button, 0, 0)
        
        uplay_dropdown = QComboBox()
        uplay_dropdown.setPlaceholderText('PICK A USER PLAYLIST')
        results = sp.current_user_playlists()
        for idx, item in enumerate(results['items']):
            playlist = item['name']
            uplay_dropdown.addItem(playlist)
        uplay_dropdown.setToolTip('PICK A PLAYLIST OF YOURS TO BASE RECS OFF OF')
        uplay_dropdown.activated.connect(self.pick_uplay)
        self.layout.addWidget(uplay_dropdown, 0, 1)

        button = QPushButton('COLLECT TOP SONGS', self)
        button.setToolTip('COLLECT TOP CHARTERS TO PIC RECS FROM')
        button.clicked.connect(self.rec_files_top)
        self.layout.addWidget(button, 0, 2)

        self.q_box = QLineEdit(self)
        self.q_box.setFixedWidth(70)
        self.q_box.setPlaceholderText("METAL")
        self.layout.addWidget(self.q_box, 0, 3)

        button = QPushButton('ENTER SEARCH TERM', self)
        button.clicked.connect(self.rec_files_q)
        button.setToolTip('SEARCH FOR KEYWORD TO BASE RECOMMENDATIONS OFF OF')
        self.layout.addWidget(button, 0, 4)


        button = GraphicButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/play.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.play_pause)
        self.layout.addWidget(button, 10, 2, alignment = Qt.AlignmentFlag.AlignLeft)

        button = GraphicButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/ffw.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.ffw)
        self.layout.addWidget(button, 10, 3, alignment = Qt.AlignmentFlag.AlignLeft)

        button = GraphicButton(self)
        button.setGeometry(200,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/rew.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.rew)
        self.layout.addWidget(button, 10, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        self.queue_button = QPushButton('QUEUE RECOMMENDATIONS', self)
        self.queue_button.clicked.connect(self.queue_recs)
        self.queue_button.setToolTip('QUEUE SELECTED RECOMMENDATION AFTER PICKING A CATEGORY ABOVE')
        self.layout.addWidget(self.queue_button, 10,0, alignment = Qt.AlignmentFlag.AlignCenter)

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

        bbox = QLabel()
        self.layout.addWidget(bbox, 4, 4, 7, 1)
        self.queue = sp.queue()['queue']
        if sp.currently_playing() != None:
            self.label_1 = QLabel(f'{self.queue[0]['name']} - {self.queue[0]['artists'][0]['name']}')
            self.layout.addWidget(self.label_1, 4, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_2 = QLabel(f'{self.queue[1]['name']} - {self.queue[1]['artists'][0]['name']}')
            self.layout.addWidget(self.label_2, 5, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_3 = QLabel(f'{self.queue[2]['name']} - {self.queue[2]['artists'][0]['name']}')
            self.layout.addWidget(self.label_3, 6, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_4 = QLabel(f'{self.queue[3]['name']} - {self.queue[3]['artists'][0]['name']}')
            self.layout.addWidget(self.label_4, 7, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_5 = QLabel(f'{self.queue[4]['name']} - {self.queue[4]['artists'][0]['name']}')
            self.layout.addWidget(self.label_5, 8, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_6 = QLabel(f'{self.queue[5]['name']} - {self.queue[5]['artists'][0]['name']}')
            self.layout.addWidget(self.label_6, 9, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.label_7 = QLabel(f'{self.queue[6]['name']} - {self.queue[6]['artists'][0]['name']}')
            self.layout.addWidget(self.label_7, 10, 4, 1, 1, Qt.AlignmentFlag.AlignLeft)

        timer_3 = QTimer(self)
        timer_3.setInterval(2000)
        timer_3.timeout.connect(self.show_queue)
        timer_3.start()

        button = GraphicButton(self)
        button.setGeometry(150,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/dislike.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.dislike_song)
        button.setToolTip('remove song from future recommendations')
        self.layout.addWidget(button, 9, 3, alignment = Qt.AlignmentFlag.AlignLeft)

        button = GraphicButton(self)
        button.setGeometry(150,150,100,100)
        button.setStyleSheet("border-radius : 50")
        button.setIcon(QIcon('C:/Users/racra/desktop/capstone stuff/capstone/back/img/add.png'))
        button.setIconSize(QSize(75,75))
        button.clicked.connect(self.add_song)
        button.setToolTip('add song to your liked songs on Spotify')
        self.layout.addWidget(button, 9, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        self.loading = MovieLabel(self)
        self.loading.setGeometry(QRect(0, 0, 200, 200)) 
        self.loading.setMinimumSize(QSize(200, 200)) 
        self.loading.setMaximumSize(QSize(200, 200)) 
        self.loading.setObjectName("lb") 
        self.movie = QMovie('C:/Users/racra/Desktop/capstone stuff/Capstone/back/img/loading.gif')
        self.layout.addWidget(self.loading, 8, 0, 2, 2, alignment = Qt.AlignmentFlag.AlignLeft)
        self.loading.setMovie(self.movie) 

        self.layout.setContentsMargins(50,20,50,20)
        self.layout.setSpacing(10)
    
    def show_loading(self):
        self.loading.setHidden(False) 
        self.movie.start()
    def hide_loading(self):
        self.loading.setHidden(True)

    def dislike_song(self):
        import black_list
        if not os.path.exists('black_list.csv'):
            black_list.make_file
        if sp.currently_playing() != None:
            black_list.add(sp.current_user_playing_track()['item']['id'])
            sp.next_track()
    
    def add_song(self):
        song = []
        song.append(sp.current_user_playing_track()['item']['id'])
        sp.current_user_saved_tracks_add(song)
    
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
        self.thread_recent = QThread()
        self.worker_recent = Worker_Recent()
        self.worker_recent.moveToThread(self.thread_recent)
        self.thread_recent.started.connect(self.show_loading)
        self.thread_recent.finished.connect(self.hide_loading)
        self.thread_recent.started.connect(self.worker_recent.run)
        self.worker_recent.finished.connect(self.thread_recent.quit)
        self.worker_recent.finished.connect(self.worker_recent.deleteLater)
        self.thread_recent.finished.connect(self.thread_recent.deleteLater)
        self.thread_recent.start()

    def rec_files_top(self):
        self.thread_top = QThread()
        self.worker_rec_top = Worker_Recs_Top()
        self.worker_rec_top.moveToThread(self.thread_top)
        self.thread_top.started.connect(self.show_loading)
        self.thread_top.finished.connect(self.hide_loading)
        self.thread_top.started.connect(self.worker_rec_top.run)
        self.worker_rec_top.finished.connect(self.thread_top.quit)
        self.worker_rec_top.finished.connect(self.worker_rec_top.deleteLater)
        self.thread_top.finished.connect(self.thread_top.deleteLater)

        self.thread_top.start()
    def pick_uplay(self, index):
        self.ind.emit(index)
        
        self.thread_u = QThread()
        self.worker_u = Worker_Recs_Top()
        self.worker_u.moveToThread(self.thread_u)
        self.thread_u.started.connect(self.show_loading)
        self.thread_u.finished.connect(self.hide_loading)
        self.thread_u.started.connect(self.worker_u.run)
        self.worker_u.finished.connect(self.thread_u.quit)
        self.worker_u.finished.connect(self.worker_u.deleteLater)
        self.thread_u.finished.connect(self.thread_u.deleteLater)

        self.thread_u.start()

    def rec_files_q(self):
        query = self.q_box.text()
        self.q_sig.emit(query)

        self.thread_q = QThread()
        self.worker_q = Worker_Recs_Q()
        self.worker_q.moveToThread(self.thread_q)
        self.thread_q.started.connect(self.show_loading)
        self.thread_q.finished.connect(self.hide_loading)
        self.thread_q.started.connect(self.worker_q.run)
        self.worker_q.finished.connect(self.thread_q.quit)
        self.worker_q.finished.connect(self.worker_q.deleteLater)
        self.thread_q.finished.connect(self.thread_q.deleteLater)
        self.thread_q.start()
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
        self.thread_queue.started.connect(self.show_loading)
        self.thread_queue.finished.connect(self.hide_loading)
        self.thread_queue.started.connect(self.worker_queue.run)
        self.worker_queue.finished.connect(self.thread_queue.quit)
        self.worker_queue.finished.connect(self.worker_queue.deleteLater)
        self.thread_queue.finished.connect(self.thread_queue.deleteLater)
        self.thread_queue.start()     

app = QApplication(sys.argv)
with open('C:\\Users\\racra\\Desktop\\capstone stuff\\Capstone\\back\\stylesheet.qss', 'r') as f:
    style = f.read()
    app.setStyleSheet(style)

id = QFontDatabase.addApplicationFont("C:\\Users\\racra\\Desktop\\capstone stuff\\Capstone\\back\\Quicksand.ttf")
font = QFont("Quicksand")
app.setFont(font)
window = Window()
window.show()
sys.exit(app.exec())


