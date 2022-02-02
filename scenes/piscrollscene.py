from .piscene import *

"""
PiScrollScene
 generic scene with mutliple scroll views
"""
class PiScrollScene(PiScene):
	def __init__(self, frame=None, name='PiScrollScene'):

		PiScene.__init__(self, frame, name)

		#page_nav = self.make_page_nav()
		
		self.page_nav_active = False

		#self.child_view_btns = []

		#self.main.add_child(self.page_down)
		#self.main.add_child(self.icon_down)
		#self.main.add_child(self.page_up)
		#self.main.add_child(self.icon_up)

		# idx of active scroll view
		self.current_child_index = 0

		# reference to active scroll view
		self.current_child = None

		# idx of active button row
		self.active_btn_row = 0

		# reference to last active button row idx for each scroll view
		self.view_idx = 0

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
			self.view_idx = new_index

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

			new_index = self.active_btn_index + 1
			
			row_length = len(self.child_view_btns[self.current_child_index][self.active_btn_row])
			
			if new_index < row_length:

				new_active_btn = self.child_view_btns[self.current_child_index][self.active_btn_row][new_index]

				if new_active_btn.state is 'disabled':
					return

				self.active_btn_index = new_index
				self.active_btn.state = 'normal'
				self.active_btn = new_active_btn
				self.active_btn.state = 'focused'

		#
		# return
		#
		elif key == pygame.K_RETURN:

			self.active_btn.on_clicked(self.active_btn, False)

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

		btn_down.tag_name = 'Down'
		btn_up.tag_name ='Up'

		btn_down.on_clicked.connect(self.on_page_nav_clicked)
		icon_down.on_clicked.connect(self.on_page_nav_clicked)
		btn_up.on_clicked.connect(self.on_page_nav_clicked)
		icon_up.on_clicked.connect(self.on_page_nav_clicked)

		self.page_down = btn_down
		self.icon_down = icon_down
		self.page_up = btn_up
		self.icon_up = icon_up
		
		return [btn_down, btn_up]

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
