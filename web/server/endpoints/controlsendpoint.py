from tornado.web import RequestHandler

from lib.mpd_client import *
from web.server.constants import *

class ControlsEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app

	def get(self, resource):
		logger.debug("ControlsEndpoint::get %s", resource)

		if resource == 'volume':
			return self.finish({'volume': mpd.volume})
		else:
			scene = self.app.dialogs['Controls']

			class Object(object):
				pass

			btn = scene.buttons[resource]
			scene.on_button_click(btn, None)

			self.finish({'play_state': mpd.get_playback(), 'play_mode': scene.play_modes[scene.current_play_mode]})

	def post(self, resource):
		if resource == 'volume':
			volume = self.get_argument('volume')
			try:
				mpd.set_volume(int(volume))
			except:
				self.set_status(500)
				pass
			scene = self.app.dialogs['Controls']
			scene.volume_slider.value = mpd.volume
			return self.finish({'volume': mpd.volume})