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
shape=(640,480)
box_annotator = sv.BoxAnnotator()
video_file_path = '/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/uploads/Scary_NunV3.mp4'
#sv_polygons = None


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
        print(image.shape)
        image = cv2.resize(image, (shape)) #was making the predictions wrong, maybe I need to resize earlier in the process?
        print(image.shape)
        # run object detections
        prediction = model.predict(source=image, device="mps", verbose=False, conf=0.80, iou=0.3)[0]
        predictions.append(prediction)
    return predictions


def process_results(prediction: dict, video_frame:VideoFrame):
    #global sv_polygons
    if pipelineend == False: #stop processing once pipeline is closed - seems to carry on processing whats in the buffer for a few seconds
        detection_found = False#this is used to keep track of whether a detection has been found in the frame
        detections = sv.Detections.from_ultralytics(prediction)
        detections = detections[np.isin(detections.class_id, selected_classes)] #just give me cell phone detections
        if detections:
            detection_found = True
            no_of_detections = 0
            if sv_polygons is not None: #loop through the polygon zones and see if any of the detections are within them
                for i in sv_polygons:
                    if i.trigger(detections):
                        no_of_detections += 1
                if no_of_detections == 0: #if no detection was found within a polygon zone
                    detection_found = False
        print(detection_found)
        frame = video_frame.image
        frame = cv2.resize(frame, (shape)) #have the resize againhere to make the predictions correct on frame
        frame = box_annotator.annotate(frame, detections=detections, skip_label=True)
        #draw the polygon zones onto the frame so I can see where they are

        video_update.process_frame(frame)#send signal to main_window to update the video frame - uses global instance of ObjectDetection class

        if detection_found:
            pipeline.pause_stream() #this pauses the stream, not the threads
            #success = play_video(video_file_path)
            #print(success)
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





def Mains(sv_polygon_zones):
    global pipeline, pipelineend, sv_polygons
    sv_polygons = sv_polygon_zones
    pipelineend = False
    pipeline = InferencePipeline.init_with_custom_logic(
        video_reference=0, #webcam - can put an RTSP stream of URL to video here instead
        on_video_frame=process_image,
        on_prediction=process_results,
        )

    pipeline.start()

    pipelineend = True #stops further frames being sent to front end


video_update = ObjectDetection()