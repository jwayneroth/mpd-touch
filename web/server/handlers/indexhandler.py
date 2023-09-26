from tornado.web import RequestHandler

from lib.mpd_client import *
from web.server.constants import *

class IndexHandler(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self):
		self.render("index.html", title="FMULCD")

