#!/usr/bin/env python
# created by chris@drumminhands.com
# see instructions at http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/


# MOD #####
from subprocess import call
from random import randint

from adbcamera import camera

from gpiozero import Button, LED
mybutt = Button(7)
myLED = LED(10)


import os
import glob
import time
import traceback
from time import sleep
#import RPi.GPIO as GPIO
import atexit
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
import config # this is the config python file config.py
from signal import alarm, signal, SIGALRM, SIGKILL

########################
### Variables Config ###
########################
# https://www.raspberrypi.org/documentation/usage/gpio/
led_pin = 10 # LED 
#btn_pin = 7 # pin for the start button

capture_delay = 3 # delay between pics
prep_delay = 7 # number of seconds at step 1 as users prep to have photo taken
gif_delay = 50 # How much time between frames in the animated gif
restart_delay = 5 # how long to display finished message before beginning a new session
test_server = 'www.google.com'

# full frame of v1 camera is 2592x1944. Wide screen max is 2592,1555
# if you run into resource issues, try smaller, like 1920x1152. 
# or increase memory http://picamera.readthedocs.io/en/release-1.12/fov.html#hardware-limits
high_res_w = 1296 # width of high res image, if taken
high_res_h = 972 # height of high res image, if taken

#############################
### Variables that Change ###
#############################
# Do not change these variables, as the code will change it anyway
transform_x = config.monitor_w # how wide to scale the jpg when replaying
transfrom_y = config.monitor_h # how high to scale the jpg when replaying
offset_x = 0 # how far off to left corner to display photos
offset_y = 0 # how far off to left corner to display photos
replay_delay = 0.25 # how much to wait in-between showing pics on-screen after taking
replay_cycles = 5 # how many times to show each photo on-screen after taking

####################
### Other Config ###
####################
real_path = os.path.dirname(os.path.realpath(__file__))


# # GPIO setup
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(led_pin,GPIO.OUT) # LED
# #GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.output(led_pin,False) #for some reason the pin turns on at the beginning of the program. Why?

# initialize pygame
pygame.init()
pygame.display.set_mode((config.monitor_w, config.monitor_h))
screen = pygame.display.get_surface()
pygame.display.set_caption('Photo Booth Pics')
pygame.mouse.set_visible(False) #hide the mouse cursor
pygame.display.toggle_fullscreen()

#################
### Functions ###
#################

# clean up running programs as needed when main program exits
def cleanup():
	print('Ended abruptly')
	pygame.quit()
	#GPIO.cleanup()
atexit.register(cleanup)

# A function to handle keyboard/mouse/device input events    
def input(events):
	for event in events:  # Hit the ESC key to quit the slideshow.
		if (event.type == QUIT or
			(event.type == KEYDOWN and event.key == K_ESCAPE)):
			pygame.quit()
				
#delete files in folder
def clear_pics(channel):
	files = glob.glob(config.file_path + '*')
	for f in files:
		os.remove(f) 
	#light the lights in series to show completed
	print "Deleted previous pics"
	for x in range(0, 3): #blink light
		myLED.on()
		#GPIO.output(led_pin,True); 
		sleep(0.25)
		myLED.off()
		#GPIO.output(led_pin,False);
		sleep(0.25)


# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h):
	# Note this only works when in booting in desktop mode. 
	# When running in terminal, the size is not correct (it displays small). Why?

	# connect to global vars
	global transform_y, transform_x, offset_y, offset_x

	# based on output screen resolution, calculate how to display
	ratio_h = (config.monitor_w * img_h) / img_w 

	if (ratio_h < config.monitor_h):
		#Use horizontal black bars
		#print "horizontal black bars"
		transform_y = ratio_h
		transform_x = config.monitor_w
		offset_y = (config.monitor_h - ratio_h) / 2
		offset_x = 0
	elif (ratio_h > config.monitor_h):
		#Use vertical black bars
		#print "vertical black bars"
		transform_x = (config.monitor_h * img_w) / img_h
		transform_y = config.monitor_h
		offset_x = (config.monitor_w - transform_x) / 2
		offset_y = 0
	else:
		#No need for black bars as photo ratio equals screen ratio
		#print "no black bars"
		transform_x = config.monitor_w
		transform_y = config.monitor_h
		offset_y = offset_x = 0

# uncomment these lines to troubleshoot screen ratios
#     print str(img_w) + " x " + str(img_h)
#     print "ratio_h: "+ str(ratio_h)
#     print "transform_x: "+ str(transform_x)
#     print "transform_y: "+ str(transform_y)
#     print "offset_y: "+ str(offset_y)
#     print "offset_x: "+ str(offset_x)

# display one image on screen
def show_image(image_path):

	# clear the screen
	screen.fill( (0,0,0) )

	# load the image
	img = pygame.image.load(image_path)
	img = img.convert()

	# set pixel dimensions based on image
	set_demensions(img.get_width(), img.get_height())

	# rescale the image to fit the current display
	img = pygame.transform.scale(img, (transform_x,transfrom_y))
	screen.blit(img,(offset_x,offset_y))
	pygame.display.flip()

# display a blank screen
def clear_screen():
	screen.fill( (0,0,0) )
	pygame.display.flip()

# display a group of images
def display_pics(jpg_group, sm=False):
	for i in range(0, replay_cycles): #show pics a few times
		for i in range(1, config.total_pics+1): #show each pic
			if sm:
				show_image(config.file_path + jpg_group + "-0" + str(i) + "-sm.jpg")
			else:
				show_image(config.file_path + jpg_group + "-0" + str(i) + ".jpg")

			time.sleep(replay_delay) # pause 


# define the photo taking function for when the big button is pressed 
def start_photobooth(): 

	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	################################# Begin Step 1 #################################

	print "Get Ready"

	show_image(real_path + "/instructions.png")

	cam = camera()

	myLED.off()
	time.sleep(prep_delay)
	cam.cam_power()


	#camera = picamera.PiCamera()
	#camera.vflip = False
	#camera.hflip = True # flip for preview, showing users a mirror image

	#camera.saturation = -100 # comment out this line if you want color images
	#camera.iso = config.camera_iso

	# pixel_width = 0 # local variable declaration
	# pixel_height = 0 # local variable declaration

	# if config.hi_res_pics:
	# 	camera.resolution = (high_res_w, high_res_h) # set camera resolution to high res
	# else:
	# 	pixel_width = 500 # maximum width of animated gif on tumblr
	# 	pixel_height = config.monitor_h * pixel_width // config.monitor_w
	# 	camera.resolution = (pixel_width, pixel_height) # set camera resolution to low res
		
	################################# Begin Step 2 #################################

	print "Taking pics"

	now = time.strftime("%Y-%m-%d-%H-%M-%S") #get the current date and time for the start of the filename

	if config.capture_count_pics:

		time.sleep(2) #warm up camera
		myLED.on()

		for s in list(reversed(range(1,config.total_pics+1))):
			show_image(real_path + "/pose" + str(s) + ".png")
			time.sleep(s*0.15)

		for s in list(reversed(range(1,config.total_pics+1))):
			# Show a random image to make people smile!
			rand_smile = str(randint(1, config.smile_pics))
			show_image(real_path + "/smile/"+rand_smile+".jpg")
			cam.take()


		show_image(real_path + "/processing.png")
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

	########################### Begin Step 3 #################################

	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	if config.make_sm: # make small images
		print 'making small pics'

		for x in range(1, config.total_pics+1): #batch process all the images
			graphicsmagick = "gm convert -size 750x750 " + config.file_path + now + "-0" + str(x) + ".jpg -thumbnail 500x500 " + config.file_path + now + "-0" + str(x) + "-sm.jpg"
			os.system(graphicsmagick) #do the graphicsmagick action
			print 'CMD: '+graphicsmagick


	if config.make_gifs and config.make_sm: # make the gifs
		print "Creating an animated gif"

		graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + config.file_path + now + "*-sm.jpg " + config.file_path + now + ".gif" 
		os.system(graphicsmagick) #make the .gif
		print 'CMD: '+graphicsmagick
	

	display_pics(now, sm=config.make_sm)
	###############

	########################### Begin Step 4 #################################

	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	print "Done"

	show_image(real_path + "/finished2.png")

	time.sleep(restart_delay)
	show_image(real_path + "/intro.png");
	myLED.on()



####################
### Main Program ###
####################

## clear the previously stored pics based on config settings
if config.clear_on_startup:
	clear_pics(1)

print "Photo booth app running..." 
for x in range(0, 5): #blink light to show the app is running
	myLED.on()
	#GPIO.output(led_pin,True)
	sleep(0.25)
	myLED.off()
	#GPIO.output(led_pin,False)
	sleep(0.25)

show_image(real_path + "/intro.png");

print 'Image shown...'

while True:
	myLED.on()
	#GPIO.output(led_pin,True); #turn on the light showing users they can push the button
	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	mybutt.wait_for_press()

	time.sleep(config.debounce) #debounce

	start_photobooth()
