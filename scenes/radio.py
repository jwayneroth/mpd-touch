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

		page_nav = self.make_page_nav()
		
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
		
		# idx of active scroll view
		self.current_child_index = 0
		
		# reference to active scroll view
		self.current_child = self.streams_view
		
		# idx of active button row
		self.active_btn_row = 0
		
		# idx of active button in active button row
		self.active_btn_index = 0
		
		# reference to active button
		self.active_btn = False

	"""
	update_btn_row
	 update the active btn row idx and its reference for the active scroll view
	"""
	def update_btn_row(self, new_index):

		self.active_btn_row = new_index
		
		self.active_btn_index = 0
		
		if self.current_child_index == 0:
			self.artist_idx = new_index
		elif self.current_child_index == 1:
			self.album_idx = new_index
		elif self.current_child_index == 2:
			self.track_idx = new_index

	"""
	on_main_active
	"""
	def on_main_active(self):
		self.update_btn_row(0)
		self.active_btn = self.child_view_btns[self.current_child_index][0][self.active_btn_index]
		self.active_btn.state = 'focused'

	"""
	key_down_main
	"""
	def key_down_main(self, key):

		#
		# up
		#
		if key == pygame.K_UP:

			if self.active_btn_row == 0:
				self.active_btn.state = 'normal'
				self.main_active = False
				self.active_sidebar_btn = 0
				self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
				return
				
			new_index = self.active_btn_row - 1

			self.active_btn.state = 'normal'
			
			self.active_btn = self.child_view_btns[self.current_child_index][new_index][0]

			btn_y = self.active_btn.frame.top
			offset = self.current_child.content_view.frame.top
			btn_vy = btn_y + offset

			if btn_vy < 0:
				pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
				self.current_child.do_scroll(pct, 'up')

			self.active_btn.state = 'focused'
			self.update_btn_row(new_index)

		#
		# down
		#
		elif key == pygame.K_DOWN:

			new_index = self.active_btn_row + 1

			if new_index >= len(self.child_view_btns[self.current_child_index]):
				return

			if new_index == 1 and self.current_child.scrolled:
				new_index = self.get_first_visible()

			self.active_btn.state = 'normal'
			self.active_btn = self.child_view_btns[self.current_child_index][new_index][0]
			self.active_btn.state = 'focused'
			self.update_btn_row(new_index)

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

			# if current button is not first in row, activate next button to the left
			if self.active_btn_index > 0:
				self.active_btn.state = 'normal'
				self.active_btn_index = self.active_btn_index - 1
				self.active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][self.active_btn_index]
				self.active_btn.state = 'focused'

			# current button is first in row
			else:

				# if current button is in first row, activate scene sidebar
				if self.active_btn_row == 0:
					self.active_btn.state = 'normal'
					self.update_btn_row(0)
					self.main_active = False
					self.active_sidebar_btn = 0
					self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

				# else activate view nav ( first button row )
				else:
					self.active_btn.state = 'normal'
					self.update_btn_row(0)
					self.active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][self.active_btn_index]
					self.active_btn.state = 'focused'
		#
		# right
		#
		elif key == pygame.K_RIGHT:

			# if there is another button in the row, activate it
			new_index = self.active_btn_index + 1

			if new_index < len(self.child_view_btns[self.current_child_index][self.active_btn_row]):
				self.active_btn_index = new_index
				self.active_btn.state = 'normal'
				self.active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][self.active_btn_index]
				self.active_btn.state = 'focused'

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

			self.station_btns.append([btn])

			scroll_contents.add_child(btn)

			scr_y = scr_y + self.label_height

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
	make_scroll_view
	"""
	def make_scroll_view(self):
		scroll_list = ui.ScrollList(
			ui.Rect(
				0,
				self.btn_size,
				self.main.frame.width - ui.SCROLLBAR_SIZE,
				self.main.frame.height - self.btn_size - self.margins - 10
			),
			ui.Rect(
				0,
				0,
				self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
				self.main.frame.height-self.btn_size
			)
		)
		return scroll_list

	"""
	make_page_nav
	"""
	def make_page_nav(self):
		
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
		
		btn_down = ui.Button(ui.Rect(
			self.main.frame.width / 2,
			0,
			120,
			self.btn_size
			),'Down', halign=ui.RIGHT, valign=ui.CENTER)

		icon_down = ui.IconButton(ui.Rect(
			self.main.frame.width / 2 + 120,
			0,
			self.btn_size,
			self.btn_size
		),'chevron-down')

		btn_up = ui.Button(ui.Rect(
			self.main.frame.width - 120 - self.btn_size,
			0,
			120,
			self.btn_size
		),'Up',halign=ui.RIGHT,valign=ui.CENTER)

		icon_up = ui.IconButton(ui.Rect(
			self.main.frame.width - self.btn_size,
			0,
			self.btn_size,
			self.btn_size
		),'chevron-up')
		
		streams_btn.tag_name = 'Streams'
		archives_btn.tag_name = 'Archive'
		btn_down.tag_name = 'Down'
		btn_up.tag_name ='Up'
		
		streams_btn.on_clicked.connect(self.on_submenu_btn_clicked)
		archives_btn.on_clicked.connect(self.on_submenu_btn_clicked)
		btn_down.on_clicked.connect(self.on_page_nav_clicked)
		icon_down.on_clicked.connect(self.on_page_nav_clicked)
		btn_up.on_clicked.connect(self.on_page_nav_clicked)
		icon_up.on_clicked.connect(self.on_page_nav_clicked)

		btn_down.sibling = btn_up
		
		self.streams_btn = streams_btn
		self.archives_btn = archives_btn
		self.page_down = btn_down
		self.icon_down = icon_down
		self.page_up = btn_up
		self.icon_up = icon_up

		return [streams_btn, archives_btn, btn_down, btn_up]
		
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
			for buttons in self.child_view_btns[self.current_child_index][idx:]:

				button = buttons[0]
				
				btn_y = button.frame.top + self.label_height
				offset = self.current_child.content_view.frame.top
				btn_vy = btn_y + offset

				if btn_vy > self.current_child.frame.height:
					pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
					self.current_child.do_scroll(pct, 'down')
					break

				idx += 1

		else:
			for buttons in self.child_view_btns[self.current_child_index][idx:]:
				
				button = buttons[0]

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
		idx = 1
		for buttons in self.child_view_btns[self.current_child_index][idx:]:
			button = buttons[0]
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
		for btn_row in btn_list:
			for btn in btn_row:
				btn.state = 'normal'
