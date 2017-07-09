# Camera control

import subprocess

import config

class camera(object):

	def __init__(self):
		# Power status
		self.status = False
		# Keep a list of pics we've taken
		self.pics = []

		# Get the starting list of files
		self.old_files = []
		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)
		for f in dir_list.split('\n'):
			self.old_files.append(f)

		# Total list of files created by this camera object
		self.session_files = []


	def power_toggle(self):
		ret = subprocess.call('adb shell "input keyevent KEYCODE_POWER"', shell=True)
		if ret == 0:
			self.status = not self.status

	def take(self):
		return subprocess.call('adb shell "input keyevent KEYCODE_CAMERA"', shell=True)

	# Get the latest file
	def get_latest(self):

		new_files = []

		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)

		for f in dir_list.split('\n'):
			if f not in self.old_files:
				new_files.append(f)
				self.session_files.append(f)

		return new_files


	def get_pic(self, filename):

		# Get the filename of the latest picture
		new_file = self.get_latest()

		# Then copy it from the camera
		ret = subprocess.call('adb pull /sdcard/DCIM/Camera/'+new_file+' '+config.file_path, shell=True)
		if ret != 0:
			return False

		# Then rename it to what we planned!
		ret = subprocess.call('mv '+config.file_path+new_file+' '+config.file_path+filename, shell=True)
		if ret != 0:
			return False

		return True

