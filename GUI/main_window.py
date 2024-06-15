from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QSize

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
        self.video_widget = VideoWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.video_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



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

