from PyQt5.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QStackedLayout, QApplication
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

import Model.object_detection
from Model.object_detection import video_update
import cv2
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Magic Mirror')
        self.setGeometry(100, 100, 800, 600)

        self.start_button = QPushButton('Start')
        self.start_button.setFixedSize(QSize(100, 50))
        self.stop_button = QPushButton('Stop')
        self.stop_button.setFixedSize(QSize(100, 50))
        self.puzzle_button = QPushButton('Play Puzzle')
        self.puzzle_button.setFixedSize(QSize(100, 50))
        self.video_widget = VideoWidget()
        self.fullscreen_window = None

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.puzzle_button)

        # Create a vertical layout and add the button layout and video widget
        layout = QVBoxLayout()
        layout.addLayout(button_layout)  # Add the horizontal button layout
        layout.addWidget(self.video_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_fullscreen_window(self):
        self.fullscreen_window = FullScreenWindow()




class VideoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)
        self.black_frame()
    def update_frame(self, frame, blackframe=False):
        """
        Update the video frame displayed in the widget.

        Parameters:
        frame (numpy.ndarray): The video frame to display.
        """
        self.blackframe = blackframe
        if Model.object_detection.pipelineend is False or blackframe is True: #only update the front end if the pipeline has not been stopped, or its a black frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.video_label.setPixmap(pixmap)
            self.video_label.setAlignment(Qt.AlignCenter)
            print("update frame function reached")


    def black_frame(self):
        """
        Display a black frame on the video label.
        """
        height, width = self.video_label.height(), self.video_label.width()
        black_frame = np.zeros((height, width, 3), np.uint8)
        self.update_frame(black_frame, True)
        print("black frame should appear")



    def connect_signal(self):
        self.connection_frame_ready = video_update.frame_ready.connect(self.update_frame)  # QT slot to connect front end video widget to back end video update function



    def disconnect_signal(self):
        video_update.frame_ready.disconnect(self.connection_frame_ready)  # Disconnect the signal
        video_update.terminate_pipeline.disconnect(self.connection_terminate_pipeline)  # Disconnect the signal

#widget for displaying a seperate screeen on a given monitor for the puzzle
class FullScreenWindow(QWidget):
    frame_received = pyqtSignal(QImage)
    play_video_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Full Screen Window')
        self.setWindowFlag(Qt.FramelessWindowHint)  # No border

        self.stacked_layout = QStackedLayout()

        # Camera frame layout
        self.camera_frame_label = QLabel(self)
        self.camera_frame_label.setAlignment(Qt.AlignCenter)
        self.stacked_layout.addWidget(self.camera_frame_label)

        # Black screen with puzzle_text layout
        self.clue_widget = QLabel('This is a clue to the puzzle', self)
        self.clue_widget.setAlignment(Qt.AlignCenter)
        self.clue_widget.setStyleSheet("background-color: black; color: gold;")
        font = QFont("Arial", 48, QFont.Bold)
        self.clue_widget.setFont(font)
        self.stacked_layout.addWidget(self.clue_widget)

        # Black screen without text layout
        self.black_screen_widget = QWidget(self)
        self.black_screen_widget.setStyleSheet("background-color: black;")
        self.stacked_layout.addWidget(self.black_screen_widget)

        self.setLayout(self.stacked_layout)

        # Media player setup
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

    def move_to_monitor(self, monitor_index):
        screen = QApplication.screens()[monitor_index]
        self.move(screen.geometry().x(), screen.geometry().y())
        self.resize(screen.size())


    def show_camera_frame(self):
        self.camera = cv2.VideoCapture(0)  # Use the first camera
        self.stacked_layout.setCurrentIndex(0)


    def show_clue_screen(self):
        self.stacked_layout.setCurrentIndex(1)

    def show_black_screen(self):
        self.stacked_layout.setCurrentIndex(2)

    def play_mp4_video(self, video_path):
        """
        Play the specified MP4 video in full screen mode and close the window when done.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.video_widget)

        video_url = QUrl.fromLocalFile(video_path)
        self.media_player.setMedia(QMediaContent(video_url))
        self.showFullScreen()
        self.media_player.play()

    def on_media_status_changed(self, status):
        """
        Handle changes in media status to close the window when the video finishes.
        """
        if status == QMediaPlayer.EndOfMedia:
            self.close_FullScreenWindow()

    def close_FullScreenWindow(self):
        self.close()  # Close the window completely
        self.deleteLater()  # Schedule the QWidget for deletion


    def closeEvent(self, event):
        """
        Handles the close event to ensure camera is released properly.
        """
        print("closeEvent called")  # Debugging output
        self.mdeia_player.stop()  # Stop the media player
        event.accept()




