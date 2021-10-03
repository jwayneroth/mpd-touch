import feedparser
import re
import urllib

from piscrollscene import *

"""
RadioScene
 radio options, playback controls
"""
class RadioScene(PiScrollScene):
	def __init__(self, frame):

		PiScrollScene.__init__(self, frame, 'Radio')

		self.sidebar_index = 2
		self.active_sidebar_btn = 2

		page_nav = self.make_page_nav()

		self.stations = [
			{'title':'WFMU','url':'http://stream0.wfmu.org/freeform-128k'},
			{'title':'GtDR','url':'http://stream0.wfmu.org:80/drummer'},
			{'title':'Rock \'n Soul','url':'http://stream0.wfmu.org/rocknsoul'},
			#{'title':'Ubu','url':'http://stream0.wfmu.org/ubu'},
			{'title':'Sheena','url':'http://stream0.wfmu.org/sheena'},
			{'title':'FMU32','url':'http://stream0.wfmu.org/freeform-32k.mp3'},
			{'title':'wkcr','url':'http://wkcr.streamguys1.com:80/live'},
			{'title':'wnyc','url':'http://fm939.wnyc.org/wnycfm'},
			{'title':'bbc','url':'http://am820.wnyc.org/wnycam'},
			{'title':'wqxr','url':'http://stream.wqxr.org/wqxr'},
			{'title':'q2','url':'http://q2stream.wqxr.org/q2'},
			{'title':'wcbs','url':'https://18843.live.streamtheworld.com/WCBSAMAAC_SC?sbmid=dff673a8-4f30-4100-9c2f-ee9a8beae226&DIST=CBS&TGT=radiocomPlayer&SRC=CBS&lsid=cookie:eb568720-186f-49a3-866f-879754cfc515'},
			{'title':'wbgo','url':'http://wbgo.streamguys.net/wbgo128'},
			{'title':'wbgo jazz','url':'http://wbgo.streamguys.net/thejazzstream'},
			{'title':'wfuv','url':'https://onair.wfuv.org/onair-hi'},
			{'title':'wmuh','url':'http://192.104.181.26:8000/stream'}
		]

		self.url_opener = urllib.FancyURLopener({})

		self.streams_view = self.make_scroll_view()
		self.archives_view = self.make_scroll_view()

		self.station_btns = [page_nav]
		self.archive_btns = [page_nav]
		
		self.child_view_btns = [
			self.station_btns,
			self.archive_btns
		]

		self.populate_streams_view()
		self.populate_archives_view()

		self.main.add_child(self.streams_btn)
		self.main.add_child(self.archives_btn)
		self.main.add_child(self.page_down)
		self.main.add_child(self.icon_down)
		self.main.add_child(self.page_up)
		self.main.add_child(self.icon_up)
		self.main.add_child(self.streams_view)
		
		self.current_child = self.streams_view

	"""
	update_btn_row
	 update the active btn row idx and its reference for the active scroll view
	"""
	def update_btn_row(self, new_index):
		self.active_btn_row = new_index
		self.active_btn_index = 0

	"""
	populate_streams_view
	"""
	def populate_streams_view(self):

		scroll_contents = ui.View(
			ui.Rect(
				0,0,
				self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
				self.main.frame.height
			)
		)

		del self.station_btns[:]

		#station_idx = 0

		btn_x = 0

		scr_y = 0
		
		row_count = len(self.stations)

		for station in self.stations:

			btn = ui.Button( ui.Rect( btn_x, scr_y, self.main.frame.width - ui.SCROLLBAR_SIZE, self.label_height ), station['title'], halign=ui.LEFT, valign=ui.CENTER )

			btn.url = station['url']
			btn.on_clicked.connect(self.on_station_clicked)
			btn.sibling = False

			self.station_btns.append([btn])

			scroll_contents.add_child(btn)

			scr_y = scr_y + self.label_height

			#station_idx = station_idx + 1

			#if station_idx > 6:
			#	scr_y = 0
			#	btn_x = 250

		scroll_contents.frame.height = row_count * self.label_height

		self.streams_view.update_content_view(scroll_contents)

		if self.streams_view.scrollable:
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()

		self.station_btns.insert(0, [self.streams_btn, self.archives_btn, self.page_down, self.page_up])

	"""
	populate_archives_view
	"""
	def populate_archives_view(self):

		scroll_contents = ui.View(
			ui.Rect(
				0,0,
				self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
				self.main.frame.height
			)
		)

		refresh_icon = ui.IconButton(ui.Rect(0,0,self.btn_size,self.btn_size),'refresh')
		refresh_icon.on_clicked.connect(self.refresh_archives_click)

		refresh_btn = ui.Button(ui.Rect(self.btn_size,0,self.main.frame.width - ui.SCROLLBAR_SIZE - self.btn_size - self.margins,self.btn_size),'refresh',halign=ui.LEFT,valign=ui.CENTER)
		refresh_btn.on_clicked.connect(self.refresh_archives_click)

		refresh_btn.sibling = False

		scroll_contents.add_child(refresh_icon)
		scroll_contents.add_child(refresh_btn)

		archives = []

		try:
			full = feedparser.parse('http://www.wfmu.org/archivefeed/mp3.xml')
			for entry in full.entries:
				archive = dict()
				archive['title'] = self.filter_stream_name(entry.title)
				archive['url'] = entry.link
				archives.append(archive)
		except:
			pass

		del self.archive_btns[:]

		self.archive_btns.append([refresh_btn])

		scr_y = self.btn_size + self.margins
		row_count = len(archives)

		for archive in archives:

			btn = ui.Button(
				ui.Rect( 0, scr_y, self.main.frame.width - ui.SCROLLBAR_SIZE, self.label_height ),
				archive['title'],
				halign=ui.LEFT,
				valign=ui.CENTER
			)

			btn.url = archive['url']
			btn.on_clicked.connect(self.on_archive_clicked)
			btn.sibling = False

			self.archive_btns.append([btn])

			scroll_contents.add_child(btn)

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.btn_size + self.margins

		self.archives_view.update_content_view(scroll_contents)

		if self.archives_view.scrollable:
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()

		self.archive_btns.insert(0, [self.streams_btn, self.archives_btn, self.page_down, self.page_up])

	"""
	filter_stream_name
	"""
	def filter_stream_name(self, raw):
		rdict = {
			'WFMU Freeform Radio' : 'WFMU',
			'with ' : 'w/',
			'Give the Drummer Some' : 'GtDS',
			'Give the Drummer Radio on WFMU' : 'GtDR',
			'Rock \'n\' Soul Ichiban from WFMU' : 'Ichiban',
			'UbuWeb Radio on WFMU' :  'Ubu',
			'Radio Boredcast on WFMU' : 'Boredcast',
			'WFMU MP3 Archive: ' : ''
		}
		robj = re.compile('|'.join(rdict.keys()))
		return robj.sub(lambda m: rdict[m.group(0)], raw)

	"""
	on_station_clicked
	"""
	def on_station_clicked(self, btn, mouse_btn):

		self.deselect_all(self.station_btns)
		
		btn.state = 'selected'

		mpd.radio_station_start(btn.url)

		self.on_nav_change('NowPlaying')

	"""
	on_archive_clicked
	"""
	def on_archive_clicked(self, btn, mouse_btn):

		#print 'RadioScene::on_archive_clicked \t ' + btn.url

		self.deselect_all(self.archive_btns)
		btn.state = 'selected'

		url = btn.url

		try:
			f = self.url_opener.open( url )
			stream = f.read()
		except:
			return

		#print '\t stream: ' + stream

		mpd.radio_station_start(stream.strip())

		self.on_nav_change('NowPlaying')

	"""
	on_submenu_btn_clicked
	"""
	def on_submenu_btn_clicked(self, btn, mouse_btn):

		
		if btn.tag_name == 'Streams':
			self.main.rm_child(self.archives_view)
			self.main.add_child(self.streams_view)
			self.current_child = self.streams_view
			self.archives_btn.state = 'normal'
			self.streams_btn.state = 'selected'
			self.current_child_index = 0

		else:
			self.main.rm_child(self.streams_view)
			self.main.add_child(self.archives_view)
			self.current_child = self.archives_view
			self.archives_btn.state = 'selected'
			self.streams_btn.state = 'normal'
			self.current_child_index = 1

		self.update_btn_row(0)
		self.active_btn_index = 0
		self.active_btn = self.child_view_btns[self.current_child_index][0][self.active_btn_index]
		self.active_btn.state = 'focused'

	"""
	refresh_archives_click
	"""
	def refresh_archives_click(self,btn,mouse_btn):
		self.populate_archives_view()

	"""
	make_page_nav
	"""
	def make_page_nav(self):

		page_nav = PiScrollScene.make_page_nav(self)

		streams_btn = ui.Button(ui.Rect(
			0,
			0,
			165,
			self.btn_size
		),'Streams',halign=ui.CENTER,valign=ui.CENTER)

		archives_btn = ui.Button(ui.Rect(
			streams_btn.frame.right,
			0,
			165,
			self.btn_size
		),'Archives',halign=ui.CENTER,valign=ui.CENTER)

		streams_btn.tag_name = 'Streams'
		archives_btn.tag_name = 'Archive'

		streams_btn.on_clicked.connect(self.on_submenu_btn_clicked)
		archives_btn.on_clicked.connect(self.on_submenu_btn_clicked)

		self.streams_btn = streams_btn
		self.archives_btn = archives_btn
		
		page_nav.extend([streams_btn, archives_btn])
		
		return page_nav
