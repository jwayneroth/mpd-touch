from tornado.web import RequestHandler
from tornado.escape import url_unescape
import feedparser
import re
import urllib
from urllib.request import Request, urlopen
import json
from bs4 import BeautifulSoup

from lib.mpd_client import *
from web.server.constants import *

class RadioEndpoint(RequestHandler):
	def parse_fmu_statuses(self):
		# print('parse_fmu_statuses')
		STATUS_URL = "https://wfmu.org/currentliveshows_aggregator.php?ch=1,4,6,8"
		req = Request(
			url = STATUS_URL,
			headers = {'User-Agent': 'Mozilla/5.0'}
		)
		statuses = urlopen( req ).read()
		#print('statues {0}'.format(statuses))
		soup = BeautifulSoup(statuses, 'html.parser')
		streams = soup.find_all('div', {'class': 'item-even'}) + soup.find_all('div', {'class': 'item-odd'})
		streams_parsed = []
		for stream in streams:
			title = stream.find('div', {'class': 'streamtitle'})
			if (title) :
				title.a.extract()
				title = title.get_text().replace('()', '').strip()
			print('stream {0}'.format(title))
			track = stream.find('div', {'class': 'bigline'})
			if (track) :
				track = track.get_text().strip()
			# print('track {0}'.format(track))
			show = stream.find('div', {'class': 'smallline'})
			if (show) :
				show = show.get_text().strip()
			# print('show {0}'.format(show))
			if (title) :
				streams_parsed.append({
					'title': title,
					'track': track,
					'show': show
				})
		# print('streams_parsed: {0}', streams_parsed)
		return streams_parsed

	def initialize(self, app):
		self.app = app
		#self.url_opener = urllib.request

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
				archive_url = self.get_argument('archive')
				logger.debug("archive url: %s", archive_url)
				archive = url_unescape(archive_url)
				logger.debug("unescaped url: %s", archive)
				req = Request(
					url=archive,
					headers={'User-Agent': 'Mozilla/5.0'}
				)
				try:
					html = urlopen( req ).read()
				except:
					logger.debug("error opening archive")
					self.finish()
					return
				logger.debug("opened archive url: %s", archive)
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

						query = urllib.parse.parse_qs( urllib.parse.urlparse( entry.guid ).query )
						show = query.get("show", [None])[0]
						archive['show'] = show

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

			elif resource == "status-all":
				try:
					statuses = self.parse_fmu_statuses()
				except:
					logger.debug("error parsing php status")
					return

				print('status-all statuses: {0}', statuses)
				self.write({'statuses': statuses})

		except:
			self.set_status(500)
			return self.finish()
