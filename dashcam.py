import cv2
import datetime
import os
import threading
import psutil
import shutil
import time
import RPi.GPIO as GPIO 



class Camera():
	""" create class for new cameras """
	

	def __init__(self, cam_id, frame_rate = 15):
		self.cameras = {0:'A', 1:'B',2:'C',3:'D', 4:'E'}
		self.cam_id = cam_id
		self.frame_rate = frame_rate

	def record(self, path, name, stop, time_stamp = True):
		"""create record object and record videos to file"""
		cap = cv2.VideoCapture(self.cam_id)
		vid_cod = cv2.VideoWriter_fourcc('M','P','E','G')
		tname = self.cameras[self.cam_id] + name + '.mp4'

		output = cv2.VideoWriter(os.path.join(path,name,tname), vid_cod, self.frame_rate, (640,480)) #TODO name done

		while(cap.isOpened()):
		    ret, frame = cap.read()
		    if stop():
		    	cap.release()
				output.release()
				cv2.destroyAllWindows()
				break
		    if ret==True:
		        #frame = cv2.flip(frame,0)
		        if time_stamp:
					tstamp = str(datetime.datetime.now()).split('.')[0]
					frame = cv2.putText(frame, tstamp, (450,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)

		        # write the flipped frame
		        output.write(frame)


class Management():
	"""Manage cameras and  video folders"""

	def __init__(self, path, memory_gb = 0.5, del_files_count = 20):
		self.path = os.path.join(path,'rpi_dashcam')
		if not os.path.exists(self.path)
			os.mkdir(self.path)
		self.memory_gb = memory_gb
		self.del_files_count = del_files_count
 

	def new_record(self):  
	"""creates a new folder for saving video from session"""
		tstamp = str(datetime.datetime.now()).split('.')[0].replace(':','_')
 		os.mkdir(os.path.join(self.path,tstamp))
		return self.path, tstamp


	def begin_record(self, camera_frame_rate):  # 
	"""creates threads for parallel recording of video"""
		camera_obj=[]
		camera_thread = []
		self.stop_threads = False
		date = self.new_record()
		for x, frm in enumerate(camera_frame_rate):
			camera_obj.append(Camera(x,frm))
			camera_thread.append(threading.Thread(target = camera_obj[x].record, args = (date[0], date[1], lambda : self.stop_threads,)))    # TODO add thread done
			camera_thread[x].start()
		self.start_time = time.time()
		return camera_thread


	def delete_folders(self):  # delete old image data, make more space
		""" delete old videos depending on memory left"""
		while True:
			disk = psutil.disk_usage(self.path)
			while len(os.listdir(self.path)) > self.del_files_count or (disk.free // (2**30)) < self.memory_gb:   #TODO change shutil/ psutil for 2.7/3.7
				file = 	os.listdir(self.path)
				file.sort()
				shutil.rmtree(os.path.join(self.path,file[0]))
				disk = psutil.disk_usage(self.path)
			time.sleep(30*60)


	def shutdown_pi(self, camera_thread):
		""" stop recording from all cameras, switch off the pi"""
		# GPIO.cleanup()
		self.stop_threads = True
		for x in camera_thread:
			x.join()
		os.system("sudo shutdown -h now")


	def GPIO_setup(self, port = 17):
		""" setup  GPIO to detect external interrupt"""
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.add_event_detect(port, GPIO.FALLING, callback=self.shutdown_pi, bouncetime=300)


def main():
	camera_frame_rate = [15]  # add framerate for each camera, adjust if video length doesn't match real time
	record_time = 60   # how long each video should be
	path = '/media/pi/Lexar/'  # file path to main save location
	m = Management(path) 

	mt1 = threading.Thread(target = m.delete_folders)
	mt1.daemon = True	
	mt1.start()	
	camera_thread = m.begin_record(camera_frame_rate)
	m.GPIO_setup()

	while True:
		time.sleep(60)
		if int(time.time() - m.start_time) > 60*record_time:
			m.stop_threads = True
			for x in camera_thread:
				x.join()
			m.stop_threads = False
			camera_thread = m.begin_record(camera_frame_rate)


main()

