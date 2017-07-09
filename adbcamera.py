# Camera control

import subprocess

import config

class camera(object):

	def __init__(self):
		# Power status
		self.status = False
		# Keep a list of pics we've taken
		self.pics = []


	def power_toggle(self):
		ret = subprocess.call('adb shell "input keyevent KEYCODE_POWER"', shell=True)
		if ret == 0:
			self.status = not self.status

	def take(self):
		return subprocess.call('adb shell "input keyevent KEYCODE_CAMERA"', shell=True)

	def get_pic(self, filename):

		# Get the filename of the latest picture
		cmd = '"cd /sdcard/DCIM/Camera/; IFS=$\'\n\'; output=(`ls -l`); lines=${#output[@]}; IFS=$\' \'; file_line=(${output[$((lines-1))]}); file_name=(); index=0; for part in ${file_line[@]}; do if [[ $index -gt 4 ]]; then file_name+=($part); fi; index=$((index+1)); done; echo ${file_name[1]}"'
		cap_name = subprocess.check_output(['adb', 'shell', cmd], shell=True)

		if cap_name.upper().find('JPG') != -1:
			return False

		# Then copy it from the camera
		ret = subprocess.call('adb pull /sdcard/DCIM/Camera/'+cap_name+' '+config.file_path, shell=True)

		if ret != 0:
			return False

		# Then rename it to what we planned!
		ret = subprocess.call('mv '+config.file_path+cap_name+' '+config.file_path+filename, shell=True)
		if ret != 0:
			return False

		self.pics.append(config.file_path+filename)
		return True