import cv2
import numpy as np
from ultralytics import YOLO
from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
import supervision as sv
import subprocess
import warnings
warnings.filterwarnings("ignore") #for supressing the annoying Supervision warnings
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread

pipeline=None
pipelineend = False
model = YOLO("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/yolov8m.pt")
selected_classes = [65,67]
shape=(640,640)
box_annotator = sv.BoxAnnotator()
video_file_path = '/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/uploads/Scary_NunV3.mp4'



def play_video(video_path):
    video_playback = subprocess.Popen(["/Applications/VLC.app/Contents/MacOS/VLC","--fullscreen", "--no-osd", video_path])
    video_playback.wait() #requires that the VLC application has the 'quit after playback' option selected
    #time.sleep(10) #if VLC won't quit after playback then use time.sleep for however long the video is
    #close the VLC application window using AppleScript - will need to change this for windows, but might be ble to use cvlc in windows anyway
    subprocess.run(["osascript", "-e", 'tell application "VLC" to quit'])

    return "Video Played"

def end_pipeline():
    if pipeline is not None:
        pipeline.terminate()#this just terminates the streams netly, not the threads
        print("pipeline terminated function reached")
        pipeline.join()#this terminates the threads

def process_image(video_frames: list[VideoFrame]):
    predictions = []
    for video_frame in video_frames:
        image = video_frame.image
        #image = cv2.resize(image, (shape)) #was making the predictions wrong, maybe I need to resize earlier in the process?
        print("new frame processed")
        # run object detections
        prediction = model.predict(source=image, device="mps", verbose=False, conf=0.80, iou=0.3)[0]
        predictions.append(prediction)
    return predictions


def process_results(prediction: dict, video_frame:VideoFrame):
    if pipelineend == False: #stop processing once pipeline is closed - seems to carry on processing whats in the buffer for a few seconds
        detections = sv.Detections.from_ultralytics(prediction)
        detections = detections[np.isin(detections.class_id, selected_classes)] #just give me cell phone detections
        print("new detection")
        frame = box_annotator.annotate(video_frame.image, detections=detections, skip_label=True)
        video_update.process_frame(frame)#send signal to main_window to update the video frame - uses global instance of ObjectDetection class

        if detections:
            pipeline.pause_stream() #this pauses the stream, not the threads
            success = play_video(video_file_path)
            print(success)
            video_update.terminate()#send signal to main_window to terminate the pipeline



class ObjectDetection(QObject):
    frame_ready = pyqtSignal(object)
    terminate_pipeline = pyqtSignal(object)

    def __init__(self):
        super(ObjectDetection, self).__init__()

    def process_frame(self, frame):
        # Emit the processed frame
        self.frame_ready.emit(frame)

    def terminate(self):
        self.terminate_pipeline.emit(None)





def Mains():
    global pipeline, pipelineend
    pipelineend = False
    pipeline = InferencePipeline.init_with_custom_logic(
        video_reference=0, #webcam - can put an RTSP stream of URL to video here instead
        on_video_frame=process_image,
        on_prediction=process_results,
        )

    pipeline.start()

    pipelineend = True #stops further frames being sent to front end


video_update = ObjectDetection()