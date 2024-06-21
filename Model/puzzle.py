from ultralytics import YOLO
import cv2
import numpy as np
import math
import time


def trigger_video(mainwindow):
    if mainwindow.fullscreen_window != None:
        mainwindow.fullscreen_window.show_mp4_video()


#run the pose estimation model and the puzzle code
def Puzzle(mainwindow):
    #detect one hand raised
    print("got to Puzzle()")
    time.sleep(15)
    mainwindow.fullscreen_window.show_camera_frame()
    pose_model = model = YOLO("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/yolov8n-pose.pt")
    vid_cap = cv2.VideoCapture(0) #capture images from webcam
    while (vid_cap.isOpened()):
        success, image = vid_cap.read()
        if success:
            #image = cv2.resize(image, (shape))
            black_mask = np.zeros_like(image)
            obj_det_result = pose_model.predict(source=image, device="mps", verbose=False, conf=0.45, iou=0.3)
            # get xy coordinates of pose results - can't use supervision for this yet
            r = obj_det_result[0]
            res_list = r.keypoints.xy.tolist()  # have to turn the results tensor into a list to access the inner items
            I_success = False
            v_candidates = []
            for i in res_list:
                if len(i) > 0:  # if there are some results
                    left_wrist = i[9]
                    right_wrist = i[10]
                    nose = i[0]
                    left_angle = 0
                    right_angle = 0
                    #calculate the angle of each wrist to the nose and print the angle to the terminal

                    if int(sum(nose)) != 0:  # only draw on the gaze if you can see the nose
                        cv2.circle(black_mask,(int(nose[0]), int(nose[1])),10,(255,255,255),thickness=-1,)
                        if int(sum(left_wrist)) != 0:
                            left_angle = calculate_angle(nose, left_wrist)
                            print("Left Wrist Angle:", left_angle)
                            if left_angle < 0:
                                left_colour = (0,255,0)
                            else:
                                left_colour = (0,0,255)
                                #draw line connecting nose and left wrist
                            cv2.line(black_mask, (int(nose[0]), int(nose[1])), (int(left_wrist[0]-50), int(left_wrist[1])),
                                     left_colour, 2)
                            if left_angle < -65:
                                time.sleep(3)
                                I_success = True

                        if int(sum(right_wrist)) != 0:
                            right_angle = calculate_angle(nose, right_wrist)
                            print("Right Wrist Angle:", right_angle)
                            if right_angle < 0:
                                right_colour = (0,255,0)
                            else:
                                right_colour = (0,0,255)
                                # draw line connecting nose and right wrist
                            cv2.line(black_mask, (int(nose[0]), int(nose[1])), (int(right_wrist[0]+50), int(right_wrist[1])),
                                right_colour, 2)
                            if -110 <= right_angle <= -90:

                                time.sleep(3)
                                I_success = True

                        if I_success == False: #i.e. this particular result was not an I but might be a V
                            v_candidates.append((left_angle,right_angle))
            #connect to the FullScreenWindow
            mainwindow.fullscreen_window.frame_received.emit(black_mask)
            #cv2.imshow("Puzzle", black_mask)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

            #once you have looped through all the results, if there was an 'I', then display sound and now check for 'V'
            if I_success == True:
                for v in v_candidates:
                    if -50 <= v[0] <= -30 and -160 <= v[1] <= -140:
                        print("v shape!")

                        return '1234'

def calculate_angle(nose, wrist):
    """Calculate the angle between the nose and a wrist point."""
    dx = wrist[0] - nose[0]
    dy = wrist[1] - nose[1]
    return math.degrees(math.atan2(dy, dx))
