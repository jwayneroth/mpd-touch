from lib.mpd_client import *
import pygameui as ui

"""
PiScene
 pygameui.Scene subclass
 parent class for all fmulcd scenes
"""
class PiScene(ui.Scene):
	def __init__(self, frame, name):

		ui.Scene.__init__(self, frame)

		self.name = name
		self.margins = 15
		self.nav_btn_size = 50
		self.btn_size = 57 #45
		self.margins_bottom = 10
		self.has_nav = False
		self.is_mpd_listener = False
		self.label_height = 57 #45
		self.controls_on = False
		self.modal_left_right_margin = 0
		self.modal_top_bottom_margin = 0
		self.music_directory = '/var/lib/mpd/music/'
		self.main_active = False
		self.sidebar_index = 0
		self.active_sidebar_btn = 0
		self.dialog = None
		self.is_screensaver = False

		self.sidebar = self.make_sidebar()
		self.main = self.make_main()
		#self.controls = self.make_controls()

		self.add_child(self.sidebar)
		self.add_child(self.main)

		self.on_nav_change = callback.Signal()
		self.open_dialog = callback.Signal()

	"""
	make_sidebar
	"""
	def make_sidebar(self):

		self.sidebar_btns = []

		sidebar = ui.View(
			ui.Rect(
				0,
				0,
				self.nav_btn_size + self.margins * 2,
				self.frame.height
			)
		)

		btns = [
			('NowPlaying','cd'),
			('Albums','list'),
			('Radio','music'),
			('Settings','cog'),
			('Controls','volume-down')
		]

		btn_x = 15

		btn_y = 20

		for btn_data in btns:
			btn = ui.NavIconButton(
				ui.Rect(
					btn_x,
					btn_y,
					self.nav_btn_size,
					self.nav_btn_size,
					halign=ui.CENTER
				),
				btn_data[1]
			)
			btn_y = btn_y + round(self.frame.height / 5 )
			btn.on_clicked.connect(self.sidebar_btn_clicked)
			btn.tag_name = btn_data[0]

			if btn_data[0] == self.name:
				btn.state = 'selected'
			sidebar.add_child(btn)
			self.sidebar_btns.append(btn)

		return sidebar

	"""
	make_main
	"""
	def make_main(self):

		main = PiMain( #ui.View(
			ui.Rect(
				self.sidebar.frame.width, #0,
				0, #self.sidebar.frame.bottom,
				self.frame.width - self.sidebar.frame.width, #self.frame.width,
				self.frame.height #self.frame.height - self.sidebar.frame.height # - self.margins - self.margins
			)
		)

		return main

	"""
	make_controls
	"""
	def make_controls(self):

		controls = PiControls(ui.Rect(
			self.modal_left_right_margin,
			self.modal_top_bottom_margin,
			self.frame.width - self.modal_left_right_margin * 2,
			self.frame.height - self.modal_top_bottom_margin * 2
		))

		controls.on_dismissed.connect(self.onControlsDismissed)

		return controls

	"""
	onControlsDismissed
	"""
	def onControlsDismissed(self):
		self.controls_on = False

	"""
	sidebar_btn_clicked
	"""
	def sidebar_btn_clicked(self, btn, mouse_btn):
		#logger.debug('PiScene::sidebar_btn_clicked %s' % btn.tag_name)

		if btn.tag_name == 'Controls':
			self.open_dialog(btn.tag_name)
		else:
			btn.state = 'normal'
			self.main_active = True
			self.on_main_active()
			self.on_nav_change(btn.tag_name)

	"""
	key_down
	"""
	def key_down(self, key, code):
		#print 'key_down key: ' + str(key) + ' code: ' + str(code)

		ui.Scene.key_down(self,key,code)

		if self.dialog is not None:
			self.dialog.key_down(key, code)
		else:
			if self.main_active == True:
				self.key_down_main(key)
			else:
				self.key_down_sidebar(key)

	"""
	key_down_main
	"""
	def key_down_main(self, key):
		if key == pygame.K_LEFT:
			self.main_active = False
			self.active_sidebar_btn = 0
			self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

	"""
	key_down_sidebar
	"""
	def key_down_sidebar(self, key):
		if key == pygame.K_UP:
			if self.active_sidebar_btn > 0:
				if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
					self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
				else:
					self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
				self.active_sidebar_btn = self.active_sidebar_btn - 1
			else:
				if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
					self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
				else:
					self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
				self.active_sidebar_btn = len(self.sidebar_btns) - 1
			self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

		elif key == pygame.K_DOWN:
			if self.active_sidebar_btn < (len(self.sidebar_btns) - 1):
				if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
					self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
				else:
					self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
				self.active_sidebar_btn = self.active_sidebar_btn + 1
			else:
				if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
					self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
				else:
					self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
				self.active_sidebar_btn = 0
			self.sidebar_btns[self.active_sidebar_btn].state = 'focused'


		elif key == pygame.K_LEFT:
			pass

		elif key == pygame.K_RIGHT:
			self.main_active = True
			if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
				self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
			else:
				self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
			self.on_main_active()

		elif key == pygame.K_RETURN:
			self.sidebar_btn_clicked(self.sidebar_btns[self.active_sidebar_btn], False)

	"""
	on_main_active
	"""
	def on_main_active(self):
		pass

	"""
	refresh
	"""
	def refresh(self):
		if self.active_sidebar_btn != self.sidebar_index:
			self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
			self.active_sidebar_btn = self.sidebar_index
			self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
		self.main_active = True
		self.on_main_active()

	"""
	entered
	"""
	def entered(self):
		logger.debug(self.name + ' entered.')
		ui.Scene.entered(self)

	"""
	update
	"""
	def update(self):
		#ui.Scene.update(self, dt)
		dialog_mpd_listener = self.dialog != None and self.dialog.is_mpd_listener == True
		#logger.debug("%s::update dialog_mpd_listener: %s", self.name, dialog_mpd_listener)
		if self.is_mpd_listener == True:
			if mpd.status_get():
				self.on_mpd_update()
				if dialog_mpd_listener :
					self.dialog.on_mpd_update()
		elif dialog_mpd_listener :
			if mpd.status_get():
				self.dialog.on_mpd_update()

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		pass

class PiMain(ui.View):
	def __init__(self, frame=None):
		ui.View.__init__(self, frame)

	"""
	draw
	 if we have been updated or forced, force children to redraw and redraw ourselves
	 else only redraw if any children have been redrawn themselves
	"""
	def draw(self, force=False):
		if self.hidden:
			return False

		if self.updated or force:
			self.updated = False

			for child in self.children:
				if not child.hidden:
					child.draw(True)
					self.surface.blit(child.surface, child.frame.topleft)
					if child.border_color and child.border_widths is not None:
						if (type(child.border_widths) is int and child.border_widths > 0):
							pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)
			return True

		else:
			drawn = False

			for child in self.children:
				if not child.hidden:
					if child.draw():
						#if child.__class__.__name__ != 'View':
						#print 'Pi Main redrawing ' + child.__class__.__name__
						drawn = True
						self.surface.blit(child.surface, child.frame.topleft)
						if child.border_color and child.border_widths is not None:
							if (type(child.border_widths) is int and child.border_widths > 0):
								pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)

			return drawn

"""
CoverView
 extend ui.ImageView
"""
class CoverView(ui.ImageView):
	def __init__(self, frame, img, parent_frame, content_mode=1):

		#ui.ImageView.__init__(self, frame, img)

		self.image_directory = 'images/'
		if os.path.dirname(__file__) != '':
			self.image_directory = os.path.dirname(__file__) + '/../' + self.image_directory

		#self.default_cover_image_directory = self.image_directory + 'default_covers'

		if img is None:
			logger.debug('CoverView img is None, find default ' + self.image_directory + 'default_covers/1.png')
			img = ui.get_image( self.image_directory + 'default_covers/1.png')
			print(img)
		assert img is not None

		if frame is None:
			frame = pygame.Rect((0, 0), img.get_size())
		elif frame.w == 0 and frame.h == 0:
			frame.size = img.get_size()

		self._max_frame = frame

		self._enabled = False
		self.content_mode = content_mode
		self.image = img
		self.parent_frame = parent_frame

		#assert self.padding[0] == 0 and self.padding[1] == 0

		if self.content_mode == 0:
			self._image = ui.resource.scale_image(self.image, frame.size)
		elif self.content_mode == 1:
			self._image = ui.resource.scale_to_fit(self.image, frame.size)
		else:
			assert False, "Unknown content_mode"

		if self._image.get_width() < self.parent_frame.width:
			frame.left = (self.parent_frame.width - self._image.get_width()) / 2

		frame.size = self._image.get_size()

		ui.View.__init__(self, frame)

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, new_image):
		try:
			self._image = ui.resource.scale_to_fit(new_image, self._max_frame.size)
		except:
			self._image = new_image

		try:
			pf = self.parent_frame

			try:
				f = self.frame
				if self._image.get_width() < pf.width:
					f.left = (pf.width - self._image.get_width() ) / 2
			except:
				pass
		except:
			pass

	"""
	layout
	 override ui.ImageView
	"""
	def layout(self):
		ui.View.layout(self)
