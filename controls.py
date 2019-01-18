import Tkinter as tk
from piscene import *

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
		self.left_margin = 50
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
		self.bottom_panel = self.make_bottom_panel()
		
		self.btns = [
			[ self.buttons['play_pause'], self.buttons['prev'],	 self.buttons['next'], self.buttons['play_mode'] ],
			[ self.volume_slider ], 
			[ self.buttons['volume-off'],  self.buttons['volume-down'],	 self.buttons['volume-up'] ]
		]
		
		self.volume_slider.value = mpd.volume
		
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

		print 'ControlsScene::entered'

		PiScene.entered(self)

		self.volume_slider.value = mpd.volume
		
		state = mpd.player_control_get()
		
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
					state = mpd.player_control_get()
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
		
		panel = tk.Frame(self.inner, background=fmuglobals.COLORS['near_black'])
		
		btns = [
			('play_pause', mpd.player_control_get()),
			('prev', 'backward'),
			('next', 'forward'),
			('play_mode', self.play_modes[self.current_play_mode][1])
		]
		
		"""
		panel = ui.View(ui.Rect(
			self.padding,
			self.padding + 10,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))
		"""

		for btn_data in btns:
			btn_img = tk.PhotoImage(file='images/icon.gif', width=20, height=20)# + btn_data[1])
			btn = tk.Button(panel, image=btn_img, width=50, height=50)
			btn.image = btn_img
			def cb(evt, self=self, btn_data=btn_data):
				return self.on_button_click(evt, btn_data[0])
			btn.bind('<Button-1>', cb)
			#btn.tag_name = btn_data[0]
			#btn.sibling = False
			btn.pack(side=tk.LEFT, expand=tk.YES)
			
			self.buttons[btn_data[0]] = btn
		
		panel.pack(side=tk.TOP, anchor=tk.W, fill=tk.X, expand=tk.YES)
		
		return panel

	"""
	make_bottom_panel
	"""
	def make_bottom_panel(self):
		
		panel = tk.Frame(self.inner, background=fmuglobals.COLORS['near_black'])
		
		btns = ['volume-off', 'volume-down', 'volume-up']
		
		"""
		panel = ui.View(ui.Rect(
			self.padding,
			self.padding * 3 + self.btn_size + self.volume_slider.frame.height,
			self.main.frame.width - self.padding * 2,
			self.btn_size
		))
		"""

		for btn_class in btns:
			btn_img = tk.PhotoImage(file='images/icon.gif', width=20, height=20)# + btn_data[1])
			btn = tk.Button(panel, image=btn_img, width=50, height=50)
			btn.image = btn_img
			def cb(evt, self=self, btn_class=btn_class):
				return self.on_button_click(evt, btn_class)
			btn.bind('<Button-1>', cb)
			#btn.tag_name = btn_data[0]
			#btn.sibling = False
			btn.pack(side=tk.LEFT, expand=tk.YES)
			self.buttons[btn_class] = btn
			
		panel.pack(side=tk.BOTTOM, anchor=tk.W, fill=tk.X, expand=tk.YES)
		
		return panel

	"""
	make_volume_slider
	"""
	def make_volume_slider(self):
		slider = tk.Scale(self.inner, background=fmuglobals.COLORS['near_black'])
		#slider.on_value_changed.connect(self.volume_slider_changed)
		#slider.on_state_changed.connect(self.volume_slider_focused)
		slider.pack()
		return slider
		
	"""
	volume_slider_changed
	"""
	def volume_slider_changed(self, slider_view, value):
		mpd.volume_set(int(value))

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
			if mpd.player_control_get() == 'play':
				mpd.player_control_set('pause')
				btn.icon_class = 'pause'
				btn.stylize()
			else:
				mpd.player_control_set('play')
				btn.icon_class = 'play'
				btn.stylize()
		elif tag_name == 'volume-off':
			self.volume_slider.value = 0
		elif tag_name == 'volume-down':
			self.volume_slider.value = self.volume_slider.value - 10
		elif tag_name == 'volume-up':
			self.volume_slider.value = self.volume_slider.value + 10
		elif tag_name == 'prev':
			mpd.player_control_set('previous')
		elif tag_name == 'next':
			mpd.player_control_set('next')
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
def make_close_btn(self):
		btn = ui.IconButton(
			ui.Rect(self.content.frame.width - self.btn_size - 10,5,self.btn_size,self.btn_size),
			'remove'
		)
		btn.on_clicked.connect(self._dismiss)
		return btn
def make_overlay(self):
		btn = Overlay(ui.Rect(0,0,self.frame.width,self.frame.height))
		btn.on_clicked.connect(self._dismiss)
		return btn

	def _dismiss(self, btn, mbtn):
		self.dismiss()
class DialogContent(ui.View):
	def __init__(self, frame):
		ui.View.__init__(self,frame)

class Overlay(ui.Button):
	def __init__(self, frame):
		ui.Button.__init__(self,frame, '')
"""
"""
 PiControls
  dialog view with playback controls
"""
"""
class PiControls(ui.DialogView):
	def __init__(self, frame):
	
		ui.DialogView.__init__(self, frame)

		self.top_margin = 30
		self.left_margin = 50
		self.padding = 25
		self.btn_size = 45

		self.buttons = {}

		self.overlay = self.make_overlay()
		self.content = DialogContent(ui.Rect(self.left_margin,self.top_margin,self.frame.width-self.left_margin*2,self.frame.height-self.top_margin*2))
		self.top_panel = self.make_top_panel()
		self.volume_slider = self.make_volume_slider()
		self.bottom_panel = self.make_bottom_panel()
		self.close_btn = self.make_close_btn()

		self.volume_slider.value = mpd.volume

		self.add_child(self.overlay)
		self.add_child(self.content)
		self.content.add_child(self.top_panel)
		self.content.add_child(self.volume_slider)
		self.content.add_child(self.bottom_panel)
		self.content.add_child(self.close_btn)

	def make_close_btn(self):
		btn = ui.IconButton(
			ui.Rect(self.content.frame.width - self.btn_size - 10,5,self.btn_size,self.btn_size),
			'remove'
		)
		btn.on_clicked.connect(self._dismiss)
		return btn

	def make_top_panel(self):

		btns = [
			('play_pause',mpd.player_control_get()),
			('prev','backward'),
			('next','forward')
		]
		
		panel = ui.View(ui.Rect(
			self.padding,
			self.padding + 10,
			self.content.frame.width - self.padding * 2,
			self.btn_size
		))
		
		btn_x = panel.frame.width / 2 - self.btn_size * 1.5 - self.padding #self.btnsself.padding

		for btn_data in btns:
			btn = ui.IconButton(
				ui.Rect(
					btn_x,
					0,
					self.btn_size,
					self.btn_size
				),
				btn_data[1]
			)
			btn_x = btn_x + self.btn_size + self.padding
			btn.on_clicked.connect(self.on_button_click)
			btn.tag_name = btn_data[0]
			panel.add_child(btn)
			self.buttons[btn_data[0]] = btn

		return panel

	def make_bottom_panel(self):

		btns = ['volume-off', 'volume-down', 'volume-up']
		
		panel = ui.View(ui.Rect(
			self.padding,
			self.padding * 3 + self.btn_size + self.volume_slider.frame.height,
			self.content.frame.width - self.padding * 2,
			self.btn_size
		))
		
		btn_x = panel.frame.width / 2 - self.btn_size * 1.5 - self.padding #self.btnsself.padding

		for btn_class in btns:
			btn = ui.IconButton(
				ui.Rect(
					btn_x,
					0,
					self.btn_size,
					self.btn_size
				),
				btn_class
			)
			btn_x = btn_x + self.btn_size + self.padding
			btn.on_clicked.connect(self.on_button_click)
			btn.tag_name = btn_class
			panel.add_child(btn)
			self.buttons[btn_class] = btn

		return panel


	def make_volume_slider(self):

		slider = ui.SliderView(
			ui.Rect(
				self.padding,
				self.top_panel.frame.bottom+self.padding,
				self.content.frame.width-self.padding*2,
				ui.SCROLLBAR_SIZE
			), 
			ui.HORIZONTAL, 
			0, 
			100
		)
		slider.on_value_changed.connect(self.volume_slider_changed)
		return slider

	def make_overlay(self):
		btn = Overlay(ui.Rect(0,0,self.frame.width,self.frame.height))
		btn.on_clicked.connect(self._dismiss)
		return btn

	def _dismiss(self, btn, mbtn):
		self.dismiss()

	def on_button_click(self, btn, mouse_btn):
		
		tag_name = btn.tag_name

		#print tag_name

		if tag_name == 'play_pause':
			if mpd.player_control_get() == 'play':
				mpd.player_control_set('pause')
				btn.icon_class = 'pause'
			else:
				mpd.player_control_set('play')
				btn.icon_class = 'play'
		elif tag_name == 'volume-off':
			self.volume_slider.value = 0
		elif tag_name == 'volume-down':
			self.volume_slider.value = self.volume_slider.value - 10
		elif tag_name == 'volume-up':
			self.volume_slider.value = self.volume_slider.value + 10
		elif tag_name == 'prev':
			mpd.player_control_set('previous')
		elif tag_name == 'next':
			mpd.player_control_set('next')

	def volume_slider_changed(self, slider_view, value):
		#print 'vol ' + str(value)
		mpd.volume_set(int(value))

class DialogContent(ui.View):
	def __init__(self, frame):
		ui.View.__init__(self,frame)

class Overlay(ui.Button):
	def __init__(self, frame):
		ui.Button.__init__(self,frame, '')
"""