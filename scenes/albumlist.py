from piscene import *

"""
AlbumListScene
 lists albums by artist
"""
class AlbumListScene(PiScene):
	def __init__(self, frame=None):

		PiScene.__init__(self, frame, 'Albums')

		self.is_mpd_listener = False
		self.sidebar_index = 1
		self.active_sidebar_btn = 1

		self.make_page_nav()
		self.page_nav_active = False

		self.artists_view = self.make_scroll_view()
		self.albums_view = self.make_scroll_view()
		self.tracks_view = self.make_scroll_view()

		self.playlist_btns = [self.new_playlist]
		self.artist_btns = []#self.page_down]
		self.album_btns = []#self.page_down]
		self.track_btns = []#self.page_down]

		self.artist_idx = 0
		self.album_idx = 0
		self.track_idx = 0

		self.child_btns = [
			self.artist_btns,
			self.album_btns,
			self.track_btns
		]

		self.populate_artists_view()

		self.main.add_child(self.new_playlist)
		self.main.add_child(self.icon_playlist)
		self.main.add_child(self.page_down)
		self.main.add_child(self.icon_down)
		self.main.add_child(self.page_up)
		self.main.add_child(self.icon_up)
		self.main.add_child(self.artists_view)

		self.current_child_index = 0
		self.current_child = self.artists_view
		self.active_btn_index = 0
		self.active_btn = False
		self.sibling_active = False

	"""
	update_active_idx
	"""
	def update_active_idx(self, new_index):
		self.active_btn_index = new_index
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
		self.update_active_idx(0)
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

			if self.active_btn_index == 0:
				self.active_btn.state = 'normal'
				self.main_active = False
				self.active_sidebar_btn = 0
				self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
				return

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
			self.update_active_idx(new_index) #self.active_btn_index = new_index
			self.sibling_active = False

		#
		# down
		#
		elif key == pygame.K_DOWN:

			new_index = self.active_btn_index + 1

			if new_index >= len(self.child_btns[self.current_child_index]):
				return

			if new_index == 1 and self.current_child.scrolled:
				new_index = self.get_first_visible()

			self.active_btn.state = 'normal'
			self.active_btn = self.child_btns[self.current_child_index][new_index]
			self.active_btn.state = 'focused'
			self.update_active_idx(new_index)
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
					self.update_active_idx(0) #self.active_btn_index = 0
					self.main_active = False
					self.active_sidebar_btn = 0
					self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
				else:
					if self.active_btn_index != 0:
						#focus to page nav
						self.active_btn.state = 'normal'
						self.update_active_idx(0) #self.active_btn_index = 0
						self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
						self.active_btn.state = 'focused'
						self.sibling_active = False
					else:
						#focus to sidebar
						self.active_btn.state = 'normal'
						self.update_active_idx(0) #self.active_btn_index = 0
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
	refresh
	"""
	def refresh(self):

		print 'AlbumListScene::refresh'

		PiScene.refresh(self)

		if self.current_child == self.albums_view:

			self.main.rm_child(self.albums_view)
			self.main.add_child(self.artists_view)

			self.reset_artists()

		elif self.current_child == self.tracks_view:

			self.main.rm_child(self.tracks_view)
			self.main.add_child(self.artists_view)

			self.reset_artists()

	"""
	reset_artists
	"""
	def reset_artists(self):
		self.active_btn.state = 'normal'
		self.current_child = self.artists_view
		self.current_child_index = 0
		self.update_active_idx(0) #self.active_btn_index = 0
		self.sibling_active = False
		self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
		self.active_btn.state = 'focused'

		btn_y = self.active_btn.frame.top
		offset = self.current_child.content_view.frame.top
		btn_vy = btn_y + offset

		if btn_vy < 0:
			#print 'scroll up ' + str( self.label_height ) + ' of ' + str(self.current_child.content_view.frame.h)
			pct = ( abs(btn_vy) / float( self.current_child.content_view.frame.h ))
			self.current_child.do_scroll(pct, 'up')

	"""
	make_scroll_view
	"""
	def make_scroll_view(self):
		scroll_list = ui.ScrollList(
			ui.Rect(
				0,
				self.btn_size,
				self.main.frame.width - ui.SCROLLBAR_SIZE,
				self.main.frame.height - self.btn_size - self.btn_size - self.margins * 2 - 10
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
		
		btn_new_playlist = ui.Button(ui.Rect(
			self.margins,
			0,
			75,
			self.btn_size
		), 'New')
		
		icon_new_playlist = ui.IconButton(ui.Rect(
			75 + self.margins,
			0,
			self.btn_size,
			self.btn_size
		), 'list-alt')
		
		btn_down = ui.Button(ui.Rect(
			self.main.frame.width / 2,
			0,
			120, #self.main.frame.width / 2 - self.btn_size,
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
			0, #self.main.frame.height - self.btn_size - self.margins,
			120, #self.main.frame.width - self.btn_size,
			self.btn_size
		),'Up',halign=ui.RIGHT,valign=ui.CENTER)

		icon_up = ui.IconButton(ui.Rect(
			self.main.frame.width - self.btn_size, #self.main.frame.width - self.btn_size,
			0, #self.main.frame.height - self.btn_size - self.margins,
			self.btn_size,
			self.btn_size
		),'chevron-up')

		btn_down.tag_name = 'Down'
		btn_up.tag_name ='Up'

		btn_down.on_clicked.connect(self.on_page_nav_clicked)
		icon_down.on_clicked.connect(self.on_page_nav_clicked)
		btn_up.on_clicked.connect(self.on_page_nav_clicked)
		icon_up.on_clicked.connect(self.on_page_nav_clicked)

		btn_new_playlist.sibling = btn_down
		btn_down.sibling = btn_up

		self.new_playlist = btn_new_playlist
		self.icon_playlist = icon_new_playlist
		self.page_down = btn_down
		self.icon_down = icon_down
		self.page_up = btn_up
		self.icon_up = icon_up

	"""
	populate_artists_view
	"""
	def populate_artists_view(self):

		scroll_contents = ui.View(
			ui.Rect(0,
					0,
					self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
					self.main.frame.height-self.btn_size
			)
		)

		del self.artist_btns[:]

		scr_y = 0 #self.label_height
		#try:
		artists = mpd.mpd_client.list('artist')
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 artists = mpd.mpd_client.list('artist')

		row_count = len(artists)

		for artist in artists:

			btn_name = artist if artist != "" else "no name"

			artist_button = ui.Button( ui.Rect( 0, scr_y, self.main.frame.width - self.btn_size - self.margins * 3 - ui.SCROLLBAR_SIZE, self.label_height ), btn_name, halign=ui.LEFT, valign=ui.CENTER )
			artist_button.artist_name = artist
			artist_button.on_clicked.connect(self.on_artist_clicked)

			add_all_btn = ui.IconButton( ui.Rect(artist_button.frame.right + self.margins,scr_y,self.btn_size,self.btn_size), 'plus' )
			add_all_btn.artist_name = artist
			add_all_btn.on_clicked.connect(self.on_artist_add_clicked)

			artist_button.sibling = add_all_btn
			self.artist_btns.append(artist_button)

			scroll_contents.add_child(artist_button)
			scroll_contents.add_child(add_all_btn)

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height

		self.artists_view.update_content_view(scroll_contents)

		if self.artists_view.scrollable:
			self.artist_btns.insert(0,self.page_down)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.artist_btns.insert(0,self.new_playlist)

	"""
	populate_albums_view
	"""
	def populate_albums_view(self, artist):

		scroll_contents = ui.View(
			ui.Rect(0,
					0,
					self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
					self.main.frame.height-self.btn_size
			))

		del self.album_btns[:]

		add_all_icon = ui.IconButton(ui.Rect(0,0,50,self.label_height),'plus')
		add_all_icon.artist_name = artist
		add_all_icon.on_clicked.connect(self.on_artist_add_clicked)

		add_all_btn = ui.Button(ui.Rect(add_all_icon.frame.right,0,65,self.label_height),'All',halign=ui.LEFT,valign=ui.CENTER,wrap=ui.CLIP)
		add_all_btn.artist_name = artist
		add_all_btn.on_clicked.connect(self.on_artist_add_clicked)

		back_icon = ui.IconButton(ui.Rect(add_all_btn.frame.right+self.margins,0,50,self.label_height),'arrow-left')
		back_icon.tag_name = 'Albums'
		back_icon.on_clicked.connect(self.sidebar_btn_clicked)

		back_btn = ui.Button(ui.Rect(back_icon.frame.right,0,self.albums_view.frame.width - self.margins,self.label_height),'Back',halign=ui.LEFT,valign=ui.CENTER,wrap=ui.CLIP)
		back_btn.tag_name = 'Albums'
		back_btn.on_clicked.connect(self.on_back_btn_clicked)#self.sidebar_btn_clicked)

		scroll_contents.add_child(add_all_icon)
		scroll_contents.add_child(add_all_btn)
		scroll_contents.add_child(back_icon)
		scroll_contents.add_child(back_btn)

		add_all_btn.sibling = back_btn

		self.album_btns.append(add_all_btn)

		scr_y = self.label_height

		#try:
		artist_albums = mpd.mpd_client.list('album','artist',artist)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 artist_albums = mpd.mpd_client.list('album','artist',artist)

		row_count = len(artist_albums)

		for album in artist_albums:

			album_name = album if album != "" else "no name"

			btn = ui.Button(
				ui.Rect( 0, scr_y, self.main.frame.width - self.btn_size - self.margins * 3 - ui.SCROLLBAR_SIZE, self.label_height	),
				album_name,
				halign=ui.LEFT,
				valign=ui.CENTER,
				wrap=ui.CLIP
			)

			btn.album_name = album
			btn.on_clicked.connect(self.album_clicked)

			self.album_btns.append(btn)

			add_btn = ui.IconButton(
				ui.Rect(btn.frame.right + self.margins,scr_y,self.btn_size,self.btn_size),
				'plus',
				12
			)
			add_btn.album_name = album
			add_btn.on_clicked.connect(self.album_add_clicked)

			btn.sibling = add_btn

			scroll_contents.add_child( btn )
			scroll_contents.add_child( add_btn )

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.margins * 2 + self.btn_size

		self.albums_view.update_content_view(scroll_contents)

		if self.albums_view.scrollable:
			self.album_btns.insert(0,self.page_down)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.album_btns.insert(0,self.new_playlist)

	"""
	populate_tracks_view
	"""
	def populate_tracks_view(self, album):

		scroll_contents = ui.View(
			ui.Rect(
				0,0,
				self.main.frame.width - ui.SCROLLBAR_SIZE - self.margins,
				self.main.frame.height-self.btn_size
			)
		)

		del self.track_btns[:]

		add_all_icon = ui.IconButton(ui.Rect(0,0,50,self.label_height),'plus')
		add_all_icon.album_name = album
		add_all_icon.on_clicked.connect(self.album_add_clicked)

		add_all_btn = ui.Button(ui.Rect(add_all_icon.frame.right,0,65,self.label_height),'All',halign=ui.LEFT,valign=ui.CENTER,wrap=ui.CLIP)
		add_all_btn.album_name = album
		add_all_btn.on_clicked.connect(self.album_add_clicked)

		back_icon = ui.IconButton(ui.Rect(add_all_btn.frame.right+self.margins,0,50,self.label_height),'arrow-left')
		back_icon.tag_name = 'Tracks'
		back_icon.on_clicked.connect(self.on_back_btn_clicked)

		back_btn = ui.Button(ui.Rect(back_icon.frame.right,0,self.albums_view.frame.width - self.margins,self.label_height),'Back',halign=ui.LEFT,valign=ui.CENTER,wrap=ui.CLIP)
		back_btn.tag_name = 'Tracks'
		back_btn.on_clicked.connect(self.on_back_btn_clicked)

		scroll_contents.add_child(add_all_icon)
		scroll_contents.add_child(add_all_btn)
		scroll_contents.add_child(back_icon)
		scroll_contents.add_child(back_btn)

		add_all_btn.sibling = back_btn

		self.track_btns.append(add_all_btn)

		scr_y = self.label_height

		#try:
		album_tracks = mpd.mpd_client.list('title','album',album)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 album_tracks = mpd.mpd_client.list('title','album',album)

		row_count = len(album_tracks)

		for track in album_tracks:
			track_name = track if track != "" else "no name"
			btn = ui.Button(
				ui.Rect( 0, scr_y, self.main.frame.width - self.margins - ui.SCROLLBAR_SIZE, self.label_height ),
				track_name,
				halign=ui.LEFT,
				valign=ui.CENTER,
				wrap=ui.CLIP
			)

			btn.track_name = track
			btn.sibling = False
			btn.on_clicked.connect(self.track_clicked)

			self.track_btns.append(btn)

			scroll_contents.add_child( btn )

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.margins * 2 + self.btn_size

		self.tracks_view.update_content_view(scroll_contents)

		if self.tracks_view.scrollable:
			self.track_btns.insert(0,self.page_down)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.track_btns.insert(0,self.new_playlist)

	"""
	on_artist_clicked
	"""
	def on_artist_clicked(self, btn, mouse_btn):

		self.deselect_all(self.artist_btns)

		btn.state = 'selected'

		self.main.rm_child(self.artists_view)
		self.populate_albums_view(btn.artist_name)
		self.main.add_child(self.albums_view)
		self.current_child = self.albums_view

		self.current_child_index = 1
		self.update_active_idx(0)

		self.active_btn = self.child_btns[self.current_child_index][self.album_idx]
		self.active_btn.state = 'focused'

		self.stylize()

	"""
	on_artist_add_clicked
	"""
	def on_artist_add_clicked(self, btn, mouse_btn):

		print 'AlbumListScene::on_artist_add_clickded \t' + btn.artist_name

		self.deselect_all(self.artist_btns)

		for button in self.artist_btns[1:]:
			if button.artist_name == btn.artist_name:
				button.state = 'selected'
				break

		mpd.mpd_client.clear()
		mpd.mpd_client.findadd('artist', btn.artist_name, 'artist', btn.artist_name)

		#try:
		mpd.mpd_client.play(0)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 mpd.mpd_client.play(0)

		#mpd.playlist_add('artist', btn.artist_name, True, True)

		self.on_nav_change('NowPlaying')
		
	"""
	album_clicked
	"""
	def album_clicked(self, btn, mouse_btn):

		print 'AlbumListScene::album_clicked \t' + btn.album_name

		self.deselect_all(self.album_btns)
		btn.state = 'selected'

		self.main.rm_child(self.albums_view)
		self.populate_tracks_view(btn.album_name)
		self.main.add_child(self.tracks_view)
		self.current_child = self.tracks_view
		self.current_child_index = 2

		#self.active_btn_index = 0
		self.update_active_idx(0)

		self.active_btn = self.child_btns[self.current_child_index][self.track_idx]

		self.active_btn.state = 'focused'

		self.stylize()

	"""
	album_add_clicked
	"""
	def album_add_clicked(self, btn, mouse_btn):

		print 'AlbumListScene::album_add_clicked \t' + btn.album_name

		self.deselect_all(self.album_btns)

		btn.state = 'selected'

		#self.mpd_client.findadd('artist', self.searching_artist, tag_type, tag_name)

		mpd.mpd_client.clear()
		mpd.mpd_client.findadd('album', btn.album_name, 'album', btn.album_name)

		#try:
		mpd.mpd_client.play(0)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 mpd.mpd_client.play(0)

		#mpd.playlist_add_album(btn.album_name,True,True)

		#self.main.rm_child(self.albums_view)
		#self.main.add_child(self.artists_view)

		#ui.scene.push(scenes['NowPlaying'])

		self.on_nav_change('NowPlaying')

	"""
	track_clicked
	"""
	def track_clicked(self, btn, mouse_btn):
		self.deselect_all(self.track_btns)
		btn.state = "selected"

		mpd.mpd_client.clear()
		mpd.mpd_client.findadd('title', btn.track_name)

		#try:
		mpd.mpd_client.play(0)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 mpd.mpd_client.play(0)

		self.on_nav_change('NowPlaying')

	"""
	on_back_btn_clicked
	"""
	def on_back_btn_clicked(self, btn, mouse_btn):
		self.main.rm_child(self.current_child)
		if btn.tag_name == "Albums":
			self.main.add_child(self.artists_view)
			self.current_child = self.artists_view
			self.current_child_index = 0
			self.active_btn_index = self.artist_idx
		elif btn.tag_name == "Tracks":
			self.main.add_child(self.albums_view)
			self.current_child = self.albums_view
			self.current_child_index = 1
			self.active_btn_index = self.album_idx
			#self.stylize()

		self.active_btn = self.child_btns[self.current_child_index][self.active_btn_index]
		self.active_btn.state = 'focused'
		self.check_scroll_active()

		#self.on_main_active()

		#self.update_active_idx(0) #self.active_btn_index = 0
		#self.active_btn = self.child_btns[self.current_child_index][0]
		#self.active_btn.state = 'focused'


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
		self.new_playlist.sibling = self.page_down
		self.page_nav_active = True
		self.page_down.state = 'normal'
		self.page_up.state = 'normal'
		self.icon_down.state = 'normal'
		self.icon_up.state = 'normal'

	"""
	deactivate_page_nav
	"""
	def deactivate_page_nav(self):
		self.new_playlist.sibling = False
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
					#self.active_btn.state = 'normal'
					#self.active_btn = button

					pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
					self.current_child.do_scroll(pct, 'down')

					#self.active_btn.state = 'focused'
					#self.active_btn_index = idx
					#self.sibling_active = False

					break

				idx += 1

		else:
			for button in self.child_btns[self.current_child_index][idx:]:
				btn_y = button.frame.top + self.label_height
				offset = self.current_child.content_view.frame.top
				btn_vy = btn_y + offset

				if btn_vy < 0:
					#self.active_btn.state = 'normal'
					#self.active_btn = button

					pct = (self.current_child.frame.height - self.label_height) / float(self.current_child.content_view.frame.h)
					self.current_child.do_scroll(pct, 'up')

					#self.active_btn.state = 'focused'
					#self.active_btn_index = idx
					#self.sibling_active = False

					break

				idx += 1
	"""
	get_first_visible
	"""
	def get_first_visible(self):
		idx = 1
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
