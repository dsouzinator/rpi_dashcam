import cv2
import datetime
import os
import shutil
import time
import RPi.GPIO as GPIO 
from multiprocessing import Process, Event

class Camera():

    def __init__(self, cam_id, frame_rate = 20):
        self.cameras = {0:'A', 1:'B',2:'C',3:'D', 4:'E'}
        self.cam_id = cam_id
        self.frame_rate = frame_rate

    def record(self, path, name, event):
        """create record object and record videos to file"""
        cap = cv2.VideoCapture(self.cam_id)
        vid_cod = cv2.VideoWriter_fourcc('M','P','E','G')
        tname = self.cameras[self.cam_id] + name + '.mp4'

        output = cv2.VideoWriter(os.path.join(path,name,tname), vid_cod, self.frame_rate, (640,480)) #TODO name done
        while(cap.isOpened()):
            ret, frame = cap.read()
            if event.is_set():
                cap.release()
                output.release()
                cv2.destroyAllWindows()
                break
            if ret==True:
                tstamp = str(datetime.datetime.now()).split('.')[0]
                frame = cv2.putText(frame, tstamp, (450,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                output.write(frame)


class Manager():
    """Manage cameras and  video folders"""
    def __init__(self, path, memory_gb = 0.5, del_files_count = 20):
        self.path = os.path.join(path,'rpi_dashcam')
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.memory_gb = memory_gb
        self.del_files_count = del_files_count

    def new_record(self):  
        """creates a new folder for saving video from session"""
        self.tstamp = str(datetime.datetime.now()).split('.')[0].replace(':','_')
        os.mkdir(os.path.join(self.path,self.tstamp))

    def delete_folders(self):
        """ delete old videos depending on memory left"""
        while True:
            disk = shutil.disk_usage(self.path)
            while len(os.listdir(self.path)) > self.del_files_count or (disk.free // (2**30)) < self.memory_gb:   
                file =  os.listdir(self.path)
                file.sort()

                shutil.rmtree(os.path.join(self.path,file[0]))
                disk = shutil.disk_usage(self.path)
            time.sleep(30*60)

    def initialize(self, camera_list):
        self.camera_obj = []
        self.processes = []
        self.new_record()
        self.event = Event()

        for x, fps in enumerate(camera_list):
            self.camera_obj.append(Camera(x,fps))
            self.processes.append(Process(target=self.camera_obj[x].record, args=(self.path, self.tstamp, self.event,)))
        self.start_time=time.time()
        for proc in self.processes:
            proc.start()


    def shutdown_pi(self):
        """ stop recording from all cameras, switch off the pi"""
        self.event.set()
        for x in self.processes:
            x.join()
        os.system("sudo shutdown -h now")


    def GPIO_setup(self, port = 17):
        """ setup  GPIO to detect external interrupt"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(port, GPIO.FALLING, callback=self.shutdown_pi, bouncetime=300)


if __name__ == '__main__':

    path = '/media/pi/Lexar/'
    record_duration = 60 # in minutes   
    camera_list = [29.82, 25]   # put the frame rate of each camera here in a list
    m = Manager(path)
    m.GPIO_setup()

    # memory managemet thread, set as daemon and forget 
    mt1 = Process(target = m.delete_folders)
    mt1.daemon = True
    mt1.start()

    m.initialize(camera_list)

    while True:
        time.sleep(50)
        if m.event.is_set():   # not to start a new process if shutdown has been initiated by GPIO pin
            break
        if int(time.time() - m.start_time) > 60*record_duration:
            m.event.set()
            time.sleep(1)
            for x in m.processes:
                x.join()
            m.event.clear()
            m.initialize(camera_list)

    while True:
        pass

