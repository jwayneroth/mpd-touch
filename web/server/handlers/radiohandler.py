from tornado.web import RequestHandler

from web.server.constants import *

class RadioHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		scene = self.app.scenes['Radio']
		stations = scene.stations
		self.render("radio.html", main_nav=MAIN_NAV, title="FMULCD | Radio", stations=stations)