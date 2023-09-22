from tornado.web import RequestHandler

from web.server.constants import *

class LibraryHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		scene = self.app.scenes['Albums']
		artists = scene.artists
		#logger.debug("LibraryHandler::get artists %s", artists)
		self.render("library.html", main_nav=MAIN_NAV, title="FMULCD | Library", artists=artists)