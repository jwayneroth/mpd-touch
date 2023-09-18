from .pidialogscene import *

"""
 ControlsDialog
  dialog scene with playback controls
"""
class ControlsDialog(PiDialogScene):
	def __init__(self, frame=None):

		PiDialogScene.__init__(self, frame, 'Volume')

		self.is_mpd_listener = True

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

		self.volume_slider = self.make_volume_slider()
		self.volume_panel = self.make_volume_panel()
		self.controls_panel = self.make_controls_panel()

		self.btns = [
			[ self.volume_slider ],
			[ self.buttons['volume-off'], self.buttons['volume-down'], self.buttons['volume-up'] ],
			[ self.buttons['play_pause'], self.buttons['prev'], self.buttons['next'], self.buttons['play_mode'] ],
		]

		self.volume_slider.value = mpd.volume

		self.main.add_child(self.controls_panel)
		self.main.add_child(self.volume_slider)
		self.main.add_child(self.volume_panel)

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
			if self.active_btn == self.volume_slider:
				self.volume_slider.value = self.volume_slider.value - 2
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
			if self.active_btn == self.volume_slider:
				self.volume_slider.value = self.volume_slider.value + 2
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

		logger.debug("vol slider val: %d; mpd vol: %d", self.volume_slider.value, mpd.volume)

		self.volume_slider.value = mpd.volume

		state = mpd.get_playback()

		play_btn = self.buttons['play_pause']

		if play_btn.icon_class != 'play' and state == 'play':
			play_btn.icon_class = 'play'
		if play_btn.icon_class != 'pause' and state == 'pause':
			play_btn.icon_class = 'pause'

		PiDialogScene.entered(self)

	"""
	on_mpd_update
	"""
	def on_mpd_update(self):
		logger.debug("%s::on_mpd_update", self.name)

		self.volume_slider.value = mpd.volume
		state = mpd.get_playback()
		play_btn = self.buttons['play_pause']
		if play_btn.icon_class != 'play' and state == 'play':
			play_btn.icon_class = 'play'
		if play_btn.icon_class != 'pause' and state == 'pause':
			play_btn.icon_class = 'pause'
	
		# while True:
		# 	try:

		# 		event = mpd.events.popleft()

		# 		logger.debug("event: %s", event)

		# 		if event == 'volume':
		# 			self.volume_slider.value = mpd.volume
		# 		elif event == 'player_control':
		# 			state = mpd.get_playback()
		# 			play_btn = self.buttons['play_pause']
		# 			if play_btn.icon_class != 'play' and state == 'play':
		# 				play_btn.icon_class = 'play'
		# 			if play_btn.icon_class != 'pause' and state == 'pause':
		# 				play_btn.icon_class = 'pause'
		# 			break

		# 	except IndexError:
		# 		break

	"""
	make_controls_panel
	"""
	def make_controls_panel(self):

		title = ui.DialogLabel(
			ui.Rect(
				0,
				self.volume_panel.frame.bottom + self.padding,
				self.main.frame.width,
				self.label_height
			),
			'Controls',
			halign=ui.CENTER
		)

		self.main.add_child(title)

		btns = [
			('play_pause',mpd.get_playback()),
			('prev','backward'),
			('next','forward'),
			('play_mode', self.play_modes[self.current_play_mode][1])
		]

		panel = ui.View(ui.Rect(
			self.padding,
			title.frame.bottom + self.padding,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))

		btn_x = panel.frame.width / 2 - self.btn_size * 2 - self.padding * 1.5

		for btn_data in btns:
			btn = ui.DialogButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_data[1] )
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
			self.volume_slider.frame.bottom + self.padding,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))

		btn_x = panel.frame.width / 2 - self.btn_size * 1.5 - self.padding

		for btn_class in btns:
			btn = ui.DialogButton( ui.Rect( btn_x, 0, self.btn_size, self.btn_size ), btn_class )
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
		slider = ui.SliderView( ui.Rect(self.left_margin, self.padding + 10, self.main.frame.width - self.left_margin * 2, ui.SCROLLBAR_SIZE ), ui.HORIZONTAL, 0, 100, show_thumb=False )
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
	on_button_click
	"""
	def on_button_click(self, btn, mouse_btn):

		tag_name = btn.tag_name

		#print tag_name

		if tag_name == 'play_pause':
			if mpd.get_playback() == 'play':
				mpd.set_playback('pause')
				btn.icon_class = 'pause'
			else:
				mpd.set_playback('play')
				btn.icon_class = 'play'
			self.stylize()
		elif tag_name == 'volume-off':
			self.volume_slider.value = 0
		elif tag_name == 'volume-down':
			self.volume_slider.value = self.volume_slider.value - 10
		elif tag_name == 'volume-up':
			self.volume_slider.value = self.volume_slider.value + 10
		elif tag_name == 'prev':
			mpd.set_playback('previous')
		elif tag_name == 'next':
			mpd.set_playback('next')
		elif tag_name == 'play_mode':
			self.current_play_mode = self.current_play_mode + 1
			if self.current_play_mode > len(self.play_modes) - 1:
				self.current_play_mode = 0
			btn.icon_class = self.play_modes[self.current_play_mode][1]
			self.stylize()
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
