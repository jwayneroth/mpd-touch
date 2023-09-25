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
fh.setLevel(logging.INFO)
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
#from lib.ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
if fmuglobals.USE_LIRCD:
	from lib.lircpoll import Irw
from scenes import *
from web.server.server import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class Fmulcd(object):
	def __init__(self):
		self.current = False
		self.last = False

		screen_width = fmuglobals.SCREEN_SIZE[0]
		screen_height = fmuglobals.SCREEN_SIZE[1]

		self.screen_dimensions = (screen_width, screen_height)
		self.screen = False
		self.ss_timer = 0
		self.ss_timer_on = True
		self.ss_delay = fmuglobals.SS_DELAY
		self.web_server = None

		self.init_pygame()

		self.init_web()

		fmutheme = Fmutheme()
		ui.theme.use_theme(fmutheme)

		rect = pygame.Rect((0,0), self.screen_dimensions)

		self.scenes = {
			'NowPlaying': NowPlayingScene(rect, 'NowPlaying'),
			'Albums': AlbumListScene(rect, 'Albums'),
			'Radio': RadioScene(rect, 'Radio'),
			'Settings': SettingsScene(rect, 'Settings'),
			#'Controls': ControlsScene(rect, 'Controls'),
			'Screensaver': ScreensaverScene(rect, 'Screensaver'),
			#'SpectrumScreensaver': SpectrumScreensaver(rect, 'SpectrumScreensaver', self.screen),
			'WaveScreensaver': WaveScreensaver(rect, 'WaveScreensaver', self.screen),
			#'OrigamiScreensaver': OrigamiScreensaver(rect, 'OrigamiScreensaver', self.screen),
			'LinesScreensaver': LinesScreensaver(rect, 'LinesScreensaver', self.screen),
		}

		for name, scene in self.scenes.items():
			scene.layout()

		self.screensavers = [
			'Screensaver',
			'WaveScreensaver',
			#'LinesScreensaver',
			#'SpectrumScreensaver',
			#'OrigamiScreensaver',
		]

		if fmuglobals.RUN_ON_RASPBERRY_PI:
			self.screensavers.append('LinesScreensaver')

		self.dialogs = {
			'Controls': ControlsDialog(rect),
			#'Brightness': BrightnessDialog(rect)
		}

		for name,scene in self.scenes.items():
			scene.on_state_changed.connect(self.scene_state_change)
			scene.on_nav_change.connect(self.change_scene)
			scene.open_dialog.connect(self.open_dialog)

		for name,dialog in self.dialogs.items():
			dialog.on_dismissed.connect(self.dialog_dismissed)

		self.make_current_scene(self.scenes['NowPlaying'])

		#self.ab = AnalogButtons()

	def scene_state_change(self, scene):
		logger.debug("FMULCD::scene_state_change::%s" % scene.name)

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
			os.environ["DISPLAY"] = ":0" # JWR 20230516
			pygame.display.init()
			pygame.font.init()

			if fmuglobals.RUN_ON_RASPBERRY_PI:
				pygame.mouse.set_visible(fmuglobals.SHOW_MOUSE)

			# custom cursor
			# surf = pygame.Surface((10, 10)) # you could also load an image 
			# surf.fill((255, 255, 255, 0))    # and use that as your surface
			# color = pygame.cursors.Cursor((0, 0), surf)
			# pygame.mouse.set_cursor(color)

			if fmuglobals.FULLSCREEN and fmuglobals.RUN_ON_RASPBERRY_PI:
				self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
			else:
				self.screen = pygame.display.set_mode((self.screen_dimensions)) #, pygame.NOFRAME)

			alarm(0)

		except Alarm:
			raise KeyboardInterrupt

		logger.debug('pygame inited on rpi?: %s' % fmuglobals.RUN_ON_RASPBERRY_PI)

		pygame.key.set_repeat(300,180)
		pygame.display.set_caption('FmuLcd')
		#pygame.event.set_allowed(None)
		#pygame.event.set_allowed(( pygame.QUIT, pygame.KEYDOWN ))

	"""
	init_web
	"""
	def init_web(self):
		#try:
		# f = open(os.devnull, 'w')
		# sys.stdout = sys.stderr = f
		self.web_server = Server(self)
		#except Exception as e:
		#	logger.debug(e)

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
		#logger.debug('fmulcd::open_dialog %s' % dialog_name)
		if self.current:
			dialog = self.dialogs[dialog_name]
			self.current.add_child(dialog)
			self.current.dialog = dialog
			dialog.entered()
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
		logger.debug("Fmulcd::change_scene %s", self)
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
				#self.change_scene('Screensaver')
				self.load_screensaver()

	def load_screensaver(self) :
		ss = self.screensavers[random.randrange(len(self.screensavers))]
		self.change_scene(ss)

	def kill_app(self) :
		logger.debug("fmu.kill_app")

		fmu.current.exited()
		
		time.sleep(.05)
		
		# if fmuglobals.RUN_ON_RASPBERRY_PI:
			
		# 	#GPIO.output(18, GPIO.LOW)
			
		# 	pygame.quit()
			
		# 	try:
		# 		subprocess.Popen('sudo service fmulcd stop', shell=True, stdout=subprocess.PIPE)
		# 	except:
		# 		pass
	
		pygame.quit()

		#sys.exit(0)
		
		os._exit(0)

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
	#logger.debug("_press_handler %s", mousepoint)

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

	if fmu.current.name in fmu.screensavers:
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
	if key == b'KEY_LEFT':
		return pygame.K_LEFT
	elif key == b'KEY_RIGHT':
		return pygame.K_RIGHT
	elif key == b'KEY_UP':
		return pygame.K_UP
	elif key == b'KEY_DOWN':
		return pygame.K_DOWN
	elif key == b'KEY_ENTER':
		return pygame.K_RETURN
	elif key == b'KEY_SELECT':
		return pygame.K_RETURN
	return key

"""
check lirc key for special case
"""
def lirc_special_case(key):
	if key == b'KEY_VOLUMEUP':
		mpd.set_volume_relative(5)
		return True
	elif key == b'KEY_VOLUMEDOWN':
		mpd.set_volume_relative(-5)
		return True
	elif key == b'KEY_MUTE':
		#mpd.toggle_muted()
		mpd.set_volume(0)
		return True
	return False

"""
main
"""
if __name__ == '__main__':
	logger.debug('fmulcd started')

	time.sleep(1)

	fmu = Fmulcd()

	update = False
	down_in_view = None
	user_active = False

	if fmuglobals.RUN_ON_RASPBERRY_PI:
		#ts = Touchscreen()
		if fmuglobals.USE_LIRCD:
			irw = Irw(8)
			irw.run()
	clock = pygame.time.Clock()
	#fps = 32 if fmuglobals.RUN_ON_RASPBERRY_PI else 30
	ticks = 0

	time.sleep(0.3)

	mpd.radio_station_start('http://stream0.wfmu.org/freeform-128k')

	while True:
		ticks = clock.tick() #(fps)

		down_in_view = None
		user_active = False

		if fmuglobals.RUN_ON_RASPBERRY_PI:

			#ts.poll()
			# for touch in ts.touches:
			# 	touch.on_press = ts_press_handler
			# 	touch.on_release = ts_release_handler
			# 	#touch.on_move = ts_move_handler

			if fmuglobals.USE_LIRCD:
				irwlast = irw.last()
				if irwlast is not None:
					user_active = True
					if lirc_special_case(irwlast) is False:
						irw_trans = lirc_key_translate(irwlast)
						fmu.current.key_down(irw_trans, '')

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

			#if not fmuglobals.RUN_ON_RASPBERRY_PI:
			if e.type == pygame.MOUSEBUTTONDOWN:
				_press_handler(pygame.mouse.get_pos())
			elif e.type == pygame.MOUSEBUTTONUP:
				_release_handler(pygame.mouse.get_pos())
			#elif e.type == pygame.MOUSEMOTION:
			# _move_handler(mousepoint, e.rel)

		if fmu.ss_timer_on:
			fmu.screensaver_tick(ticks, user_active)

		update = fmu.current.update()

		if update and fmu.web_server is not None:
			fmu.web_server.update_clients()

		if fmu.current.draw(): # and fmu.current.is_screensaver != True:

			fmu.screen.blit(fmu.current.surface, (0, 0))

			pygame.display.flip()

		#time.sleep(.033)
