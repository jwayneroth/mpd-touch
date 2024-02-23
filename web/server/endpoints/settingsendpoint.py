from tornado.web import RequestHandler
import feedparser

from web.server.constants import *

class SettingsEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self, resource):
		scene = self.app.scenes['Settings']
		
		if resource == "":
			btn_data = scene.btn_data
			ss_types = self.app.screensavers
			current_type = self.app.ss_type
			return self.render("settings.html", btn_data=btn_data, ss_types=ss_types, current_type=current_type)

		else:
			for btn in scene.btns:
				if btn.name == resource:
					btn.on_clicked(btn, False)
					return self.finish()

		self.set_status(500)
		return self.finish()

	def post(self, resource):
		if resource == 'screensaver':
			type = self.get_argument('type')
			self.app.set_screensaver_type(type)
			return self.finish({'ss_type': self.app.ss_type})