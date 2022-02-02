from lib.mpd_client import *
import pygameui as ui

class PiDialogScene(ui.Scene):
	def __init__(self, frame=None, name='PiDialog'):

		ui.Scene.__init__(self, frame)

		self.on_dismissed = callback.Signal()

		self.name = name
		self.margins = 15
		self.btn_size = 57 #45
		self.margins_bottom = 10
		self.is_mpd_listener = False
		self.label_height = 57 #45
		self.music_directory = '/var/lib/mpd/music/'
		self.close_active = True
		self.main_active = False

		#overlay = self.make_overlay()
		self.content = self.make_content()
		self.close = self.make_close()
		self.close.state = 'focused'
		self.main = self.make_main()
		title = self.make_title()

		#self.add_child(overlay)
		self.add_child(self.content)

		self.content.add_child(title)
		self.content.add_child(self.close)
		self.content.add_child(self.main)

	"""
	make_overlay
	"""
	def make_overlay(self):
		view = DialogOverlay(ui.Rect(0,0,self.frame.width,self.frame.height))
		return view

	"""
	make_content
	"""
	def make_content(self):
		view = DialogContent(ui.Rect(75,60,self.frame.width-150,self.frame.height-120))
		return view

	"""
	make_title
	"""
	def make_title(self):
		label = ui.DialogLabel(
			ui.Rect(0, 0, self.content.frame.width, self.label_height),
			self.name,
			halign=ui.CENTER
		)
		return label

	"""
	make_close
	"""
	def make_close(self):
		close = ui.DialogButton(
			ui.Rect(self.content.frame.width - self.btn_size,0,self.btn_size,self.btn_size,halign=ui.CENTER),
			'remove'
		)
		close.on_clicked.connect(self.dismiss)
		close.tag_name = 'close'
		return close

	"""
	make_main
	"""
	def make_main(self):
		main = ui.View(
			ui.Rect(
				0,
				self.label_height,
				self.content.frame.width,
				self.content.frame.height - self.label_height
			)
		)
		return main

	"""
	key_down
	"""
	def key_down(self, key, code):
		logger.debug('pidialogscene key_down key: %s code %s' % (str(key), str(code)))

		ui.Scene.key_down(self,key,code)

		if self.main_active == True:
			self.key_down_main(key)
		else:
			self.key_down_header(key)

	"""
	key_down_header
	"""
	def key_down_header(self, key):
		if key == pygame.K_UP:
			pass

		elif key == pygame.K_DOWN:
			self.close_active = False
			self.close.state = 'normal'
			self.main_active = True
			self.on_main_active()

		elif key == pygame.K_LEFT:
			pass

		elif key == pygame.K_RIGHT:
			self.close_active = False
			self.close.state = 'normal'
			self.main_active = True
			self.on_main_active()

		elif key == pygame.K_RETURN:
			self.dismiss()

	"""
	key_down_main
	"""
	def key_down_main(self, key):
		if key == pygame.K_UP:
			self.main_active = False
			self.close_active = True
			self.close.state = 'focused'

	"""
	on_main_active
	"""
	def on_main_active(self):
		pass

	"""
	refresh
	"""
	def refresh(self):
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
		if self.is_mpd_listener == True:
			if mpd.status_get():
				self.on_mpd_update()

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		pass

	"""
	dismiss
	"""
	def dismiss(self, btn=None, mouse_btn=None):
		self.rm()
		ui.focus.set(None)
		self.on_dismissed()

class DialogContent(ui.View):
	def __init__(self, frame):
		ui.View.__init__(self,frame)

class DialogOverlay(ui.View):
	def __init__(self, frame):
		ui.View.__init__(self,frame)
