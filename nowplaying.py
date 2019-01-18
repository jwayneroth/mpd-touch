import os
import Tkinter as tk
from PIL import Image, ImageTk
import fmuglobals
from piscene import *
import resource as resource

import logging
logger = logging.getLogger('fmu_logger')

"""
NowPlayingScene
 displays cover art, if available
 and playback controls
"""
class NowPlayingScene(PiScene):
	def __init__(self, frame=None):
		logger.debug('NowPlaying::init')
		logger.debug('mpd host %s' % mpd.host)
		
		PiScene.__init__(self, frame, 'NowPlaying')
		
		self.has_nav = True
		self.is_mpd_listener = True
		self.cover_size = 160
		self.label_height = 20
		self.track_scroll_velocity = 3
		if fmuglobals.RUN_ON_RASPBERRY_PI == True:
			self.track_scroll_velocity = 3
		self.main_active = False
		self.components = {}
		self.image_directory = 'images/'
		if os.path.dirname(__file__) != '':
			self.image_directory = os.path.dirname(__file__) + '/' + self.image_directory
		self.default_cover_image_directory = self.image_directory + 'default_covers'
		self.cover_image_directory = self.image_directory + 'covers'
		self.track_left = 0
		
		self.init_labels()
		
		self.init_cover()
		
	"""
	key_down
	"""
	def key_down(self, key, code):
		ui.Scene.key_down(self,key,code)

		if key == pygame.K_RIGHT or	 key == pygame.K_LEFT or key == pygame.K_RETURN:
			self.key_down_sidebar(key)

	"""
	initialize the artist, album, and track label widgets
	"""
	def init_labels(self):
		artist = tk.Label(self.inner, text=mpd.now_playing.artist, background=fmuglobals.COLORS['near_black'], foreground=fmuglobals.COLORS['slime'])
		album = tk.Label(self.inner, text=mpd.now_playing.album, background=fmuglobals.COLORS['near_black'], foreground=fmuglobals.COLORS['slime'])
		track = tk.Label(self.inner, text=mpd.now_playing.title, background=fmuglobals.COLORS['near_black'], foreground=fmuglobals.COLORS['slime'])
		
		artist.pack(fill=tk.X, expand=tk.YES)
		album.pack(fill=tk.X, expand=tk.YES)
		track.place(x=self.track_left)
		
		self.components['artist'] = artist
		self.components['album'] = album
		self.components['track'] = track
	
	"""
	initialize the album cover photo widget
	"""
	def init_cover(self):
		
		ci = self.get_cover_image()
		cover_image = ImageTk.PhotoImage(ci)
		
		cover = tk.Label(self.inner, image=cover_image, background=fmuglobals.COLORS['near_black'])
		cover.image = cover_image
		cover.pack(fill=tk.X, expand=tk.YES)
		
		self.components['album_cover'] = cover
		
		"""
		cover = CoverView(
			ui.Rect(
				0,
				self.label_height * 2 + self.margins * 2,
				self.main.frame.width,
				self.cover_size
			),
			self.get_cover_image(),
			ui.Rect(
				0,
				self.label_height * 2 + self.margins * 2,
				self.main.frame.width,
				self.cover_size
			)
		)
		cover.updated = True
		self.main.add_child(cover)
		self.components['album_cover'] = cover
		"""
		
	"""
	entered
	"""
	def entered(self):

		logger.debug('NowPlaying::entered')
		
		#print mpd.now_playing.title
		
		PiScene.entered(self)
		
		playing = mpd.now_playing
		
		logger.debug('now playing artist %s album %s track %s' % (playing.artist, playing.album, playing.title))
		
		self.components['artist'].config(text = playing.artist)
		self.components['album'].config(text = playing.album)
		
		ci = self.get_cover_image()
		cover_image = ImageTk.PhotoImage(ci)
		cover = self.components['album_cover']
		cover.config(image = cover_image)
		cover.image = cover_image
		
		self.components['track'].config(text = playing.title)
		
		if mpd.now_playing.playing_type == 'radio':
			self.radio_track_settings(True)
		else:
			self.radio_track_settings(False)

		#self.scroller.start()

		#self.stylize()

		#PiScene.entered(self)

	"""
	exited
	"""
	def exited(self):
		print 'NowPlaying exited'
		#self.scroller.stop()

	"""
	radio_track_settings
	"""
	def radio_track_settings(self, on_off):
		
		track = self.components['track']
		"""
		if on_off == True:
			track.halign = ui.LEFT
			self.resize_track()
		else:
			track.halign = ui.CENTER
			track.frame.left = 10
			track.frame.width = self.main.frame.width
		
		self.stylize()
		"""
		
	"""
	resize_track
	"""
	def resize_track(self):
		track = self.components['track']
		track.frame.width = track.text_size[0] + 10 # + self.margins
		track.frame.left = 0
		print 'NowPlayingScene::resize_track \t w: ' + str(track.frame.width)
		self.stylize()

	"""
	update
	"""
	def update(self):
		PiScene.update(self)
		
		if mpd.now_playing.playing_type == 'radio':
			
			track = self.components['track']
			
			self.track_left = self.track_left - self.track_scroll_velocity
			
			track.update()
			
			track_width = track.winfo_width()
			
			if self.track_left < (0 - track_width):
				self.track_left = 0
			
			track.place(x=self.track_left)
			
	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		while True:
			try:
				event = mpd.events.popleft()

				if event == 'radio_mode_on':
					self.radio_track_settings(True)
				
				#elif event == 'time_elapsed':
				#	 print 'NowPlayingScene::on_mpd_update: \t time_elapsed'
				#	 break
				
				elif event == 'radio_mode_off':
					self.radio_track_settings(False)
				
				elif event == 'title_change':
					playing = mpd.now_playing
					self.components['track'].config(text = playing.title)
					#if playing.playing_type == 'radio':
					#	self.resize_track()
				
				elif event == 'album_change':
					playing = mpd.now_playing
					
					self.components['artist'].config(text = playing.artist)
					self.components['album'].config(text = playing.album)
					
					ci = self.get_cover_image()
					cover_image = ImageTk.PhotoImage(ci)
					cover = self.components['album_cover']
					cover.config(image = cover_image)
					cover.image = cover_image
					
				"""
				elif event == 'volume':
					print 'NowPlayingScene::on_mpd_update: \t volume: ' + str(mpd.volume)
					self.controls.volume_slider.value = mpd.volume
				elif event == 'player_control':
					state = mpd.player_control_get()
					play_btn = self.controls.buttons['play_pause']
					print 'NowPlayingScene::on_mpd_update: \t state: ' + state
					if play_btn.icon_class != 'play' and state == 'play':
						play_btn.icon_class = 'play'
					if play_btn.icon_class != 'pause' and state == 'pause':
						play_btn.icon_class = 'pause'
					break
				"""
			except IndexError:
				break

		#print 'on_mpd_update'

	"""
	load a cover image (PIL Image) for the current album
	"""
	def get_cover_image(self):
		
		#cover_image = self.get_cover_image()
		#cover_photo = ImageTK.PhotoImage(cover_image)
		
		if mpd.now_playing.playing_type == 'radio':
			if mpd.now_playing.file.find('wfmu.org') != -1:
				return resource.get_image(self.image_directory + '/wfmu.png')
			else:
				return resource.get_image(self.get_default_cover_image())
		
		
		file_dir = self.music_directory + os.path.dirname(mpd.now_playing.file)
		file_name = file_dir + '/' + 'cover_art.jpg'
		
		logger.debug('NowPlaying::get_cover_image: ' + file_name)
		
		if os.path.isfile(file_name) == False:
			print '\t no existing image'
			try:
				music_file = File(self.music_directory + mpd.now_playing.file)
				if 'covr' in music_file:
					art_data = music_file.tags['covr'].data
				elif 'APIC:' in music_file:
					art_data = music_file.tags['APIC:'].data
				else:
					logger.debug('\t no cover art data')
					return resource.get_image( self.get_default_cover_image() )
				with open(file_name, 'wb') as img:
					img.write(art_data)
			except IOError, e:
				logger.debug('\t no music file')
				return resource.get_image( self.get_default_cover_image() )
			
		logger.debug('\t returning: ' + file_name)
		
		return resource.get_image(file_name)

	"""
	get the path of a random, default cover image
	"""
	def get_default_cover_image(self):
		defaults = [name for name in os.listdir( self.default_cover_image_directory ) if os.path.isfile( self.default_cover_image_directory + '/' + name )]
		return self.default_cover_image_directory + '/' + defaults[random.randrange(0, len(defaults))]

"""
CoverView
 extend ui.ImageView
"""
class CoverView():#ui.ImageView):
	def __init__(self, frame, img, parent_frame, content_mode=1):
		pass
		"""
		#ui.ImageView.__init__(self, frame, img)

		if img == None:
			img = resource.get_image( self.image_directory + 'defaults_covers/1.png')

		assert img is not None

		if frame is None:
			frame = pygame.Rect((0, 0), img.get_size())
		elif frame.w == 0 and frame.h == 0:
			frame.size = img.get_size()

		self._max_frame = frame

		self._enabled = False
		self.content_mode = content_mode
		self.image = img
		self.parent_frame = parent_frame

		#assert self.padding[0] == 0 and self.padding[1] == 0

		if self.content_mode == 0:
			self._image = ui.resource.scale_image(self.image, frame.size)
		elif self.content_mode == 1:
			self._image = ui.resource.scale_to_fit(self.image, frame.size)
		else:
			assert False, "Unknown content_mode"

		if self._image.get_width() < self.parent_frame.width:
			frame.left = (self.parent_frame.width - self._image.get_width()) / 2

		frame.size = self._image.get_size()

		ui.View.__init__(self, frame)

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, new_image):
		try:
			self._image = ui.resource.scale_to_fit(new_image, self._max_frame.size)
		except:
			self._image = new_image

		try:
			pf = self.parent_frame

			try:
				f = self.inner
				if self._image.get_width() < pf.width:
					f.left = (pf.width - self._image.get_width() ) / 2
			except:
				pass
		except:
			pass

	def layout(self):
		ui.View.layout(self)
	"""

