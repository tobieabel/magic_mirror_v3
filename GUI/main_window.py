from PyQt5.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QStackedLayout, \
    QApplication, QFileDialog, QComboBox
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import shutil
import os
import glob
import Model.object_detection
from Model.object_detection import video_update
import cv2
import numpy as np
import time

#video_file_path = '/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/uploads/Scary_NunV3.mp4'
uploads_dir = '/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/uploads/'
video_file_path = os.path.join(uploads_dir, 'Scary_NunV3.mp4')  # Initial hardcoded path



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
        self.upload_button = QPushButton('Upload Video')
        self.upload_button.setFixedSize(QSize(150, 50))
        self.video_picklist = QComboBox()
        self.video_picklist.setFixedSize(QSize(300, 50))
        self.video_widget = VideoWidget()
        self.fullscreen_window = None

        # Connect the upload button to the upload method
        self.upload_button.clicked.connect(self.upload_video)
        self.video_picklist.currentIndexChanged.connect(self.select_video)

        # Populate video picklist
        self.update_video_picklist()

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.puzzle_button)
        button_layout.addWidget(self.upload_button)

        # Create a vertical layout and add the button layout and video widget
        layout = QVBoxLayout()
        layout.addLayout(button_layout)  # Add the horizontal button layout
        layout.addWidget(self.video_picklist)
        layout.addWidget(self.video_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_fullscreen_window(self):
        self.fullscreen_window = FullScreenWindow()


    def upload_video(self):
        """
        Handle video file upload and save it to the uploads directory.
        """
        global video_file_path

        # Open file dialog to select video file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4)")

        if file_path:
            # Save the selected video to the uploads directory
            video_name = os.path.basename(file_path)
            target_path = os.path.join(uploads_dir, video_name)
            shutil.copy(file_path, target_path)
            video_file_path = target_path
            print(f"Uploaded video path: {video_file_path}")

    def update_video_picklist(self):
        """
        Update the video picklist with MP4 files in the uploads directory.
        """
        self.video_picklist.clear()
        mp4_files = glob.glob(os.path.join(uploads_dir, "*.mp4"))
        if mp4_files:
            for file_path in mp4_files:
                self.video_picklist.addItem(os.path.basename(file_path), file_path)

    def select_video(self):
        """
        Update the video_file_path based on the picklist selection.
        """
        global video_file_path
        selected_video = self.video_picklist.currentData()
        if selected_video:
            video_file_path = selected_video
            print(f"Selected video path: {video_file_path}")

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
    frame_received = pyqtSignal(object)
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
        self.connection_frame_received = self.frame_received.connect(self.update_frame) #connect signal to show camera frame function

        # Black screen with puzzle_text layout
        self.clue_widget = QLabel('To Open the box,\nMake the number you see,\nRed lights turn green,\nWith an I before V')
        self.clue_widget.setAlignment(Qt.AlignCenter)
        self.clue_widget.setStyleSheet("background-color: black; color: gold;")
        font = QFont("Arial", 48, QFont.Bold)
        self.clue_widget.setFont(font)
        self.stacked_layout.addWidget(self.clue_widget)

        # Black screen without text layout
        self.black_screen_widget = QWidget(self)
        self.black_screen_widget.setStyleSheet("background-color: black;")
        self.stacked_layout.addWidget(self.black_screen_widget)



        # Media player setup
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.play_video_signal.connect(self.show_mp4_video)
        self.stacked_layout.addWidget(self.video_widget)

        self.setLayout(self.stacked_layout)

    def move_to_monitor(self, monitor_index):
        screen = QApplication.screens()[monitor_index]
        self.move(screen.geometry().x(), screen.geometry().y())
        self.resize(screen.size())

    def update_frame(self,frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.camera_frame_label.setPixmap(pixmap)
        self.camera_frame_label.setAlignment(Qt.AlignCenter)
        print('Puzzle update frame reached')

    def show_camera_frame(self):
        self.stacked_layout.setCurrentIndex(0)


    def show_clue_screen(self):
        self.stacked_layout.setCurrentIndex(1)


    def show_black_screen(self):
        self.stacked_layout.setCurrentIndex(2)

    def show_mp4_video(self):
        """
        Play the specified MP4 video in full screen mode and close the window when done.
        """
        video_path=video_file_path
        self.stacked_layout.setCurrentIndex(3)
        video_url = QUrl.fromLocalFile(video_path)
        self.media_player.setMedia(QMediaContent(video_url))
        self.media_player.play()
        print("playing ",video_file_path)

    def on_media_status_changed(self, status):
        """
        Handles any changes in media status automatically - used to close the window when the video finishes.
        """
        if status == QMediaPlayer.EndOfMedia:
            self.show_clue_screen()
            #self.close_FullScreenWindow() #don't need this function at the moment, but keep for future

    def close_FullScreenWindow(self):
        self.close()  # Close the window completely
        self.deleteLater()  # Schedule the QWidget for deletion


    def closeEvent(self, event):
        """
        Handles the close event to ensure camera is released properly.
        """
        print("closeEvent called")  # Debugging output
        self.media_player.stop()  # Stop the media player
        event.accept()




