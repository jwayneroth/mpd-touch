from .piscrollscene import *

"""
AlbumListScene
 lists albums by artist
"""
class AlbumListScene(PiScrollScene):
	def __init__(self, frame, name):

		PiScrollScene.__init__(self, frame, name)

		self.is_mpd_listener = False
		self.sidebar_index = 1
		self.active_sidebar_btn = 1

		page_nav = self.make_page_nav()

		self.new_playlist_set = False
		
		self.artists_view = self.make_scroll_view()
		self.albums_view = self.make_scroll_view()
		self.tracks_view = self.make_scroll_view()

		self.artist_idx = 0
		self.album_idx = 0
		self.track_idx = 0
		
		self.artist_btns = [page_nav]
		self.album_btns = [page_nav]
		self.track_btns = [page_nav]

		self.child_view_btns = [
			self.artist_btns,
			self.album_btns,
			self.track_btns
		]

		self.populate_artists_view()

		self.main.add_child(self.page_down)
		self.main.add_child(self.icon_down)
		self.main.add_child(self.page_up)
		self.main.add_child(self.icon_up)
		self.main.add_child(self.new_playlist)
		self.main.add_child(self.icon_playlist)
		self.main.add_child(self.artists_view)

		self.current_child = self.artists_view
		
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
	refresh
	"""
	def refresh(self):

		print('AlbumListScene::refresh')

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
		self.update_btn_row(0)
		self.active_btn_index = 0
		self.active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][self.active_btn_index]
		self.active_btn.state = 'focused'

		btn_y = self.active_btn.frame.top
		offset = self.current_child.content_view.frame.top
		btn_vy = btn_y + offset

		if btn_vy < 0:
			#print 'scroll up ' + str( self.label_height ) + ' of ' + str(self.current_child.content_view.frame.h)
			pct = ( abs(btn_vy) / float( self.current_child.content_view.frame.h ))
			self.current_child.do_scroll(pct, 'up')

	"""
	make_page_nav
	"""
	def make_page_nav(self):
		
		page_nav = PiScrollScene.make_page_nav(self)
		
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
		
		btn_new_playlist.on_clicked.connect(self.on_new_playlist_clicked)
		icon_new_playlist.on_clicked.connect(self.on_new_playlist_clicked)

		self.new_playlist = btn_new_playlist
		self.icon_playlist = icon_new_playlist
		
		page_nav.insert(0, btn_new_playlist)
		
		return page_nav

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

		scr_y = 0

		artists = mpd.mpd_client.list('artist')

		row_count = len(artists)

		logger.debug('artists {}'.format(artists))

		for artist in artists:

			logger.debug('artist name {}'.format(artist))

			btn_name = "no name"
			if 'artist' in artist and artist['artist'] != '':
				btn_name = artist['artist']

			logger.debug('btn_name {}'.format(btn_name))

			artist_button = ui.Button( ui.Rect( 0, scr_y, self.main.frame.width - self.btn_size - self.margins * 3 - ui.SCROLLBAR_SIZE, self.label_height ), btn_name, halign=ui.LEFT, valign=ui.CENTER )
			artist_button.artist_name = artist['artist']
			artist_button.on_clicked.connect(self.on_artist_clicked)

			add_all_btn = ui.IconButton( ui.Rect(artist_button.frame.right + self.margins,scr_y,self.btn_size,self.btn_size), 'plus' )
			add_all_btn.artist_name = artist['artist']
			add_all_btn.on_clicked.connect(self.on_artist_add_clicked)

			self.artist_btns.append([artist_button, add_all_btn])

			scroll_contents.add_child(artist_button)
			scroll_contents.add_child(add_all_btn)

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height

		self.artists_view.update_content_view(scroll_contents)

		if self.artists_view.scrollable:
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.artist_btns.insert(0, [self.new_playlist, self.page_down, self.page_up])

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
		back_btn.on_clicked.connect(self.on_back_btn_clicked)

		scroll_contents.add_child(add_all_icon)
		scroll_contents.add_child(add_all_btn)
		scroll_contents.add_child(back_icon)
		scroll_contents.add_child(back_btn)

		self.album_btns.append([add_all_btn, back_btn])

		scr_y = self.label_height

		artist_albums = mpd.mpd_client.list('album','artist', artist)

		logger.debug('%d albums' % len(artist_albums))
		logger.debug('for artist %s' % artist)
		logger.debug('artist_albums {}'.format(artist_albums))

		row_count = len(artist_albums)

		for album in artist_albums:

			album_name = "no name"
			if 'album' in album and album['album'] != '':
				album_name = album['album']

			btn = ui.Button(
				ui.Rect( 0, scr_y, self.main.frame.width - self.btn_size - self.margins * 3 - ui.SCROLLBAR_SIZE, self.label_height	),
				album_name,
				halign=ui.LEFT,
				valign=ui.CENTER,
				wrap=ui.CLIP
			)

			btn.album_name = album_name
			btn.on_clicked.connect(self.album_clicked)

			add_btn = ui.IconButton(
				ui.Rect(btn.frame.right + self.margins,scr_y,self.btn_size,self.btn_size),
				'plus',
				12
			)
			add_btn.album_name = album_name
			add_btn.on_clicked.connect(self.album_add_clicked)

			scroll_contents.add_child( btn )
			scroll_contents.add_child( add_btn )

			self.album_btns.append([btn, add_btn])
			
			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.margins * 2 + self.btn_size

		self.albums_view.update_content_view(scroll_contents)

		if self.albums_view.scrollable:
			#self.album_btns.insert(0,self.page_down)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.album_btns.insert(0, [self.new_playlist, self.page_down, self.page_up])

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

		self.track_btns.append([add_all_btn, back_btn])

		scr_y = self.label_height

		#try:
		album_tracks = mpd.mpd_client.list('title','album',album)
		#except mpd.mpd_client.ConnectionError:
		#	 mpd.mpd_client.connect('localhost',6600)
		#	 album_tracks = mpd.mpd_client.list('title','album',album)

		row_count = len(album_tracks)

		for track in album_tracks:
			logger.debug('track {}'.format(track))
			track_name = "no name"
			if 'title' in track and track['title'] != '':
				track_name = track['title']
			btn = ui.Button(
				ui.Rect( 0, scr_y, self.main.frame.width - self.margins - ui.SCROLLBAR_SIZE, self.label_height ),
				track_name,
				halign=ui.LEFT,
				valign=ui.CENTER,
				wrap=ui.CLIP
			)

			btn.track_name = track_name
			btn.on_clicked.connect(self.track_clicked)

			self.track_btns.append([btn])

			scroll_contents.add_child( btn )

			scr_y = scr_y + self.label_height

		scroll_contents.frame.height = row_count * self.label_height + self.margins * 2 + self.btn_size

		self.tracks_view.update_content_view(scroll_contents)

		if self.tracks_view.scrollable:
			#self.track_btns.insert(0,self.page_down)
			self.activate_page_nav()
		else:
			self.deactivate_page_nav()
			
		self.track_btns.insert(0, [self.new_playlist, self.page_down, self.page_up])

	"""
	on_artist_clicked
	"""
	def on_artist_clicked(self, btn, mouse_btn):

		self.deselect_all(self.artist_btns)

		btn.state = 'selected'

		self.main.rm_child(self.artists_view)
		logger.debug('artist %s clicked' % btn.artist_name)
		self.populate_albums_view(btn.artist_name)
		self.main.add_child(self.albums_view)
		self.current_child = self.albums_view

		self.current_child_index = 1
		self.update_btn_row(0)

		self.active_btn_index = 0
		self.active_btn = self.child_view_btns[self.current_child_index][self.album_idx][self.active_btn_index]
		self.active_btn.state = 'focused'

		self.stylize()

	"""
	on_artist_add_clicked
	"""
	def on_artist_add_clicked(self, btn, mouse_btn):

		print('AlbumListScene::on_artist_add_clickded \t%s' % btn.artist_name)

		self.deselect_all(self.artist_btns)

		for buttons in self.artist_btns[1:]:
			for button in buttons:
				if button.artist_name == btn.artist_name:
					button.state = 'selected'
					break

		#mpd.mpd_client.clear()
		#mpd.mpd_client.findadd('artist', btn.artist_name, 'artist', btn.artist_name)
		#mpd.mpd_client.play(0)
		
		autoplay = False
		if self.new_playlist_set:
			self.new_playlist_set = False
			autoplay = True
		
		mpd.playlist_add('artist', btn.artist_name, autoplay, False)
		
		#self.on_nav_change('NowPlaying')
		
	"""
	album_clicked
	"""
	def album_clicked(self, btn, mouse_btn):

		print('AlbumListScene::album_clicked \t%s' % btn.album_name)

		self.deselect_all(self.album_btns)
		btn.state = 'selected'

		self.main.rm_child(self.albums_view)
		self.populate_tracks_view(btn.album_name)
		self.main.add_child(self.tracks_view)
		self.current_child = self.tracks_view
		self.current_child_index = 2

		#self.active_btn_row = 0
		self.update_btn_row(0)

		self.active_btn_index = 0
		self.active_btn = self.child_view_btns[self.current_child_index][self.track_idx][self.active_btn_index]

		self.active_btn.state = 'focused'

		self.stylize()

	"""
	album_add_clicked
	"""
	def album_add_clicked(self, btn, mouse_btn):

		logger.debug('AlbumListScene::album_add_clicked \t%s' % btn.album_name)

		self.deselect_all(self.album_btns)

		btn.state = 'selected'

		#mpd.mpd_client.clear()
		#mpd.mpd_client.findadd('album', btn.album_name, 'album', btn.album_name)
		#mpd.mpd_client.play(0)

		autoplay = False
		if self.new_playlist_set:
			self.new_playlist_set = False
			autoplay = True
		
		mpd.playlist_add('album', btn.album_name, autoplay, False)
		
		#self.on_nav_change('NowPlaying')

	"""
	track_clicked
	"""
	def track_clicked(self, btn, mouse_btn):
		self.deselect_all(self.track_btns)
		btn.state = "selected"

		#mpd.mpd_client.clear()
		#mpd.mpd_client.findadd('title', btn.track_name)
		#mpd.mpd_client.play(0)
		
		autoplay = False
		if self.new_playlist_set:
			self.new_playlist_set = False
			autoplay = True
		
		mpd.playlist_add('title', btn.track_name, autoplay, False)
		
		#self.on_nav_change('NowPlaying')

	"""
	on_back_btn_clicked
	"""
	def on_back_btn_clicked(self, btn, mouse_btn):
		self.main.rm_child(self.current_child)
		if btn.tag_name == "Albums":
			self.main.add_child(self.artists_view)
			self.current_child = self.artists_view
			self.current_child_index = 0
			self.active_btn_row = self.artist_idx
		elif btn.tag_name == "Tracks":
			self.main.add_child(self.albums_view)
			self.current_child = self.albums_view
			self.current_child_index = 1
			self.active_btn_row = self.album_idx
			#self.stylize()

		self.active_btn_index = 0
		self.active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][self.active_btn_index]
		self.active_btn.state = 'focused'
		self.check_scroll_active()

		#self.on_main_active()

		#self.update_btn_row(0) #self.active_btn_row = 0
		#self.active_btn = self.child_view_btns[self.current_child_index][0]
		#self.active_btn.state = 'focused'

	"""
	on_new_playlist_clicked
	
	 empty current playlist
	 set a flag so that when first item is added to empty playlist, we know to play it
	"""
	def on_new_playlist_clicked(self, btn, mouse_btn):
		mpd.set_playback('stop')
		mpd.clear_current_playlist()
		self.new_playlist_set = True
