import time
import os

from mutagen import File
import fmuglobals
from .piscene import *

"""
NowPlayingScene
 displays cover art, if available
 and playback controls
"""
class NowPlayingScene(PiScene):
	def __init__(self, frame, name):

		PiScene.__init__(self, frame, name)

		self.has_nav = True
		self.is_mpd_listener = True
		self.cover_size = self.main.frame.height - 190 #290 #160
		self.label_height = 36
		self.track_scroll_velocity = fmuglobals.TRACK_SPEED
		self.main_active = False
		self.components = {}
		self.image_directory = 'images/'
		if os.path.dirname(__file__) != '':
			self.image_directory = os.path.dirname(__file__) + '/../' + self.image_directory
		self.default_cover_image_directory = self.image_directory + 'default_covers'
		self.cover_image_directory = self.image_directory + 'covers'

		#logger.debug('nowplaying image_directory: ' + self.image_directory)

		self.current_default_cover = False

		self.make_labels()

	"""
	key_down
	"""
	def key_down(self, key, code):
		ui.Scene.key_down(self,key,code)

		if self.dialog is not None:
			self.dialog.key_down(key, code)
		else:
			if key == pygame.K_DOWN or key == pygame.K_UP or key == pygame.K_RETURN:
				self.key_down_sidebar(key)

	"""
	make_labels
	"""
	def make_labels(self):
		comp_labels = {
			'artist': [
				ui.Rect( 0, self.margins, self.main.frame.width, self.label_height ),
				mpd.now_playing.artist
			],
			'album': [
				ui.Rect( 0, self.label_height + self.margins * 2, self.main.frame.width, self.label_height ),
				mpd.now_playing.album
			],
			'track': [
				ui.Rect( 0, self.label_height * 2 + self.margins * 4 + self.cover_size, self.main.frame.width, self.label_height ),
				mpd.now_playing.title
			]
		}

		for key, val in comp_labels.items():
			label = ui.HeadingOne( val[0], val[1], halign=ui.CENTER )
			self.main.add_child(label)
			self.components[key] = label

		cover = CoverView(
			ui.Rect(
				0,
				self.label_height * 2 + self.margins * 3,
				self.main.frame.width,
				self.cover_size
			),
			self.update_cover_image(), #self.get_cover_image(),
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
	entered
	"""
	def entered(self):

		PiScene.entered(self)

		playing = mpd.now_playing

		self.components['artist'].text = playing.artist
		self.components['album'].text = playing.album
		self.components['album_cover'].image = self.update_cover_image() #self.get_cover_image()
		self.components['album_cover'].updated = True
		self.components['track'].text = playing.title

		self.resize_track()

		#if mpd.now_playing.playing_type == 'radio':
		#	 self.radio_track_settings(True)
		#else:
		#	 self.radio_track_settings(False)

		self.stylize()


	"""
	exited
	"""
	def exited(self):
		logger.debug('NowPlaying exited')
		#self.scroller.stop()

	"""
	radio_track_settings
	"""
	def radio_track_settings(self, on_off):

		track = self.components['track']

		if on_off == True:
			track.halign = ui.LEFT
			self.resize_track()
		else:
			track.halign = ui.CENTER
			track.frame.left = 10
			track.frame.width = self.main.frame.width

		self.stylize()

	"""
	resize_track
	"""
	def resize_track(self):
		track = self.components['track']
		track.frame.width = track.text_size[0] + 10 # + self.margins
		track.frame.left = 0
		#print('NowPlayingScene::resize_track \t w: ' + str(track.frame.width)
		self.stylize()

	"""
	update
	"""
	def update(self):

		update = PiScene.update(self)

		track = self.components['track']

		if True:
		#if track.frame.width > self.main.frame.width:
		#if mpd.now_playing.playing_type == 'radio':

			track.frame.left = track.frame.left - self.track_scroll_velocity
			if track.frame.left < -( track.frame.width ):
				track.frame.left = self.main.frame.right
			track.updated = True

			self.updated = True

		#logger.debug("NowPlaying::update %s" % update)
		return update

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		while True:
			try:

				event = mpd.events.popleft()

				#print('NowPlaying::on_mpd_update \t ' + event

				if event == 'radio_mode_on':
					#print('NowPlayingScene::on_mpd_update: \t radio_mode_on')
					#self.radio_track_settings(True)
				#elif event == 'time_elapsed':
					#	 print('NowPlayingScene::on_mpd_update: \t time_elapsed'
					#	 break
					self.resize_track()
					self.stylize()
				elif event == 'radio_mode_off':
					#print('NowPlayingScene::on_mpd_update: \t radio_mode_off')
					#self.radio_track_settings(False)
					self.resize_track()
					self.stylize()
				elif event == 'title_change':
					#print('NowPlayingScene::on_mpd_update: \t title_change')
					playing = mpd.now_playing
					self.components['track'].text = playing.title
					#if playing.playing_type == 'radio':
					self.resize_track()
					self.stylize()
				elif event == 'album_change':
					#print('NowPlayingScene::on_mpd_update: \t album_change')
					playing = mpd.now_playing
					self.components['artist'].text = playing.artist
					self.components['album'].text = playing.album
					self.components['album_cover'].image = self.update_cover_image() #self.get_cover_image()
					self.resize_track()
					self.stylize()
				"""
				elif event == 'volume':
					print('NowPlayingScene::on_mpd_update: \t volume: ' + str(mpd.volume)
					self.controls.volume_slider.value = mpd.volume
				elif event == 'player_control':
					state = mpd.get_playback()
					play_btn = self.controls.buttons['play_pause']
					print('NowPlayingScene::on_mpd_update: \t state: ' + state
					if play_btn.icon_class != 'play' and state == 'play':
						play_btn.icon_class = 'play'
					if play_btn.icon_class != 'pause' and state == 'pause':
						play_btn.icon_class = 'pause'
					break
				"""
			except IndexError:
				break

	"""
	update_cover_image
	"""
	def update_cover_image(self):
		img = self.get_cover_image()
		logger.debug('NowPlaying::update_cover_image: current: %s new: %s' % (fmuglobals.current_cover_image, img))
		fmuglobals.current_cover_image = img
		return img

	"""
	get_cover_image
	"""
	def get_cover_image(self):
		if mpd.now_playing.playing_type == 'radio':
			if mpd.now_playing.file.find('wfmu.org') != -1:
				return ui.get_image(self.image_directory + '/wfmu.png')
			else:
				return ui.get_image(self.get_default_cover_image())


		file_dir = self.music_directory + os.path.dirname(mpd.now_playing.file)
		file_name = file_dir + '/' + 'cover_art.jpg'

		print('NowPlaying::get_cover_image for %s: %s' % (mpd.now_playing.file, file_name))

		if os.path.isfile(file_name) == False:
			print('\t no existing image')
			try:
				music_file = File(self.music_directory + mpd.now_playing.file)
				if 'covr' in music_file:
					print('has covr')
					try:
						art_data = music_file.tags['covr'].data
					except:
						return ui.get_image( self.get_default_cover_image() )
				elif 'APIC:' in music_file:
					print('has APIC')
					try:
						art_data = music_file.tags['APIC:'].data
					except:
						return ui.get_image( self.get_default_cover_image() )
				else:
					print('\t no cover art data')
					return ui.get_image( self.get_default_cover_image() )

				with open(file_name, 'wb') as img:
					img.write(art_data)

			except IOError as e:
				print('\t no music file')
				return ui.get_image( self.get_default_cover_image() )

		print('\t returning: %s' % file_name)

		return ui.get_image( file_name )

	"""
	get_default_cover_image
	"""
	def get_default_cover_image(self):
		if self.current_default_cover is not False:
			return self.current_default_cover
		defaults = [name for name in os.listdir( self.default_cover_image_directory ) if os.path.isfile( self.default_cover_image_directory + '/' + name )]
		self.current_default_cover = self.default_cover_image_directory + '/' + defaults[random.randrange(0, len(defaults))]
		return self.current_default_cover
