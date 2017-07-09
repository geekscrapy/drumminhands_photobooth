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
		dir_list = dir_list.splitlines()

		for f in dir_list:
				self.old_files.append(f)

		# Total list of files created by this camera object
		self.session_files = []


	def power_toggle(self):
		print 'adb powering on'
		ret = subprocess.call('adb shell "input keyevent KEYCODE_POWER"', shell=True)
		if ret == 0:
			self.status = not self.status


	def take(self):
		print 'adb taking photo'
		subprocess.call('adb shell "input keyevent KEYCODE_CAMERA"', shell=True)


	# Get the latest file
	def get_new(self):

		new_files = []

		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)
		total_files = dir_list.splitlines()

		for f in total_files:
			if f not in self.old_files and not in self.session_files:
				new_files.append(f)
				self.session_files.append(f)
				print 'new photo: ', f

		return new_files


	def download_session(self):

		# Get the filename of the latest picture
		new_files = self.get_new()

		# Copy all the new files
		for f in new_files:
			# Then copy it from the camera
			ret = subprocess.call('adb pull /sdcard/DCIM/Camera/'+f+' '+config.file_path+f, shell=True)
			print 'Downloaded:', '/sdcard/DCIM/Camera/'+f, ', to: ', config.file_path+f

			if ret != 0:
				return False

			print 'Copied: ', f

		return new_files



