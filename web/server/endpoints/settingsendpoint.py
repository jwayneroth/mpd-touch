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
			return self.render("settings.html", btn_data=btn_data)

		else:
			for btn in scene.btns:
				if btn.name == resource:
					btn.on_clicked(btn, False)
					return self.finish()

		self.set_status(500)
		return self.finish()

		# class Object(object):
		# 	pass

		# btn = Object()
		# btn.name = resource

		# try:

		# 	if resource == "update":
		# 		self.finish('updated')
		# 		scene.on_btn_clicked(btn, None)
		# except:
		# 	self.set_status(500)
		# 	return self.finish()