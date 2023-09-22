from tornado.web import RequestHandler

from web.server.constants import *

class NowPlayingHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		nowplaying = self.app.scenes['NowPlaying']
		#cover = self.get_png_from_surface(nowplaying.components['album_cover'].image)
		#logger.debug(cover)
		artist = nowplaying.components['artist'].text
		album = nowplaying.components['album'].text
		track = nowplaying.components['track'].text
		
		self.render("nowplaying.html", title="FMULCD", main_nav=MAIN_NAV, artist=artist, album=album, track=track)

