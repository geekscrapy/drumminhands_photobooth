# Camera control

import config

class camera(object):

	def __init__(self):
		# Power status
		self.status = False
		# Keep a list of pics we've taken
		self.pics = []


	def power_toggle(self):
		ret = call('adb shell "input keyevent KEYCODE_POWER"')
		if ret == 0:
			self.status = not self.status

	def take(self):
		return call('adb shell "input keyevent KEYCODE_CAMERA"')

	def get_pic(self, filename):

		# Get the filename of the latest picture
		cmd = 'cd /sdcard/DCIM/Camera/; IFS=$\'\n\'; output=(`ls -l`); lines=${#output[@]}; IFS=$\' \'; file_line=(${output[$((lines-1))]}); file_name=(); index=0; for part in ${file_line[@]}; do if [[ $index -gt 4 ]]; then file_name+=($part); fi; index=$((index+1)); done; echo ${file_name[1]}'
		cap_name = subprocess.check_output(['adb', 'shell', cmd])

		if cap_name == '':
			return False

		# Then copy it from the camera
		ret = call('adb pull /sdcard/DCIM/Camera/'+cap_name+' '+config.file_path)

		if ret != 0:
			return False

		# Then rename it to what we planned!
		ret = call('mv '+config.file_path+cap_name config.file_path+filename)
		if ret != 0:
			return False

		self.pics.append(config.file_path+filename)
		return True