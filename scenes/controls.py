import fmuglobals
from .piscene import *

"""
 ControlsScene
  scene with playback controls
"""
class ControlsScene(PiScene):
	def __init__(self, frame=None):

		PiScene.__init__(self, frame, 'Controls')

		self.is_mpd_listener = True
		self.sidebar_index = 4
		self.active_sidebar_btn = 4

		self.top_margin = 30
		self.left_margin = 75
		self.padding = 25
		self.btn_size = 45
		self.play_modes = [["normal","unchecked"], ["single_repeat","expand"], ["repeat_all","repeat"], ["shuffle","random"]]
		self.current_play_mode = 0;

		self.buttons = {}

		self.active_btn_index = 0
		self.sibling_index = 0
		self.active_btn = False

		self.top_panel = self.make_top_panel()
		self.volume_slider = self.make_volume_slider()
		self.volume_panel = self.make_volume_panel()
		self.brightness_slider = self.make_brightness_slider()
		self.brightness_panel = self.make_brightness_panel()

		self.btns = [
			[ self.buttons['play_pause'], self.buttons['prev'], self.buttons['next'], self.buttons['play_mode'] ],
			[ self.volume_slider ],
			[ self.buttons['volume-off'], self.buttons['volume-down'], self.buttons['volume-up'] ],
			[ self.brightness_slider ],
			[ self.buttons['minus'], self.buttons['plus'] ]
		]

		self.volume_slider.value = mpd.volume
		self.brightness_slider.value = int(float(self.get_brightness() / 255. * 100.))

		self.main.add_child(self.top_panel)
		self.main.add_child(self.volume_slider)
		self.main.add_child(self.volume_panel)
		self.main.add_child(self.brightness_slider)
		self.main.add_child(self.brightness_panel)

		mpd.mpd_client.random(0)
		mpd.mpd_client.single(0)
		mpd.mpd_client.repeat(0)

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
				self.active_sidebar_btn = 0
				self.sidebar_btns[self.active_sidebar_btn].state = 'focused'
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
			if self.active_btn == self.volume_slider:
				self.volume_slider.value = self.volume_slider.value - 2
			elif self.active_btn == self.brightness_slider:
				self.brightness_slider.value = self.brightness_slider.value - 2
			else:
				if self.sibling_index == 0:
					self.active_btn.state = 'normal'
					self.active_btn_index = 0
					self.main_active = False
					self.active_sidebar_btn = 0
					self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

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
			if self.active_btn == self.volume_slider:
				self.volume_slider.value = self.volume_slider.value + 2
			elif self.active_btn == self.brightness_slider:
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

			if self.active_btn == self.volume_slider:
				return

			self.active_btn.on_clicked(self.active_btn, False)

	"""
	entered
	"""
	def entered(self):

		PiScene.entered(self)

		self.volume_slider.value = mpd.volume

		state = mpd.get_playback()

		play_btn = self.buttons['play_pause']

		if play_btn.icon_class != 'play' and state == 'play':
			play_btn.icon_class = 'play'
		if play_btn.icon_class != 'pause' and state == 'pause':
			play_btn.icon_class = 'pause'

		self.stylize()

		PiScene.entered(self)

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):

		while True:
			try:

				event = mpd.events.popleft()

				#print 'Controls::on_mpd_update \t ' + event

				if event == 'volume':
					self.volume_slider.value = mpd.volume
				elif event == 'player_control':
					state = mpd.get_playback()
					play_btn = self.buttons['play_pause']
					if play_btn.icon_class != 'play' and state == 'play':
						play_btn.icon_class = 'play'
					if play_btn.icon_class != 'pause' and state == 'pause':
						play_btn.icon_class = 'pause'
					break

			except IndexError:
				break

	"""
	make_top_panel
	"""
	def make_top_panel(self):

		btns = [
			('play_pause',mpd.get_playback()),
			('prev','backward'),
			('next','forward'),
			('play_mode', self.play_modes[self.current_play_mode][1])
		]

		panel = ui.View(ui.Rect(
			self.padding,
			self.padding + 10,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))

		btn_x = panel.frame.width / 2 - self.btn_size * 2 - self.padding * 1.5

		for btn_data in btns:
			btn = ui.NavIconButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_data[1] )
			btn_x = btn_x + self.btn_size + self.padding
			btn.on_clicked.connect(self.on_button_click)
			btn.tag_name = btn_data[0]
			btn.sibling = False

			panel.add_child(btn)

			self.buttons[btn_data[0]] = btn

		return panel

	"""
	make_volume_panel
	"""
	def make_volume_panel(self):

		btns = ['volume-off', 'volume-down', 'volume-up']

		panel = ui.View(ui.Rect(
			self.padding,
			self.volume_slider.frame.bottom + self.padding, #self.padding * 3 + self.btn_size + self.volume_slider.frame.height,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))

		btn_x = panel.frame.width / 2 - self.btn_size * 1.5 - self.padding

		for btn_class in btns:
			btn = ui.NavIconButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_class )
			btn_x = btn_x + self.btn_size + self.padding
			btn.on_clicked.connect(self.on_button_click)
			btn.tag_name = btn_class
			btn.sibling = False;

			panel.add_child(btn)

			self.buttons[btn_class] = btn

		return panel

	"""
	make_volume_slider
	"""
	def make_volume_slider(self):

		title = ui.HeadingOne(
			ui.Rect(
				0,
				self.top_panel.frame.bottom + self.padding,
				self.main.frame.width,
				self.label_height
			),
			'Volume',
			halign=ui.CENTER
		)

		self.main.add_child(title)

		slider = ui.SliderView( ui.Rect( self.left_margin, title.frame.bottom + self.padding, self.main.frame.width - self.left_margin * 2, ui.SCROLLBAR_SIZE ), ui.HORIZONTAL, 0, 100, show_thumb=False )
		slider.on_value_changed.connect(self.volume_slider_changed)
		slider.on_state_changed.connect(self.volume_slider_focused)
		return slider

	"""
	volume_slider_changed
	"""
	def volume_slider_changed(self, slider_view, value):
		mpd.set_volume(int(value))

	"""
	volume_slider_focused
	"""
	def volume_slider_focused(self):
		if self.volume_slider.state == 'focused':
			self.volume_slider.thumb.state = 'focused'
		else:
			self.volume_slider.thumb.state = 'normal'

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
			btn = ui.NavIconButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_class )
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

		title = ui.HeadingOne(
			ui.Rect(
				0,
				self.volume_panel.frame.bottom + self.padding,
				self.main.frame.width,
				self.label_height
			),
			'Brightness',
			halign=ui.CENTER
		)

		self.main.add_child(title)

		slider = ui.SliderView( ui.Rect( self.left_margin, title.frame.bottom + self.padding, self.main.frame.width - self.left_margin * 2, ui.SCROLLBAR_SIZE ), ui.HORIZONTAL, 0, 100, show_thumb=False )
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

		#print tag_name

		if tag_name == 'play_pause':
			if mpd.get_playback() == 'play':
				mpd.set_playback('pause')
				btn.icon_class = 'pause'
				btn.stylize()
			else:
				mpd.set_playback('play')
				btn.icon_class = 'play'
				btn.stylize()
		elif tag_name == 'volume-off':
			self.volume_slider.value = 0
		elif tag_name == 'volume-down':
			self.volume_slider.value = self.volume_slider.value - 10
		elif tag_name == 'volume-up':
			self.volume_slider.value = self.volume_slider.value + 10
		elif tag_name == 'minus':
			self.brightness_slider.value = self.brightness_slider.value - 10
		elif tag_name == 'plus':
			self.brightness_slider.value = self.brightness_slider.value + 10
		elif tag_name == 'prev':
			mpd.set_playback('previous')
		elif tag_name == 'next':
			mpd.set_playback('next')
		elif tag_name == 'play_mode':
			self.current_play_mode = self.current_play_mode + 1
			if self.current_play_mode > len(self.play_modes) - 1:
				self.current_play_mode = 0
			btn.icon_class = self.play_modes[self.current_play_mode][1]
			btn.stylize()
			play_mode = self.play_modes[self.current_play_mode][0]
			if play_mode == "normal":
				mpd.mpd_client.random(0)
			elif play_mode == "single_repeat":
				mpd.mpd_client.single(1)
				mpd.mpd_client.repeat(1)
			elif play_mode == "repeat_all":
				mpd.mpd_client.single(0)
			elif play_mode == "shuffle":
				mpd.mpd_client.repeat(0)
				mpd.mpd_client.random(1)

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
