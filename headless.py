#!/usr/bin/env python

# MOD #####
from subprocess import call
from random import randint

from adbcamera import camera

from gpiozero import Button, LED
mybutt = Button(7)
myLED = LED(10)

import os
import time
from time import sleep
import sys
import config # this is the config python file config.py

########################
### Variables Config ###
########################
# https://www.raspberrypi.org/documentation/usage/gpio/
led_pin = 10 # LED 
#btn_pin = 7 # pin for the start button

prep_delay = 4 # number of seconds at step 1 as users prep to have photo taken
capture_delay = 3 # delay between pics
gif_delay = 50 # How much time between frames in the animated gif
restart_delay = 5 # how long to display finished message before beginning a new session

real_path = os.path.dirname(os.path.realpath(__file__))


print "Photo booth app running..." 

while True:
	myLED.on()
	#GPIO.output(led_pin,True); #turn on the light showing users they can push the button
	mybutt.wait_for_press()
	time.sleep(config.debounce) #debounce

	print "Get Ready"

	cam = camera()

	myLED.off()
	time.sleep(prep_delay)
	cam.cam_power()

	print "Taking pics"
	for s in list(reversed(range(1,config.total_pics+1))):
			cam.take()

	myLED.on()
	myLED.off()
	myLED.on()

	filenames = cam.download_session()

	# Go with what we have!!
	config.total_pics = len(filenames)

	# Move those files to expected filenames
	i = 1
	for f in filenames:
		call('mv '+config.file_path+f+' '+config.file_path+now+"-0"+str(i)+'.jpg', shell=True)
		print 'CMD: mv '+config.file_path+f+' '+config.file_path+now+"-0"+str(i)+'.jpg'
		i += 1

	print 'Downloaded this session: ', filenames
	myLED.off()

	cam.power_toggle()
	print "Done"

	time.sleep(restart_delay)

