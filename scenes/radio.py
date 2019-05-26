import feedparser
import re
import urllib

from piscene import *

"""
RadioScene
 radio options, playback controls
"""
class RadioScene(PiScene):
	def __init__(self, frame):

		PiScene.__init__(self, frame, 'Radio')

		self.sidebar_index = 2
		self.active_sidebar_btn = 2

		self.make_page_nav()
		self.page_nav_active = False

		self.stations = [
			{'title':'WFMU','url':'http://stream0.wfmu.org/freeform-128k'},
			{'title':'GtDR','url':'http://stream0.wfmu.org:80/drummer'},
			{'title':'Ichiban','url':'http://stream0.wfmu.org/ichiban'},
			{'title':'Ubu','url':'http://stream0.wfmu.org/ubu'},
			{'title':'Sheena','url':'http://stream0.wfmu.org/sheena'},
			{'title':'FMU32','url':'http://stream0.wfmu.org/freeform-32k.mp3'},
			{'title':'wkcr','url':'http://wkcr.streamguys1.com:80/live'},
			{'title':'wnyc','url':'http://fm939.wnyc.org/wnycfm'},
			{'title':'bbc','url':'http://am820.wnyc.org/wnycam'},
			{'title':'wqxr','url':'http://stream.wqxr.org/wqxr'},
			{'title':'q2','url':'http://q2stream.wqxr.org/q2'}
		]

		self.url_opener = urllib.FancyURLopener({})

		self.streams_btn = ui.Button(ui.Rect(0,0,165,self.btn_size),'Streams',halign=ui.CENTER,valign=ui.CENTER)
		self.archives_btn = ui.Button(ui.Rect(self.streams_btn.frame.right,0,165,self.btn_size),'Archives',halign=ui.CENTER,valign=ui.CENTER)

		self.streams_btn.tag_name = 'Streams'
		self.archives_btn.tag_name = 'Archive'

		self.streams_btn.on_clicked.connect(self.on_submenu_btn_clicked)
		self.archives_btn.on_clicked.connect(self.on_submenu_btn_clicked)

		self.streams_btn.sibling = self.archives_btn

		self.streams_view = self.make_scroll_view()
		self.archives_view = self.make_scroll_view()

		self.station_btns = []
		self.archive_btns = []
		self.child_btns = [ self.station_btns, self.archive_btns ]

		self.populate_streams_view()
		self.populate_archives_view()

		self.main.add_child(self.streams_btn)
		self.main.add_child(self.archives_btn)
		self.main.add_child(self.page_down)
		self.main.add_child(self.icon_down)
		self.main.add_child(self.page_up)
		self.main.add_child(self.icon_up)
		self.main.add_child(self.streams_view)

		self.current_child_index = 0
		self.current_child = self.streams_view
		self.active_btn_index = 0
		self.active_btn = False
		self.sibling_active = False

	"""
	on_main_active
	"""
	def on_main_active(self):
		self.active_btn_index = 0
		self.active_btn = self.child_btns[self.current_child_index][0]
		self.active_btn.state = 'focused'


	"""
	key_down_main
	"""
	def key_down_main(self, key):

		#
		# up
		#
		if key == pygame.K_UP:

			new_index = self.active_btn_index - 1

			self.active_btn.state = 'normal'
			self.active_btn = self.child_btns[self.current_child_index][new_index]

			btn_y = self.active_btn.frame.top
			offset = self.current_child.content_view.frame.top
			btn_vy = btn_y + offset

			if btn_vy < 0:
				pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
				self.current_child.do_scroll(pct, 'up')

			self.active_btn.state = 'focused'
			self.active_btn_index = new_index
			self.sibling_active = False

		#
		# down
		#
		elif key == pygame.K_DOWN:

			new_index = self.active_btn_index + 1

			if new_index >= len(self.child_btns[self.current_child_index]):
				return

			if new_index == 2 and self.current_child.scrolled:
				new_index = self.get_first_visible()

			self.active_btn.state = 'normal'
			self.active_btn = self.child_btns[self.current_child_index][new_index]
			self.active_btn.state = 'focused'
			self.active_btn_index = new_index #self.update_active_idx(new_index)
			self.sibling_active = False

			btn_y = self.active_btn.frame.top + self.label_height
			offset = self.current_child.content_view.frame.top
			btn_vy = btn_y + offset

			if btn_vy > self.current_child.frame.height:
				pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
				self.current_child.do_scroll(pct, 'down')

		#
		# left
		#
		elif key == pygame.K_LEFT:
			if self.active_btn_index == 0:
				self.active_btn.state = 'normal'
				self.main_active = False
				self.active_sidebar_btn = 0
				self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
				return
			if self.sibling_active == True:
				#focus to sibling
				self.active_btn.state = 'normal'
				self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
				self.active_btn.state = 'focused'
				self.sibling_active = False

			else:
				if self.page_nav_active == False:
					#focus to sidebar
					self.active_btn.state = 'normal'
					self.active_btn_index = 0
					self.main_active = False
					self.active_sidebar_btn = 0
					self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
				else:
					if self.active_btn_index > 1:
						#focus to page nav
						self.active_btn.state = 'normal'
						self.active_btn_index = 1
						self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
						self.active_btn.state = 'focused'
						self.sibling_active = False
					elif self.active_btn_index == 1:
						#focus to streams / archives
						self.active_btn.state = 'normal'
						self.active_btn_index = 0
						self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
						self.active_btn.state = 'focused'
						self.sibling_active = False
					elif self.active_btn_index == 0:
						#focus to sidebar
						self.active_btn.state = 'normal'
						self.active_btn_index = 0
						self.main_active = False
						self.active_sidebar_btn = 0
						self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
		#
		# right
		#
		elif key == pygame.K_RIGHT:
			current_btn = self.child_btns[self.current_child_index][self.active_btn_index]
			if self.sibling_active == False and current_btn.sibling != False :
				current_btn.state = 'normal'
				current_btn.sibling.state = 'focused'

				self.active_btn = current_btn.sibling
				self.sibling_active = True


		#
		# return
		#
		elif key == pygame.K_RETURN:

			self.active_btn.on_clicked(self.active_btn, False)

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

		scr_y = 0
		row_count = len(self.stations)

		for station in self.stations:

			btn = ui.Button( ui.Rect( 0, scr_y, self.main.frame.width - ui.SCROLLBAR_SIZE, self.label_height ), station['title'], halign=ui.LEFT, valign=ui.CENTER )

			btn.url = station['url']
			btn.on_clicked.connect(self.on_station_clicked)
			btn.sibling = False

			self.station_btns.append(btn)

			#add_btn = ui.IconButton( ui.Rect(btn.frame.right + self.margins,scr_y,self.btn_size,self.btn_size), 'plus', 12 )
			#add_btn.url = station['url']
			#add_btn.on_clicked.connect(self.on_station_clicked)

			scroll_contents.add_child(btn)
			#scroll_contents.add_child(add_btn)

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height

		self.streams_view.update_content_view(scroll_contents)

		if self.streams_view.scrollable:
			self.station_btns.insert(0,self.page_down)
			self.station_btns.insert(0,self.streams_btn)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()

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

		self.archive_btns.append(refresh_btn)

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

			self.archive_btns.append(btn)

			scroll_contents.add_child(btn)

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.btn_size + self.margins

		self.archives_view.update_content_view(scroll_contents)

		if self.archives_view.scrollable:
			self.archive_btns.insert(0,self.page_down)
			self.archive_btns.insert(0,self.streams_btn)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()

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

		self.active_btn_index = 0
		self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
		self.active_btn.state = 'focused'

	"""
	refresh_archives_click
	"""
	def refresh_archives_click(self,btn,mouse_btn):
		self.populate_archives_view()

	"""
	make_scroll_view
	"""
	def make_scroll_view(self):
		scroll_list = ui.ScrollList(
			ui.Rect(
				0,
				self.btn_size * 2,
				self.main.frame.width - ui.SCROLLBAR_SIZE,
				self.main.frame.height - self.btn_size - self.btn_size - self.btn_size - self.margins * 2 - 10
			),
			ui.Rect(
				0,
				0,
				self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
				self.main.frame.height-self.btn_size-self.btn_size
			)
		)
		return scroll_list

	"""
	make_page_nav
	"""
	def make_page_nav(self):
		btn_down = ui.Button(
			ui.Rect(0, self.btn_size, self.main.frame.width - self.btn_size, self.btn_size),
			'Page Down',
			halign=ui.RIGHT,
			valign=ui.CENTER
		)

		icon_down = ui.IconButton(
			ui.Rect(self.main.frame.width - self.btn_size, self.btn_size, self.btn_size, self.btn_size),
			'chevron-down'
		)

		btn_up = ui.Button(
			ui.Rect(0, self.main.frame.height - self.btn_size - self.margins, self.main.frame.width - self.btn_size, self.btn_size),
			'Page Up',
			halign=ui.RIGHT,
			valign=ui.CENTER
		)

		icon_up = ui.IconButton(
			ui.Rect(self.main.frame.width - self.btn_size, self.main.frame.height - self.btn_size- self.margins, self.btn_size, self.btn_size),
			'chevron-up'
		)

		btn_down.tag_name = 'Down'
		btn_up.tag_name ='Up'

		btn_down.on_clicked.connect(self.on_page_nav_clicked)
		icon_down.on_clicked.connect(self.on_page_nav_clicked)
		btn_up.on_clicked.connect(self.on_page_nav_clicked)
		icon_up.on_clicked.connect(self.on_page_nav_clicked)

		btn_down.sibling = btn_up

		self.page_down = btn_down
		self.icon_down = icon_down
		self.page_up = btn_up
		self.icon_up = icon_up

	"""
	check_scroll_active
	"""
	def check_scroll_active(self):
		if self.current_child.scrollable:
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()

	"""
	activate_page_nav
	"""
	def activate_page_nav(self):
		self.page_nav_active = True
		self.page_down.state = 'normal'
		self.page_up.state = 'normal'
		self.icon_down.state = 'normal'
		self.icon_up.state = 'normal'

	"""
	deactivate_page_nav
	"""
	def deactivate_page_nav(self):
		self.page_nav_active = False
		self.page_down.state = 'disabled'
		self.page_up.state = 'disabled'
		self.icon_down.state = 'disabled'
		self.icon_up.state = 'disabled'

	"""
	on_page_nav_clicked
	"""
	def on_page_nav_clicked(self, btn, mouse_btn):
		idx = 1
		if btn == self.page_down or btn == self.icon_down:
			for button in self.child_btns[self.current_child_index][idx:]:
				btn_y = button.frame.top + self.label_height
				offset = self.current_child.content_view.frame.top
				btn_vy = btn_y + offset

				if btn_vy > self.current_child.frame.height:
					pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
					self.current_child.do_scroll(pct, 'down')
					break

				idx += 1

		else:
			for button in self.child_btns[self.current_child_index][idx:]:
				btn_y = button.frame.top + self.label_height
				offset = self.current_child.content_view.frame.top
				btn_vy = btn_y + offset

				if btn_vy < 0:
					pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
					self.current_child.do_scroll(pct, 'up')
					break

				idx += 1

	"""
	get_first_visible
	"""
	def get_first_visible(self):
		idx = 2
		for button in self.child_btns[self.current_child_index][idx:]:
			btn_y = button.frame.top + self.label_height / 2
			offset = self.current_child.content_view.frame.top
			btn_vy = btn_y + offset
			if btn_vy > 0:
				return idx
			idx += 1

	"""
	deselect_all
	"""
	def deselect_all(self, btn_list):
		for btn in btn_list:
			btn.state = 'normal'
