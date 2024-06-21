import threading
import Model.object_detection as od
import Model.puzzle as puzzle
import time


class MainController:

    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.start_button.clicked.connect(self.start_application)
        self.main_window.stop_button.clicked.connect(self.stop_application)
        self.main_window.puzzle_button.clicked.connect(self.start_puzzle)
        self.thread_od = None
        self.thread_puzzle = None

    def start_application(self):

        if self.main_window.fullscreen_window !=None:
            self.main_window.fullscreen_window.show_black_screen()
            self.main_window.fullscreen_window.move_to_monitor(1)  # monitor 2 would be (index 1)
            self.main_window.fullscreen_window.showFullScreen()
        else:
            self.main_window.create_fullscreen_window()
            self.main_window.fullscreen_window.show_black_screen()
            self.main_window.fullscreen_window.move_to_monitor(1)  # monitor 2 would be (index 1)
            self.main_window.fullscreen_window.showFullScreen()

        if self.thread_od is None or not self.thread_od.is_alive():
            self.main_window.video_widget.connect_signal() #connection to slot between video widget and object detection script
            od.video_update.terminate_pipeline.connect(self.Stop_Inference_pipeline) #connection between object detection script and main controller
            self.thread_od= threading.Thread(target=od.Mains)
            self.thread_od.start()


    def Stop_Inference_pipeline(self):

        od.end_pipeline()
        self.thread_od.join()
        self.thread_od = None
        # self.main_window.video_widget.disconnect_signal() #disconnect signal between front and back ends, think this is not needed to close threads
        print("threads terminated")
        self.main_window.video_widget.black_frame()
        # now call puzzle code
        puzzle.trigger_video(self.main_window)
        if self.thread_puzzle is None:
            self.thread_puzzle = threading.Thread(target=lambda:puzzle.Puzzle(self.main_window))#if the function has parameters you need to specify it using a lambda function, otherwise python calls it immediately
            self.thread_puzzle.start()
            print("got here")






    def stop_application(self):
        # Code to stop the application
        if self.main_window.fullscreen_window != None:
            self.main_window.fullscreen_window.close_FullScreenWindow()
            self.main_window.fullscreen_window = None
        if self.thread is not None:
            #self.main_window.video_widget.disconnect_signal() #disconnect signal between front and back ends, think this is not needed to close threads
            od.end_pipeline()

            self.thread.join()
            self.thread = None
            while od.pipelineend is False:
                time.sleep(0.1)
            print("threads terminated")
            self.main_window.video_widget.black_frame()

    def start_puzzle(self):
        if self.main_window.fullscreen_window !=None:
            self.main_window.fullscreen_window.show_clue_screen()
            self.main_window.fullscreen_window.move_to_monitor(1)  # monitor 2 would be (index 1)
            self.main_window.fullscreen_window.showFullScreen()
        else:
            self.main_window.create_fullscreen_window()
            self.main_window.fullscreen_window.show_clue_screen()
            self.main_window.fullscreen_window.move_to_monitor(1)  # monitor 2 would be (index 1)
            self.main_window.fullscreen_window.showFullScreen()



