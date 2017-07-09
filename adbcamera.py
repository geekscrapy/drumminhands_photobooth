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


	def power_toggle(self):
		print 'adb powering on'
		ret = subprocess.call('adb shell "input keyevent KEYCODE_POWER"', shell=True)
		if ret == 0:
			self.status = not self.status


	def take(self):
		print 'adb taking photo'
		subprocess.call('adb shell "input keyevent KEYCODE_CAMERA"', shell=True)
		check_take()


	# Wait for the photo to be saved before moving on
	def check_take(self):
		while not len(get_new()) > 0:
			print 'Waiting for save...'
			time.sleep(0.5)


	# Get the latest file
	def get_new(self):

		new_files = []

		dir_list = subprocess.check_output('adb shell ls /sdcard/DCIM/Camera/', shell=True)
		total_files = dir_list.splitlines()

		for f in total_files:
			if f not in self.old_files:
				new_files.append(f)
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

		self.rebase_file_list()

		return new_files



