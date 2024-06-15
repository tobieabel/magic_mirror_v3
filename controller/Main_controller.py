import threading
import Model.object_detection as od
import time
class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.start_button.clicked.connect(self.start_application)
        self.main_window.stop_button.clicked.connect(self.stop_application)
        self.thread = None

    def start_application(self):
        if self.thread is None or not self.thread.is_alive():
            self.main_window.video_widget.connect_signal() #connection to slot between video widget and object detection script
            od.video_update.terminate_pipeline.connect(self.Stop_Inference_pipeline) #connection between object detection script and main controller
            self.thread = threading.Thread(target=od.Mains)
            self.thread.start()


    def Stop_Inference_pipeline(self):
        od.end_pipeline()

        self.thread.join()
        self.thread = None
        # self.main_window.video_widget.disconnect_signal() #disconnect signal between front and back ends, think this is not needed to close threads
        print("threads terminated")
        self.main_window.video_widget.black_frame()
        # now call puzzle code



    def stop_application(self):
        # Code to stop the application
        if self.thread is not None:
            #self.main_window.video_widget.disconnect_signal() #disconnect signal between front and back ends, think this is not needed to close threads
            od.end_pipeline()

            self.thread.join()
            self.thread = None
            while od.pipelineend is False:
                time.sleep(0.1)
            print("threads terminated")
            self.main_window.video_widget.black_frame()

