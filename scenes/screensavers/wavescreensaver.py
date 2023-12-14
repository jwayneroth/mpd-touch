import time
import os

import fmuglobals
from ..piscene import *

from .wave.wave import Wave

"""
ScreensaverScene
"""
class WaveScreensaver(PiScene):
	def __init__(self, frame, name, screen=None):
		ui.Scene.__init__(self, frame)

		self.name = name
		self.is_mpd_listener = True
		self.label_height = 36
		self.is_screensaver = True
		self.top_screen = screen

		self.sidebar_index = 0
		self.active_sidebar_btn = 0
		self.dialog = None
		self.on_nav_change = callback.Signal()
		self.open_dialog = callback.Signal()

		self.track_scroll_velocity = fmuglobals.TRACK_SPEED
		self.track_y = self.frame.height - self.label_height - 15
		self.track = self.make_track()

		self.make_screenaver()

	"""
	mouse_down
	"""
	def hit(self, pt):
		pass

	"""
	key_down
	"""
	def key_down(self, key, code):
		if self.dialog is not None:
			self.dialog.key_down(key, code)
		else:
			if key == pygame.K_RETURN:
				self.on_nav_change('NowPlaying', from_screensaver=True)

	"""
	make_track
	"""
	def make_track(self):
		track_x = 0
		track_y = self.track_y
		track_rect = ui.Rect(track_x, track_y, self.frame.width, self.label_height)
		track = ui.ScreensaverTrack(track_rect, mpd.now_playing.title, halign=ui.CENTER)
		track.stylize()
		return track

	"""
	resize_track
	"""
	def resize_track(self):
		logger.debug("%s::resize_track", self.name)
		track = self.track
		track.frame.width = track.text_size[0] + 10
		track.frame.left = 0
		track.stylize()
		track.updated = True

	"""
	make_screenaver
	"""
	def make_screenaver(self):
		surface = pygame.Surface(self.top_screen.get_size())
		self.ss = Wave(window=surface, batch=None)

	"""
	entered
	"""
	def entered(self):
		PiScene.entered(self)

		playing = mpd.now_playing
		self.track.text = playing.title
		self.resize_track()

		#self.ss.start()

	"""
	exited
	"""
	def exited(self):
		logger.debug('Screensaver exited')
		#self.ss.stop()

	"""
	update
	"""
	def update(self):
		updated = False
		
		try:
			if mpd.status_get():
				self.on_mpd_update()
				updated = True
		except:
			pass

		track = self.track

		track.frame.left = track.frame.left - self.track_scroll_velocity
		if track.frame.left < -( track.frame.width ):
			track.frame.left = self.frame.right
			track.updated = True
		self.updated = True
		
		time.sleep(fmuglobals.SS_UPDATE_INTERVAL)

		return updated

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		while True:
			try:

				event = mpd.events.popleft()

				#logger.debug("%s::on_mpd_update %s", self.name, event)

				if event == 'radio_mode_on':
					self.resize_track()
				elif event == 'radio_mode_off':
					self.resize_track()
				elif event == 'title_change':
					playing = mpd.now_playing
					self.track.text = playing.title
					self.resize_track()
				elif event == 'album_change':
					playing = mpd.now_playing
					self.track.text = playing.title
					self.resize_track()
			except IndexError:
				break

	"""
	draw (override)
	"""
	def draw(self, force=False):
		#self.ss.window.fill(0)
		self.ss.loopDisplay()
		self.track.draw()
		self.top_screen.blit(self.ss.window, (0,0))
		self.top_screen.blit(self.track.surface, (self.track.frame.left, self.track_y))
		#pygame.display.update(self.ss.frame)
		return True
