import sys, pygame
import time
import subprocess
import os
import glob
import random

from PersistentMPDClient import PersistentMPDClient
from collections import deque
#from ..mutagen import File
from pygameui import callback as callback

import logging
logger = logging.getLogger('fmu_logger')

MPD_TYPE_ARTIST = 'artist'
MPD_TYPE_ALBUM = 'album'
MPD_TYPE_SONGS = 'title'

TEMP_PLAYLIST_NAME = '_pi-jukebox_temp'

reload(sys)
sys.setdefaultencoding('utf8')

class MPDController(object):
	def __init__(self):
		self.host = 'localhost'
		self.port = 6600
		self.mpd_client = PersistentMPDClient(None, self.host, self.port);
		self.update_interval = 1800
		self.volume = 0
		self.current_playlist = []
		self.repeat = False
		self.random = False
		self.single = False
		self.consume = False
		self.updating_library = False
		self.now_playing = MPDNowPlaying()
		self.events = deque([])
		self.searching_artist = ""
		self.searching_album = ""
		self.list_albums = []
		self.list_artists = []
		self.list_songs = []
		self.list_query_results = []

		self.__music_directory = ""
		self.__song_status = {'album':'','artist':'','file':''}
		self.__now_playing_changed = False
		self.__player_control = ''
		self.__muted = False
		self.__current_playlist_playing_index = 0
		self.__last_update_time = 0
		self.__status = {}
		
		self.on_album_changed = callback.Signal()

	def dict_to_string(self, dict):
		print ', '.join("%s=%r" % (key,val) for (key,val) in dict.iteritems())

	def connect(self):
		self.mpd_client.connect(self.host, self.port)
		return True

	def disconnect(self):
		self.mpd_client.close()
		self.mpd_client.disconnect()

	def music_directory_set(self, path):
		self.now_playing.music_directory = path
		self.__music_directory = path

	"""
	parse_mpc_status
	 parse the mpd status and fill mpd event queue
	 return boolean indicating if the status was changed
	"""
	def parse_mpc_status(self):
	
		status_change = False

		song_status = self.mpd_client.currentsong()

		if self.__song_status != song_status and len(song_status) > 0:

			self.now_playing.update_status( song_status )
	
			if 'album' in song_status:

				if 'album' in self.__song_status:
					if song_status['album'] != self.__song_status['album']:
						self.events.append('album_change')
						status_change = True

				else:
					self.events.append('album_change')
					status_change = True

			else:
				if self.now_playing.album != '':
					self.events.append('album_change')
					status_change = True

			if 'title' in song_status:

				if 'title' in self.__song_status:

					if song_status['title'] != self.__song_status['title']:
						self.events.append('title_change')
						status_change = True

				else:
					self.events.append('title_change')
					status_change = True

			else:
				if 'file' in self.__song_status and self.now_playing.title != os.path.splitext(os.path.basename(self.__song_status['file']))[0]:
					self.events.append('title_change')
					status_change = True

			self.__song_status = song_status

		status = self.mpd_client.status()

		# if our playback status is unchanged, end parsing
		if self.__status == status:
			return status_change
		
		self.__status = status

		self.playback_options_get(status)

		if self.volume != int(status['volume']):
			self.volume = int(status['volume'])
			self.events.append('volume')
			self.__muted = self.volume == 0
			status_change = True

		if self.__player_control != status['state']:
			self.__player_control = status['state']
			self.events.append('player_control')
			status_change = True

		if self.__player_control != 'stop':
			if self.__current_playlist_playing_index != int(status['song']):
				self.__current_playlist_playing_index = int(status['song'])
				#self.events.append('playing_index')
				#status_change = True

			#if self.now_playing.current_time_set(self.str_to_float(status['elapsed'])):
				#self.events.append('time_elapsed')
				#status_change = True

		else:
			if self.__current_playlist_playing_index != -1:
				self.__current_playlist_playing_index = -1
				#self.events.append('playing_index')
				#status_change = True

				#if self.now_playing.current_time_set(0):
					#self.events.append('time_elapsed')

		return status_change

	def playback_options_get(self, status):
		if self.repeat != status['repeat'] == '1':
			self.repeat = status['repeat'] == '1'
			self.events.append('repeat')
		if self.random != status['random'] == '1':
			self.random = status['random'] == '1'
			self.events.append('random')
		if self.single != status['single'] == '1':
			self.single = status['single'] == '1'
			self.events.append('single')
		if self.consume != status['consume'] == '1':
			self.consume = status['consume'] == '1'
			self.events.append('consume')

	def str_to_float(self, s):
		try:
			return float(s)
		except ValueError:
			return float(0)

	def status_get(self):

		gt = pygame.time.get_ticks()

		time_elapsed = gt - self.__last_update_time

		if gt > self.update_interval and time_elapsed < self.update_interval:
			return False

		self.__last_update_time = gt

		return self.parse_mpc_status()

	def current_song_changed(self):
		if self.__now_playing_changed:
			self.__now_playing_changed = False
			return True
		return False

	def set_playback(self, play_status):
		if play_status == 'play':
			if self.__player_control == 'pause':
				self.mpd_client.pause(0)
			else:
				self.mpd_client.play()
		elif play_status == 'pause':
			self.mpd_client.pause(1)
		elif play_status == 'stop':
			self.mpd_client.stop()
		elif play_status == 'next':
			logger.debug('set_playback next %d of %d' % (self.get_current_playlist_playing_index() + 1, self.current_playlist_count()))
			if self.get_current_playlist_playing_index() < self.current_playlist_count() - 1:
				self.mpd_client.next()
		elif play_status == 'previous':
			logger.debug('set_playback previous %d of %d' % (self.get_current_playlist_playing_index() - 1, self.current_playlist_count()))
			if self.get_current_playlist_playing_index() > 0:
				self.mpd_client.previous()

	def get_playback(self):
		self.status_get()
		return self.__player_control

	def play_playlist_item(self, index):
		self.mpd_client.play(index - 1)

	def set_volume(self, percentage):
		if percentage < 0 or percentage > 100: return
		self.mpd_client.setvol(percentage)
		self.volume = percentage

	def set_volume_relative(self, percentage):
		if self.volume + percentage < 0:
			self.volume = 0
		elif self.volume + percentage > 100:
			self.volume = 100
		else:
			self.volume += percentage
		self.mpd_client.setvol(self.volume)

	def toggle_muted(self):
		if self.__muted:
			self.mpd_client.setvol(self.volume)
			self.__muted = False
		else:
			self.mpd_client.setvol(0)
			self.__muted = True

	def get_muted(self):
		return self.__muted

	def toggle_random(self):
		self.random = not self.random
		if self.random:
			self.mpd_client.random(1)
		else:
			self.mpd_client.random(0)

	def toggle_repeat(self):
		self.repeat = not self.repeat
		if self.repeat:
			self.mpd_client.repeat(1)
		else:
			self.mpd_client.repeat(0)

	def toggle_single(self):
		self.single = not self.single
		if self.consume:
			self.mpd_client.single(1)
		else:
			self.mpd_client.single(0)

	def toggle_consume(self):
		self.consume = not self.consume
		if self.consume:
			self.mpd_client.consume(1)
		else:
			self.mpd_client.consume(0)

	def get_current_playlist(self):
		self.current_playlist = []
		playlist_info = []
		playlist_info = self.mpd_client.playlistinfo()
		track_no = 0
		for i in playlist_info:
			track_no += 1
			if 'title' in i:
				self.current_playlist.append(str(track_no) + '. ' + i['title'])
			else:
				self.current_playlist.append(str(track_no) + '. ' + os.path.splitext(os.path.basename(i['file']))[0])
		return self.current_playlist

	def get_current_playlist_playing_index(self):
		self.status_get()
		return self.__current_playlist_playing_index

	def set_current_playlist_playing_index(self, index):
		if index > 0 and index <= self.current_playlist_count():
			self.mpd_client.playid(index)
			self.__current_playlist_playing_index = index
		return self.__current_playlist_playing_index

	def current_playlist_count(self):
		return len(self.current_playlist)

	def clear_current_playlist(self):
		self.mpd_client.clear()
		self.current_playlist = []

	def library_update(self):
		self.mpd_client.update()

	def library_rescan(self):
		self.mpd_client.rescan()

	def __search(self, tag_type):
		self.list_query_results = self.mpd_client.list(tag_type)
		self.list_query_results.sort()
		return self.list_query_results

	def __search_first_letter(self, tag_type, first_letter):
		temp_results = []
		for i in self.list_query_results:
			if i[:1].upper() == first_letter.upper():
				temp_results.append(i)
		self.list_query_results = temp_results
		return self.list_query_results

	def __search_partial(self, tag_type, part):
		all_results = []
		all_results = self.mpd_client.list(tag_type)
		self.list_query_results = []
		all_results.sort()
		for i in all_results:
			result = i.upper()
			if result.find(part.upper()) > -1:
				self.list_query_results.append(i)
		return self.list_query_results

	def __search_of_type(self, type_result, type_filter, name_filter):
		if self.searching_artist == "" and self.searching_album == "":
			self.list_query_results = self.mpd_client.list(type_result, type_filter, name_filter)
		elif self.searching_artist != "" and self.searching_album == "":
			self.list_query_results = self.mpd_client.list(
				type_result,
				'artist',
				self.searching_artist,
				type_filter,
				name_filter
			)
		elif self.searching_artist == "" and self.searching_album != "":
			self.list_query_results = self.mpd_client.list(
				type_result, 'album',
				self.searching_album,
				type_filter,
				name_filter
			)
		elif self.searching_artist != "" and self.searching_album != "":
			self.list_query_results = self.mpd_client.list(
				type_result, 'artist',
				self.searching_artist,
				'album',
				self.searching_album,
				type_filter,
				name_filter
			)
		self.list_query_results.sort()
		return self.list_query_results

	def get_artists(self, part=None, only_start=True):
		self.searching_artist = ""
		self.searching_album = ""
		if part is None:
			if len(self.list_artists) == 0:
				self.list_artists = self.__search('artist')
			return self.list_artists
		elif only_start:
			self.list_query_results = self.__search_first_letter('artist', part)
		else:
			self.list_query_results = self.__search_partial('artist', part)
		return self.list_query_results

	def get_albums(self, part=None, only_start=True):
		self.searching_artist = ""
		self.searching_album = ""
		if part is None:
			if len(self.list_albums) == 0:
				self.list_albums = self.__search('album')
			return self.list_albums
		elif only_start:
			self.list_query_results = self.__search_first_letter('album', part)
		else:
			self.list_query_results = self.__search_partial('album', part)
		return self.list_query_results

	def get_songs(self, part=None, only_start=True):
		self.searching_artist = ""
		self.searching_album = ""
		if part is None:
			if len(self.list_songs) == 0:
				self.list_songs = self.__search('title')
			return self.list_songs
		elif only_start:
			self.list_query_results = self.__search_first_letter('title', part)
		else:
			self.list_query_results = self.__search_partial('title', part)
		return self.list_query_results

	def get_artist_albums(self, artist_name):
		self.searching_artist = artist_name
		return self.__search_of_type('album', 'artist', artist_name)

	def get_artist_songs(self, artist_name):
		self.searching_artist = artist_name
		return self.__search_of_type('title', 'artist', artist_name)

	def get_album_songs(self, album_name):
		self.searching_album = album_name
		return self.__search_of_type('title', 'album', album_name)

	def get_playlists(self, first_letter=None):
		result_list = []
		all_playlists = []
		all_playlists = self.mpd_client.listplaylists()
	
		if first_letter is None:
			for playlist in all_playlists:
				result_list.append(playlist['playlist'])
		else:
			for playlist in all_playlists:
				if playlist['playlist'][:1].upper() == first_letter.upper():
					result_list.append(playlist['playlist'])
		return result_list

	def list_directory(self, path="", first_letter=None):
		result_list = []
		list_directory = []
		path_entries = None
		path_entries = self.mpd_client.lsinfo(path)
	
		for entry in path_entries:
			if 'directory' in entry:
				list_directory.append(('directory', entry['directory']))
			elif 'file' in entry:
				list_directory.append(('file', entry['file']))

		if first_letter is None:
			result_list = list_directory
		else:
			for entry in list_directory:
				if 'directory' in entry:
					if entry['directory'][:1].upper() == first_letter.upper():
						result_list.append(('directory', entry['directory']))
				elif 'file' in entry:
					if entry['file'][:1].upper() == first_letter.upper():
						result_list.append(('file', os.path.basename(entry['file'])))
		return result_list

	def get_directory_songs(self, path=""):
		contents_list = self.__get_directory_recursive(path)
		songs_list = []
		for entry in contents_list:
			if 'file' in entry:
				songs_list.append(entry)
		return songs_list

	def __get_directory_recursive(self, path=""):
		content_list = []
		content_list = self.mpd_client.lsinfo(path)
		for entry in content_list:
			if 'directory' in entry:
				content_list += self.__get_directory_recursive(entry['directory'])
		return content_list

	"""
	Adds songs to the current playlist
	
	 :param tag_type: Kind of add you want to do ["artist", "album", song"title"].
	 :param tag_name: The name of the tag_type.
	 :param play: Boolean indicating whether you want to start playing what was just added.
	 :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
	"""
	def playlist_add(self, tag_type, tag_name, play=False, clear_playlist=False):
		if clear_playlist:
			self.clear_current_playlist()
		i = self.current_playlist_count()
		if self.searching_artist == "" and self.searching_album == "":
			self.mpd_client.findadd(tag_type, tag_name)
		elif self.searching_artist != "" and self.searching_album == "":
			self.mpd_client.findadd('artist', self.searching_artist, tag_type, tag_name)
		elif self.searching_artist == "" and self.searching_album != "":
			self.mpd_client.findadd('album', self.searching_album, tag_type, tag_name)
		elif self.searching_artist != "" and self.searching_album != "":
			self.mpd_client.findadd('artist', self.searching_artist, 'album', self.searching_album, tag_type, tag_name)
		self.get_current_playlist()
		if play:
			self.play_playlist_item(i + 1)

	def playlist_add_artist(self, artist_name, play=False, clear_playlist=False):
		self.playlist_add('artist', artist_name, play, clear_playlist)

	def playlist_add_album(self, album_name, play=False, clear_playlist=False):
		self.playlist_add('album', album_name, play, clear_playlist)

	def playlist_add_song(self, song_name, play=False, clear_playlist=False):
		self.playlist_add('title', song_name, play, clear_playlist)

	def playlist_add_playlist(self, playlist_name, play=False, clear_playlist=False):
		if clear_playlist:
			self.clear_current_playlist()
		i = self.current_playlist_count()
		self.mpd_client.load(playlist_name)
		if play:
			self.play_playlist_item(i + 1)

	def playlist_add_file(self, uri, play=False, clear_playlist=False):
		self.clear_current_playlist()
		i = self.current_playlist_count()
		self.mpd_client.addid(uri)
		if play:
			self.play_playlist_item(i + 1)

	def playlist_add_directory(self, path, play=False, clear_playlist=False):
		if clear_playlist:
			self.clear_current_playlist()
		i = self.current_playlist_count()
		songs = self.get_directory_songs(path)
		for song in songs:
			self.mpd_client.addid(song['file'])
		if play:
			self.play_playlist_item(i + 1)

	def radio_station_start(self, station_URL):
		self.get_current_playlist()
		self.mpd_client.rm(TEMP_PLAYLIST_NAME)
		self.mpd_client.save(TEMP_PLAYLIST_NAME)
		self.clear_current_playlist()
		self.mpd_client.addid(station_URL)
		self.mpd_client.play(0)

class MPDNowPlaying(object):

	def __init__(self):
		self.playing_type = ''
		self.title = ""
		self.artist = ""
		self.name = ""
		self.album = ""
		self.file = ""
		self.__time_current_sec = 0
		self.time_current = ""
		self.__time_total_sec = 0
		self.time_total = ""
		self.time_percentage = 0
		self.music_directory = "/var/lib/mpd/music/"

	def update_status(self, song_status=None):

		self.title = ""
		self.artist = ""
		self.album = ""
		self.name = ""
		self.file = ""
		self.time_percentage = 0
		self.__time_total_sec = 0
		self.time_total = self.make_time_string(0)
		
		if song_status is not None:

			try:
				self.file = song_status['file']
				if self.file[:7] == "http://":
					self.playing_type = 'radio'
				else:
					self.playing_type = 'file'
			except KeyError:
				self.playing_type = 'file'
				return

			if 'title' in song_status:
				self.title = song_status['title']
			else:
				self.title = os.path.splitext(os.path.basename(song_status['file']))[0]

			if self.playing_type == 'file':

				if 'artist' in song_status:
					self.artist = song_status['artist']

				if 'album' in song_status:
					self.album = song_status['album']

				current_total = self.str_to_float(song_status['time']) if 'time' in song_status else 0
				self.__time_total_sec = current_total
				self.time_total = self.make_time_string(current_total)

			elif self.playing_type == 'radio':

				if 'name' in song_status:
					self.album = song_status['name']

	def current_time_set(self, seconds):
		if self.__time_current_sec != seconds:
			self.__time_current_sec = seconds
			self.time_current = self.make_time_string(seconds)
			if self.playing_type != 'radio':
				self.time_percentage = int(self.__time_current_sec / self.__time_total_sec * 100)
			else:
				self.time_percentage = 0
			return True
		else:
			return False

	def make_time_string(self, seconds):
		minutes = int(seconds / 60)
		seconds_left = int(round(seconds - (minutes * 60), 0))
		time_string = str(minutes) + ':'
		seconds_string = ''
		if seconds_left < 10:
			seconds_string = '0' + str(seconds_left)
		else:
			seconds_string = str(seconds_left)
		time_string += seconds_string
		return time_string

	def str_to_float(self, s):
		try:
			return float(s)
		except ValueError:
			return float(0)

mpd = MPDController()
