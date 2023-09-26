from tornado.web import RequestHandler
from tornado.escape import url_unescape

from lib.mpd_client import *
from web.server.constants import *

class LibraryEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app

	def check_autoplay(self, scene):
		autoplay = False
		if scene.new_playlist_set:
			scene.new_playlist_set = False
			autoplay = True
		return autoplay

	def get(self, resource=None):
		scene = self.app.scenes['Albums']
		
		logger.debug("LibraryEndpoint::get %s", resource)

		#try:

		if resource == None or resource == "":
			artists = scene.artists
			#logger.debug("LibraryHandler::get artists %s", artists)
			return self.render("library.html", artists=artists)

		elif resource == "artist":
			artist = url_unescape(self.get_argument('artist'))
			albums = []
			artist_albums = mpd.mpd_client.list('album','artist', artist)

			for album in artist_albums:
				if 'album' in album and album['album'] != '':
					albums.append(album['album'])

			self.finish({'albums': albums})

		elif resource == "add-artist":
			artist = url_unescape(self.get_argument('artist'))
			autoplay = self.check_autoplay(scene)
			mpd.playlist_add('artist', artist, autoplay, False)
			self.finish()

		elif resource == "album":
			album = url_unescape(self.get_argument('album'))
			tracks = []
			album_tracks = mpd.mpd_client.list('title','album', album)
			logger.debug('LibraryEndpoint::get album %s', album_tracks)
			for track in album_tracks:
				if 'title' in track and track['title'] != '':
					tracks.append(track['title'])

			self.finish({'tracks': tracks})

		elif resource == "add-album":
			album = url_unescape(self.get_argument('album'))
			autoplay = self.check_autoplay(scene)
			mpd.playlist_add('album', album, autoplay, False)
			self.finish()

		elif resource == "add-artist-albums":
			artist = url_unescape(self.get_argument('artist'))
			autoplay = self.check_autoplay(scene)
			mpd.playlist_add('artist', artist, autoplay, False)
			self.finish()

		elif resource == "add-track":
			track = url_unescape(self.get_argument('track'))
			autoplay = self.check_autoplay(scene)
			mpd.playlist_add('title', track, autoplay, False)
			self.finish()

		elif resource == "new-playlist":
			mpd.set_playback('stop')
			mpd.clear_current_playlist()
			scene.new_playlist_set = True
			self.finish()

		# except:
		# 	self.set_status(500)
		# 	return self.finish()