import fmuglobals
from pidialogscene import *

"""
 Brightness Dialog
  scene with playback controls
"""
class BrightnessDialog(PiDialogScene):
	def __init__(self, frame=None):

		PiDialogScene.__init__(self, frame, 'Brightness')

		self.top_margin = 30
		self.left_margin = 75
		self.padding = 25
		self.btn_size = 45

		self.buttons = {}

		self.active_btn_index = 0
		self.sibling_index = 0
		self.active_btn = False

		self.brightness_slider = self.make_brightness_slider()
		self.brightness_panel = self.make_brightness_panel()

		self.btns = [
			[ self.brightness_slider ],
			[ self.buttons['minus'], self.buttons['plus'] ]
		]

		self.brightness_slider.value = int(float(self.get_brightness() / 255. * 100.))

		self.main.add_child(self.brightness_slider)
		self.main.add_child(self.brightness_panel)


	"""
	on_main_active
	"""
	def on_main_active(self):
		self.active_btn_index = 0
		self.sibling_index = 0
		self.active_btn = self.btns[self.active_btn_index][self.sibling_index]
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
				self.close_active = True
				self.close.state = 'focused'
				return

			new_index = self.active_btn_index - 1

			self.active_btn.state = 'normal'
			self.sibling_index = 0
			self.active_btn = self.btns[new_index][self.sibling_index]
			self.active_btn.state = 'focused'
			self.active_btn_index = new_index

		#
		# down
		#
		elif key == pygame.K_DOWN:
			new_index = self.active_btn_index + 1

			if new_index >= len(self.btns):
				return

			self.active_btn.state = 'normal'
			self.sibling_index = 0
			self.active_btn = self.btns[new_index][self.sibling_index]
			self.active_btn.state = 'focused'
			self.active_btn_index = new_index

		#
		# left
		#
		elif key == pygame.K_LEFT:
			if self.active_btn == self.brightness_slider:
				self.brightness_slider.value = self.brightness_slider.value - 2
			else:
				if self.sibling_index == 0:
					self.active_btn.state = 'normal'
					self.active_btn_index = 0
					self.main_active = False
					self.close_active = True
					self.close.state = 'focused'

				else :
					if len(self.btns[self.active_btn_index]) > 1:
						self.sibling_index = self.sibling_index - 1
						self.active_btn.state = 'normal'
						self.active_btn = self.btns[self.active_btn_index][self.sibling_index]
						self.active_btn.state = 'focused'

		#
		# right
		#
		elif key == pygame.K_RIGHT:
			if self.active_btn == self.brightness_slider:
				self.brightness_slider.value = self.brightness_slider.value + 2
			else:
				if self.sibling_index + 1 >= len(self.btns[self.active_btn_index]):
					return

				self.sibling_index = self.sibling_index + 1
				self.active_btn.state = 'normal'
				self.active_btn = self.btns[self.active_btn_index][self.sibling_index]
				self.active_btn.state = 'focused'

		#
		# return
		#
		elif key == pygame.K_RETURN:
			self.active_btn.on_clicked(self.active_btn, False)

	"""
	entered
	"""
	def entered(self):
		self.stylize()
		PiScene.entered(self)

	"""
	make_brightness_panel
	"""
	def make_brightness_panel(self):

		btns = ['minus', 'plus']

		panel = ui.View(ui.Rect(
			self.padding,
			self.brightness_slider.frame.bottom,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))

		btn_x = panel.frame.width / 2 - self.btn_size * 1.5 - self.padding

		for btn_class in btns:
			btn = ui.DialogButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_class )
			btn_x = btn_x + (self.btn_size + self.padding) * 2
			btn.on_clicked.connect(self.on_button_click)
			btn.tag_name = btn_class
			btn.sibling = False

			panel.add_child(btn)

			self.buttons[btn_class] = btn

		return panel

	"""
	make_brightness_slider
	"""
	def make_brightness_slider(self):
		slider = ui.SliderView( ui.Rect( self.left_margin, self.padding + 10, self.main.frame.width - self.left_margin * 2, ui.SCROLLBAR_SIZE ), ui.HORIZONTAL, 0, 100, show_thumb=False )
		slider.on_value_changed.connect(self.brightness_slider_changed)
		slider.on_state_changed.connect(self.brightness_slider_focused)
		return slider

	"""
	brightness_slider_changed
	value will be between 0 and 100
	"""
	def brightness_slider_changed(self, slider_view, value):
		v = float(value / 100. * 255.)
		logger.debug('brightness_slider_changed %s %s' % (value, int(v)))
		self.set_brightness(int(v))

	"""
	brightness_slider_focused
	"""
	def brightness_slider_focused(self):
		if self.brightness_slider.state == 'focused':
			self.brightness_slider.thumb.state = 'focused'
		else:
			self.brightness_slider.thumb.state = 'normal'

	"""
	on_button_click
	"""
	def on_button_click(self, btn, mouse_btn):

		tag_name = btn.tag_name

		if tag_name == 'minus':
			self.brightness_slider.value = self.brightness_slider.value - 10
		elif tag_name == 'plus':
			self.brightness_slider.value = self.brightness_slider.value + 10

	"""
	get_brightness
	"""
	def get_brightness(self):
		if not fmuglobals.RUN_ON_RASPBERRY_PI:
			return 100
		f = open("/sys/class/backlight/rpi_backlight/brightness","r")
		val = f.read()
		f.close()
		return int(val)

	"""
	set_brightness
	"""
	def set_brightness(self, val=100):
		if not fmuglobals.RUN_ON_RASPBERRY_PI:
			return
		if val < 20:
			val = 20
		elif val > 255:
			val = 255
		f = open("/sys/class/backlight/rpi_backlight/brightness","w")
		f.write(str(val))
		f.close()
