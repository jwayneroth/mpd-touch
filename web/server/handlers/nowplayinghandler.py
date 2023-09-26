from tornado.web import RequestHandler

from lib.mpd_client import *
from web.server.constants import *

class NowPlayingHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		#nowplaying = self.app.scenes['NowPlaying']
		#artist = nowplaying.components['artist'].text
		#album = nowplaying.components['album'].text
		#track = nowplaying.components['track'].text

		#type = mpd.now_playing.playing_type
		track = mpd.now_playing.title
		artist = mpd.now_playing.artist
		#name = mpd.now_playing.name
		album = mpd.now_playing.album

		self.render("nowplaying.html", title="FMULCD", main_nav=MAIN_NAV, artist=artist, album=album, track=track)

