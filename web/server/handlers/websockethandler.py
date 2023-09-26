from tornado.websocket import WebSocketHandler
import json

from web.server.constants import *

class WebSocketHandler(WebSocketHandler):
	""" Custom WebSocket handler extends Tornado handler """

	def initialize(self, web_clients):
		""" Initializer

			:param web_clients: the list of web clients
		"""
		logger.debug("WebSocketHandler initialized")

		self.web_clients = web_clients

	def open(self):
		""" Handle opening WebSocket connection """
		logger.debug("WebSocketHandler::open")

		if self not in self.web_clients:
			self.web_clients.append(self)
			logging.debug("Added web client")

	def on_message(self, message):
		""" Handle message received from web UI """
		

		d = json.loads(message)
		
		logger.debug("WebSocketHandler::on_message %s" % d)

		self.handle_command(d)

	def on_close(self):
		""" Handle closing WebSocket connection """

		logger.debug("WebSocketHandler::on_close")

		if self in self.web_clients:
			self.web_clients.remove(self)
			logging.debug("Removed web client")

	def check_origin(self, origin):
		""" Check request origin """

		return True

	def handle_command(self, d):
		""" Handle commands sent from web client 

			:param d: command object
		"""
		if d["command"] == "init":
			#self.redraw_web_ui()
			pass
		elif d["command"] == "mouse":
			a = {}
			a["pos"] = (d["x"], d["y"])
			a["button"] = d["b"]
			event = None
			if d["d"] == 0:
				event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, **a)
			elif d["d"] == 1:
				event = pygame.event.Event(pygame.MOUSEBUTTONUP, **a)
			elif d["d"] == 2:
				event = pygame.event.Event(pygame.MOUSEMOTION, **a)
				event.p = True
			event.source = "browser"
			thread = Thread(target=pygame.event.post, args=[event])
			thread.start()