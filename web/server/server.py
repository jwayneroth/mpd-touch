import asyncio
import tornado.httpserver
import tornado.web
from tornado.web import StaticFileHandler, Application
from tornado.httpserver import HTTPServer
import os
from threading import Thread

from lib.mpd_client import *
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
				(r"/", IndexHandler, {"app": self.app}),
				(r"/ws", WebSocketHandler, {"web_clients": self.web_clients}),
				(r"/api/cover/?(.*)", CoverEndpoint, {"app": self.app}),
				("/api/nowplaying", NowPlayingEndpoint, {"app": self.app}),
				(r"/api/radio/?(.*)", RadioEndpoint, {"app": self.app}),
				(r"/api/library/?(.*)", LibraryEndpoint, {"app": self.app}),
				(r"/api/settings/?(.*)", SettingsEndpoint, {"app": self.app}),
				(r"/api/controls/?(.*)", ControlsEndpoint, {"app": self.app}),
			],
			debug=False,
			autoreload=False,
			template_path="web/templates"
		)
		http_server = HTTPServer(app)
		http_server.listen(8888)
		await asyncio.Event().wait()

	def start_thread(self):
		asyncio.run(self.start_server())

	def update(self):
		#logger.debug("server::update %d clients" % len(self.web_clients))
		if len(self.web_clients) > 0:
			try:
				for c in self.web_clients:
					c.write_message(json.dumps({"status" : {
						"volume": mpd.volume,
						"now_playing": {
							"type": mpd.now_playing.playing_type,
							"title": mpd.now_playing.title,
							"artist": mpd.now_playing.artist,
							"name": mpd.now_playing.name,
							"album": mpd.now_playing.album
						}
					}}).encode(encoding="utf-8"))
					#c.write_message(json.dumps({"command" : "refresh"}).encode(encoding="utf-8"))
			except Exception as e:
				logging.debug(e)
		else:
			pass
			#logger.debug("no clients to update!")

if __name__ == "__main__":
	pass
