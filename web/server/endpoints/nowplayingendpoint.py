from tornado.web import RequestHandler

from lib.mpd_client import *
from web.server.constants import *

class NowPlayingEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		volume = mpd.volume
		playing_type = mpd.now_playing.playing_type
		title = mpd.now_playing.title
		artist = mpd.now_playing.artist
		name = mpd.now_playing.name
		album = mpd.now_playing.album

		self.render("nowplaying.html", artist=artist, album=album, track=title)