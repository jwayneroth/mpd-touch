import pygame
from PIL import Image
from io import BytesIO
from tornado.web import RequestHandler

from web.server.constants import *

class CoverEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get_png_from_surface(self, surface):
		""" Convert Pygame Surface to PNG image

			:param surface: Pygame Surface object

			:return: PNG image
		"""
		if surface == None:
			return None

		s = None
		try:
			d = pygame.image.tostring(surface, "RGBA", False)
			img = Image.frombytes("RGBA", surface.get_size(), d)
			buffer = BytesIO()
			img.save(buffer, "PNG")
			s = buffer.getvalue()
		except Exception as e:
			logging.debug(e)

		return s

	def get(self):
		logger.debug("CoverHandler::get")
		try:
			s = self.app.scenes['NowPlaying']
			if not s:
				logger.debug("no NowPlaying scene!")
				return

			center_button = s.components['album_cover']
			content = center_button.image
			
			img = self.get_png_from_surface(content)
			
			#logger.debug("got img %s" % img)
			
			self.set_header("Content-Type", "image/png")
			self.write(img)
		except:
			self.set_status(500)
			return self.finish()