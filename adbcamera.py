# Camera control

import subprocess, time

import config

class camera(object):

	def __init__(self):
		# Power status
		self.status = False
		# Keep a list of pics we've taken
		self.pics = []

		# Get the starting list of files
		self.old_files = []
		self.rebase_file_list()

		self.session = []


	def power_toggle(self):
		print 'adb toggle power'
		ret = subprocess.call('adb shell "input keyevent KEYCODE_POWER"', shell=True)
		if ret == 0:
			self.status = not self.status


	def take(self):
		print 'adb taking photo'
		subprocess.call('adb shell "input keyevent KEYCODE_CAMERA"', shell=True)
		time.sleep(5)
		#self.check_take()


	# Wait for the photo to be saved before moving on
	def check_take(self):
		time.sleep(5)
		i = 0
		while not len(self.get_new()) > 0:
			if i > 5:
				return
			i += 1
			print 'Waiting for save...'
			time.sleep(0.75)

	# Get the latest file
	def get_new(self):

		new_files = []

		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)
		total_files = dir_list.splitlines()

		for f in total_files:
			if f not in self.old_files and f not in self.session:
				new_files.append(f)
				self.session.append(f)
				print 'new photo: ', f

		return new_files

	def rebase_file_list(self):
		# Update oldfiles
		self.old_files = []
		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)
		dir_list = dir_list.splitlines()

		for f in dir_list:
			self.old_files.append(f)

	def download_session(self):

		# Copy all the new files
		for f in self.session:
			# Then copy it from the camera
			ret = subprocess.call('adb pull /sdcard/DCIM/Camera/'+f+' '+config.file_path+f, shell=True)
			print 'Downloaded:', '/sdcard/DCIM/Camera/'+f, ', to: ', config.file_path+f

			if ret != 0:
				return False

		downloaded_files = self.session

		self.rebase_file_list()
		self.session = []

		return downloaded_files



