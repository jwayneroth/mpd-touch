import asyncio
import tornado.httpserver
import tornado.web
from tornado.web import StaticFileHandler, Application
from tornado.httpserver import HTTPServer
import os
from threading import Thread

from web.server.constants import *
from .handlers import * 
from .endpoints import * 

class Server(object):
	""" Starts Tornado web server in a separate thread """
	def __init__(self, app):
		logger.debug('Server::__init__')

		self.instance = None
		self.app = app
		self.web_clients = []
		#self.player_listeners = []

		thread = Thread(target=self.start_thread)
		thread.daemon = True
		thread.start()

	async def start_server(self):

		root = os.getcwd()

		logger.debug('Server::start_server %s' % root)

		app = Application(
			[
				(r"/assets/(.*)", StaticFileHandler, {"path": root + "/web/client/public"}),
				(r"/", NowPlayingHandler, {"app": self.app}),
				(r"/library", LibraryHandler, {"app": self.app}),
				(r"/radio", RadioHandler, {"app": self.app}),
				(r"/settings", SettingsHandler, {"app": self.app}),
				(r"/ws", WebSocketHandler, {"redraw_web_ui": self.redraw_web_ui, "web_clients": self.web_clients}),
				("/api/cover", CoverEndpoint, {"app": self.app}),
				("/api/radio/(.*)", RadioEndpoint, {"app": self.app}),
				("/api/library/(.*)", LibraryEndpoint, {"app": self.app}),
				("/api/settings/(.*)", SettingsEndpoint, {"app": self.app}),
				("/api/controls/(.*)", ControlsEndpoint, {"app": self.app}),
			],
			debug=False,
			autoreload=True,
			template_path="web/templates"
		)
		http_server = HTTPServer(app)
		http_server.listen(8888)
		await asyncio.Event().wait()

	def start_thread(self):
		asyncio.run(self.start_server())

	# def update_player_listeners(self, state=None):
	# 	""" Update player listeners """

	# 	if len(self.web_clients) == 0:
	# 		return

		# for c in self.player_listeners:
		# 	self.send_json_to_web_ui(self.json_factory.container_to_json(c))

	def redraw_web_ui(self, state=None):
		""" Redraw the whole screen in web UI """

		if len(self.web_clients) == 0:
			return

		#self.send_json_to_web_ui(self.screen_to_json())

	def update_clients(self):
		logger.debug("Server::update_clients")
		self.send_json_to_web_ui()

	def send_json_to_web_ui(self):
		""" Send provided Json object to all web clients
				
			"param j": Json object to send
		"""
		if len(self.web_clients) == 0:
			logger.debug("no clients to update!")
			return


		try:
			for c in self.web_clients:
				#e = json.dumps(j).encode(encoding="utf-8")
				#self.instance.add_callback(c.write_message, e)
				c.write_message(json.dumps({"command" : "refresh"}).encode(encoding="utf-8"))
		except Exception as e:
			logging.debug(e)

if __name__ == "__main__":
	pass