from tornado.web import RequestHandler
from tornado.escape import url_unescape
import feedparser
import re
import urllib
import json

from lib.mpd_client import *
from web.server.constants import *

class RadioEndpoint(RequestHandler):
	def initialize(self, app):
		self.app = app
		self.url_opener = urllib.request

	def get(self, resource):
		scene = self.app.scenes['Radio']
		
		logger.debug("RadioEndpoint::get %s", resource)
		
		try:

			if resource == "":
				stations = scene.stations
				return self.render("radio.html", stations=stations)

			elif resource == "stream":
				stream = url_unescape(self.get_argument('stream'))
				logger.debug('stream url: %s', stream)
				mpd.radio_station_start(stream)
				self.finish()

			elif resource == "archive":
				archive = url_unescape(self.get_argument('archive'))
				try:
					res = self.url_opener.urlopen( archive )
					logger.debug("opened archive url: %s", res)
					html = res.read()
				except:
					logger.debug("error opening archive")
					self.finish()
					return
				archive_url = str(html, 'utf-8').strip()
				mpd.radio_station_start(archive_url)
				self.finish()

			elif resource == "archives":
				archives = []
				try:
					full = feedparser.parse('https://www.wfmu.org/archivefeed/mp3.xml')
					for entry in full.entries:
						archive = dict()
						archive['title'] = scene.filter_stream_name(entry.title)
						archive['url'] = entry.link
						archives.append(archive)
				except:
					pass
				self.write({'archives': archives})

			elif resource == "status":
				title = url_unescape(self.get_argument('title'))
				url = url_unescape(self.get_argument('url'))
				url_opener = urllib.request
				try:
					res = self.url_opener.urlopen( url )
					html = res.read()
				except:
					logger.debug("error opening stream status json")
					return

				stripped = str(html, 'utf-8').strip()

				self.write({'title': title, 'status': json.loads(stripped)})

		except:
			self.set_status(500)
			return self.finish()