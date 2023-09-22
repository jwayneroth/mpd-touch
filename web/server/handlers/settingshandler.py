from tornado.web import RequestHandler

from web.server.constants import *

class SettingsHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		scene = self.app.scenes['Settings']
		btn_data = scene.btn_data
		self.render("settings.html", main_nav=MAIN_NAV, title="FMULCD | Settings", btn_data=btn_data)