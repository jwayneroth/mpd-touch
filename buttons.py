#!/usr/bin/python
import pygame
import time
#import thread
import fmuglobals

if fmuglobals.RUN_ON_RASPBERRY_PI:
	import RPi.GPIO as GPIO

"""
AnalogButtons
"""
class AnalogButtons:

	def __init__(self):
		if fmuglobals.RUN_ON_RASPBERRY_PI:
			GPIO.setmode(GPIO.BCM)
			
			#import rotary_encoder
			#self.encoder = rotary_encoder.RotaryEncoder(4,15)
			#from rotary_class import RotaryEncoder
			#self.encoder = RotaryEncoder(4,15,callback=self.encoder_event)

		self.buttons = [
			{ 'pin': 23, 'key': pygame.K_UP, 'callback': self.on_up_click},
			{ 'pin': 22, 'key': pygame.K_RIGHT, 'callback': self.on_right_click},
			{ 'pin': 14, 'key': pygame.K_DOWN, 'callback': self.on_down_click},
			{ 'pin': 17, 'key': pygame.K_LEFT, 'callback': self.on_left_click},
			{ 'pin': 27, 'key': pygame.K_RETURN, 'callback': self.on_return_click},
		]
                                                           
		if fmuglobals.RUN_ON_RASPBERRY_PI:
			for btn in self.buttons:
				GPIO.setup( btn['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.add_event_detect(btn['pin'], GPIO.FALLING, callback=btn['callback'], bouncetime=20)
	
		#self.startListener()
	
	def encoder_event(self,event):
		if event == self.encoder.CLOCKWISE:
			#print "Clockwise"
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode=None, mod=None))
		elif event == self.encoder.ANTICLOCKWISE:
			#print "Anticlockwise"
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, unicode=None, mod=None))
		#elif event == self.encoder.BUTTONDOWN:
		#	print "Button down"
		#elif event == self.encoder.BUTTONUP:
		#	print "Button up"
		return

	#def on_click(self, btn):
	#	print 'GPIO ' + str(btn) + ' clicked'
	#	pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=btn['key'], unicode=None, mod=None))

	def on_left_click(self, btn):
		while GPIO.input(btn) == GPIO.LOW:
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, unicode=None, mod=None))
			time.sleep(0.18)

	def on_up_click(self, btn):
		while GPIO.input(btn) == GPIO.LOW:
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, unicode=None, mod=None))
			time.sleep(0.18)

	def on_down_click(self, btn):
		while GPIO.input(btn) == GPIO.LOW:
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode=None, mod=None))
			time.sleep(0.18)

	def on_right_click(self, btn):
		while GPIO.input(btn) == GPIO.LOW:
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, unicode=None, mod=None))
			time.sleep(0.18)

	def on_return_click(self, btn):
		while GPIO.input(btn) == GPIO.LOW:
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=None, mod=None))
			time.sleep(0.18)

	def startListener(self):
		if fmuglobals.RUN_ON_RASPBERRY_PI:
			try:
				thread.start_new_thread( self.check_buttons, ())
			except:
			   print "Error: AnalogButtons unable to start thread"
		else:
			try:
				thread.start_new_thread( self.check_buttons_desktop, ())
			except:
			   print "Error: AnalogButtons unable to start thread"

	def check_buttons(self):
		while 1:
			#delta = self.encoder.get_delta()

			#if delta != 0:
			#	if delta > 0:
			#		pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode=None, mod=None))
			#	else:
			#		pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, unicode=None, mod=None))
			#else:
			
			for btn in self.buttons:
				if GPIO.input(btn['pin']) == False:
					#print 'GPIO ' + str(btn['pin']) + ' pressed'
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=btn['key'], unicode=None, mod=None))
					time.sleep(.3)
					break
			

			#time.sleep(.01)

	def check_buttons_desktop(self):
		while 1:
			for btn in self.buttons:
				pass
			time.sleep(.08)