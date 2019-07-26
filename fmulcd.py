#!/usr/bin/python

import random
import sys
from signal import alarm, signal, SIGALRM, SIGKILL
import os
import time
import subprocess

import logging
logger = logging.getLogger('fmu_logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/fmulcd.log', 'a')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

from lib.mpd_client import *
import fmuglobals
from fmutheme import Fmutheme
#from lib.gpio-buttons import AnalogButtons
import pygameui as ui
from lib.ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
from lib.lircpoll import Irw
from scenes import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class Fmulcd(object):
	def __init__(self):
		self.current = False
		self.last = False
		
		screen_width = 800
		screen_height = 480
		
		self.screen_dimensions = (screen_width, screen_height)
		self.screen = False
		self.ss_timer = 0
		self.ss_timer_on = True
		self.ss_delay = 60000

		if not fmuglobals.RUN_ON_RASPBERRY_PI:
			self.ss_delay = 600000

		self.init_pygame()

		fmutheme = Fmutheme()
		ui.theme.use_theme(fmutheme)

		rect = pygame.Rect((0,0), self.screen_dimensions)

		self.scenes = {
			'NowPlaying': NowPlayingScene(rect),
			'Albums': AlbumListScene(rect),
			'Radio': RadioScene(rect),
			'Settings': SettingsScene(rect),
			#'Controls': ControlsScene(rect),
			'Screensaver': ScreensaverScene(rect)
		}
		
		self.dialogs = {
			'Controls': ControlsDialog(rect),
			'Brightness': BrightnessDialog(rect)
		}
		
		for name,scene in self.scenes.iteritems():
			scene.on_nav_change.connect(self.change_scene)
			scene.open_dialog.connect(self.open_dialog)
		
		for name,dialog in self.dialogs.iteritems():
			dialog.on_dismissed.connect(self.dialog_dismissed)
			
		self.make_current_scene(self.scenes['NowPlaying'])

		#self.ab = AnalogButtons()

	"""
	init_pygame
	"""
	def init_pygame(self):
		# this section is an unbelievable nasty hack - for some reason Pygame
		# needs a keyboardinterrupt to initialise in some limited circs (second time running)
		class Alarm(Exception):
			pass

		def alarm_handler(signum, frame):
			raise Alarm

		signal(SIGALRM, alarm_handler)

		alarm(3)

		try:
			pygame.init()

			if fmuglobals.RUN_ON_RASPBERRY_PI:
				pygame.mouse.set_visible(False)
				self.screen = pygame.display.set_mode((self.screen_dimensions), pygame.FULLSCREEN)
			else:
				self.screen = pygame.display.set_mode(self.screen_dimensions)

			alarm(0)

		except Alarm:
			raise KeyboardInterrupt

		logger.debug('pygame inited on rpi?: %s' % fmuglobals.RUN_ON_RASPBERRY_PI)

		pygame.key.set_repeat(300,180)
		pygame.display.set_caption('Raspberry Pi UI')
		#pygame.event.set_allowed(None)
		#pygame.event.set_allowed(( pygame.QUIT, pygame.KEYDOWN ))

	"""
	make_current_scene
	"""
	def make_current_scene(self, scene):
		logger.debug('Fmulcd::make_current_scene \t' + scene.name)
		#if self.current == scene:
		#	 return
		if self.current:
			self.current.exited()
			self.last = self.current
		self.current = scene
		self.current.entered()
		self.current.refresh()

	"""
	open_dialog
		add the requested dialog on top of the current scene
	"""
	def open_dialog(self, dialog_name):
		if self.current: 
			dialog = self.dialogs[dialog_name]
			self.current.add_child(dialog)
			self.current.dialog = dialog
			dialog.focus()
	
	"""
	dialog_dismissed
	"""
	def dialog_dismissed(self):
		logger.debug('fmulcd::dialog_dismissed')
		if self.current:
			self.current.dialog = None
			self.current.layout()
		
	"""
	change_scene
	 called from a PiScene on_nav_change
	 push requested scene to ui and refresh it
	"""
	def change_scene(self, scene_name, refresh=False, from_screensaver=False):
		if from_screensaver:
			logger.debug('exiting screensaver, going to %s' % self.last.name)
			self.ss_timer_on = True
			#if self.last:
			#	self.make_current_scene(self.last)
			#	return
		if refresh == True:
			self.scenes['Albums'].populate_artists_view()
		self.make_current_scene(self.scenes[scene_name])

	def screensaver_tick(self, ms, activity):
		if activity:
			self.ss_timer = 0
		else:
			self.ss_timer += ms
			if self.ss_timer >= self.ss_delay:
				logger.debug('going to screensaver')
				self.ss_timer_on = False
				self.ss_timer = 0
				self.change_scene('Screensaver')

	def kill_app(self):
		if fmuglobals.RUN_ON_RASPBERRY_PI:
			#GPIO.output(18, GPIO.LOW)
			pygame.quit()
			try:
				subprocess.Popen('sudo service fmulcd stop', shell=True, stdout=subprocess.PIPE)
			except:
				pass
			sys.exit(0)
		else:
			pygame.quit()
			sys.exit(0)

"""
ts mousedown handler
"""
def ts_press_handler(event, touch):
	_press_handler((touch.x, touch.y))

"""
ts mouseup handler
"""
def ts_release_handler(event, touch):
	_release_handler((touch.x, touch.y))

"""
ts mousemove handler
"""
def ts_move_handler(event, touch):
	lst = touch.last_position
	delta = max(abs(lst[0] - touch.x), abs(lst[1] - touch.y))
	move_handler((touch.x, touch.y), delta)

"""
mousedown handler
"""
def _press_handler(mousepoint):

	global user_active
	global down_in_view

	user_active = True

	hit_view = fmu.current.hit(mousepoint)

	if (hit_view is not None and not isinstance(hit_view, ui.Scene)):
		ui.focus.set(hit_view)
		down_in_view = hit_view
		pt = hit_view.from_window(mousepoint)
		hit_view.mouse_down('FOO', pt)
	else:
		ui.focus.set(None)

"""
mouseup handler
"""
def _release_handler(mousepoint):

	global user_active
	global down_in_view

	user_active = True

	hit_view = fmu.current.hit(mousepoint)

	if fmu.current == fmu.scenes['Screensaver']:
		fmu.change_scene('NowPlaying', False, True)
		return

	if hit_view is not None:
		if down_in_view and hit_view != down_in_view:
			down_in_view.blurred()
			ui.focus.set(None)
		pt = hit_view.from_window(mousepoint)
		hit_view.mouse_up('FOO', pt)

	down_in_view = None

"""
mousemove handler
"""
def _move_handler(mousepoint):

	global user_active
	global down_in_view

	user_active = True

	if down_in_view and down_in_view.draggable:
		pt = down_in_view.from_window(mousepoint)
		down_in_view.mouse_drag(pt, e.rel)
	else:
		fmu.current.mouse_motion(mousepoint)

"""
translate lirc key to pygame key
"""
def lirc_key_translate(key):
	if key == 'KEY_LEFT':
		return pygame.K_LEFT
	elif key == 'KEY_RIGHT':
		return pygame.K_RIGHT
	elif key == 'KEY_UP':
		return pygame.K_UP
	elif key == 'KEY_DOWN':
		return pygame.K_DOWN
	elif key == 'KEY_ENTER':
		return pygame.K_RETURN

	return key

"""
main
"""
if __name__ == '__main__':
	logger.debug('fmulcd started')

	time.sleep(1)

	fmu = Fmulcd()

	down_in_view = None
	user_active = False

	if fmuglobals.RUN_ON_RASPBERRY_PI:
		ts = Touchscreen()
		irw = Irw(8)
		irw.run()
	clock = pygame.time.Clock()
	fps = 32 if fmuglobals.RUN_ON_RASPBERRY_PI else 30
	ticks = 0

	time.sleep(0.3)

	mpd.radio_station_start('http://stream0.wfmu.org/freeform-128k')

	while True:
		ticks = clock.tick()#(fps)

		down_in_view = None
		user_active = False

		if fmuglobals.RUN_ON_RASPBERRY_PI:
			ts.poll()
			irwlast = irw.last()

			for touch in ts.touches:
				touch.on_press = ts_press_handler
				touch.on_release = ts_release_handler
				#touch.on_move = ts_move_handler

			if irwlast is not None:
				user_active = True
				fmu.current.key_down(lirc_key_translate(irwlast), '')

		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				fmu.kill_app()
				break
			if e.type == pygame.KEYDOWN:
				user_active = True
				if (( e.key == pygame.K_ESCAPE )):
					fmu.kill_app()
				else:
					fmu.current.key_down(e.key, e.unicode)
					break

			if not fmuglobals.RUN_ON_RASPBERRY_PI:
				mousepoint = pygame.mouse.get_pos()
				if e.type == pygame.MOUSEBUTTONDOWN:
					_press_handler(mousepoint)
				elif e.type == pygame.MOUSEBUTTONUP:
					_release_handler(mousepoint)
				#elif e.type == pygame.MOUSEMOTION:
				# _move_handler(mousepoint, e.rel)

		if fmu.ss_timer_on:
			fmu.screensaver_tick(ticks, user_active)

		fmu.current.update()

		if fmu.current.draw():

			fmu.screen.blit(fmu.current.surface, (0, 0))

			pygame.display.flip()

		#time.sleep(.05)
