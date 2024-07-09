from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
import math
import time
from Model.Arduino_communication import ArduinoCommunicator
import Model.LLM as LLM

def trigger_video(mainwindow):
    if mainwindow.fullscreen_window != None:
        mainwindow.fullscreen_window.show_mp4_video()



#run the pose estimation model and the puzzle code
def Puzzle(mainwindow):
    #detect one hand raised
    print("got to Puzzle()")
    while True: #the Start_Puzzle flag is set to True once the clue screen has been displayed for about 10 seconds
        if mainwindow.fullscreen_window.Start_Puzzle == True:
            mainwindow.fullscreen_window.Start_Puzzle = False
            break

    mainwindow.fullscreen_window.show_camera_frame()
    pose_model = model = YOLO("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/yolov8n-pose.pt")
    model = YOLO("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/yolov8m.pt")
    selected_classes = [65, 67]
    IDX = 1 #for keeping track of frames so I can check for prop every 30 frames
    I_success = False
    vid_cap = cv2.VideoCapture(0) #capture images from webcam
    while (vid_cap.isOpened()):
        success, image = vid_cap.read()
        if success:
            if IDX % 30 == 0: #amend this later to do sliding window to check for prop several times rather than just once
                print("looking for prop")
                prediction = model.predict(source=image, device="mps", verbose=False, conf=0.80, iou=0.3)[0]
                detections = sv.Detections.from_ultralytics(prediction)
                detections = detections[
                    np.isin(detections.class_id, selected_classes)]  # just give me cell phone detections
                if detections:
                    LLM.ask_for_input(mainwindow)
            else:
                #image = cv2.resize(image, (shape))
                black_mask = np.zeros_like(image)
                obj_det_result = pose_model.predict(source=image, device="mps", verbose=False, conf=0.45, iou=0.3)
                # get xy coordinates of pose results - can't use supervision for this yet
                r = obj_det_result[0]
                res_list = r.keypoints.xy.tolist()  # have to turn the results tensor into a list to access the inner items
                #I_success = False
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
                                #print("Left Wrist Angle:", left_angle)
                                if left_angle < 0:
                                    left_colour = (0,255,0)
                                else:
                                    left_colour = (0,0,255)
                                    #draw line connecting nose and left wrist
                                cv2.line(black_mask, (int(nose[0]), int(nose[1])), (int(left_wrist[0]-50), int(left_wrist[1])),
                                         left_colour, 2)
                                if left_angle < -65: #means the left wrist is raised straight up signfying an 'I'

                                    I_success = True

                            if int(sum(right_wrist)) != 0:
                                right_angle = calculate_angle(nose, right_wrist)
                                #print("Right Wrist Angle:", right_angle)
                                if right_angle < 0:
                                    right_colour = (0,255,0)
                                else:
                                    right_colour = (0,0,255)
                                    # draw line connecting nose and right wrist
                                cv2.line(black_mask, (int(nose[0]), int(nose[1])), (int(right_wrist[0]+50), int(right_wrist[1])),
                                    right_colour, 2)
                                if -110 <= right_angle <= -90:

                                    I_success = True #means the right wrist is raised straight up signfying an 'I'

                            #if I_success == False: #i.e. this particular result was not an I but might be a V, so put result in list to loop through below
                            v_candidates.append((left_angle,right_angle))
                            if I_success == True and mainwindow.lock_switch._checked == False:  #if an 'I' was detected, then send message to arduino
                                #change the _checked value and ToggleSwitch on GUI which automatically sends the arduino message with correct value
                                mainwindow.lock_switch.toggle()
                                print("I shape!")
                                time.sleep(3)
                            elif I_success == True and mainwindow.lock_switch._checked == True:  #if I has been detected in the past and the box is currently locked then check for V shapes
                                for v in v_candidates:
                                    if -50 <= v[0] <= -30 and -160 <= v[1] <= -140:  # if the left and right wrists are at v angle
                                        mainwindow.lock_switch.toggle()
                                        print("v shape!")
                                        time.sleep(3)
                                        mainwindow.fullscreen_window.show_unlock_screen()
                                        return '1234'

            #connect to the FullScreenWindow
            mainwindow.fullscreen_window.frame_received.emit(black_mask)
            IDX += 1

            #cv2.imshow("Puzzle", black_mask)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

            #once you have looped through all the results, if there was an 'I', then display sound and now check for 'V'
            #if I_success == True:
            #    for v in v_candidates:
            #        if -50 <= v[0] <= -30 and -160 <= v[1] <= -140:#if the left and right wrists are at v angle
            #            mainwindow.lock_switch.toggle()
            #            print("v shape!")

            #            return '1234'

def calculate_angle(nose, wrist):
    """Calculate the angle between the nose and a wrist point."""
    dx = wrist[0] - nose[0]
    dy = wrist[1] - nose[1]
    return math.degrees(math.atan2(dy, dx))
