from itertools import chain
import resource

class Theme(object):
	def __init__(self):
		self._styles = {}

	def set(self, class_name, state, key, value):
		self._styles.setdefault(class_name, {}).setdefault(state, {})
		self._styles[class_name][state][key] = value

	def get_dict_for_class(self, class_name, state=None, base_name='View'):
		classes = []
		klass = class_name

		while True:
			classes.append(klass)
			if klass.__name__ == base_name:
				break
			klass = klass.__bases__[0]

		if state is None:
			state = 'normal'

		style = {}

		for klass in classes:
			class_name = klass.__name__

			try:
				state_styles = self._styles[class_name][state]
			except KeyError:
				state_styles = {}

			if state != 'normal':
				try:
					normal_styles = self._styles[class_name]['normal']
				except KeyError:
					normal_styles = {}

				state_styles = dict(chain(normal_styles.iteritems(),
										  state_styles.iteritems()))

			style = dict(chain(state_styles.iteritems(),
							   style.iteritems()))

		return style

	def get_dict(self, obj, state=None, base_name='View'):
		return self.get_dict_for_class(class_name=obj.__class__,
									   state=obj.state,
									   base_name=base_name)

	def get_value(self, class_name, attr, default_value=None,
				  state='normal', base_name='View'):
		styles = self.get_dict_for_class(class_name, state, base_name)
		try:
			return styles[attr]
		except KeyError:
			return default_value

current = None
dark_theme = Theme()

def use_theme(theme):
	global current
	current = theme

def init_dark_theme():
	near_black = (10,5,0)
	dark_brown = (60,44,28)
	mid_brown = (80,62,32)
	slime = (139,250,73)
	lemon = (246,248,63)
	orange = (240,140,2)
	dark_gray = (80,77,81)
	mid_gray = (124,120,132)
	light_gray = (180,140,190)
	dark_purple = (60,50,65)
	light_purple = (124,100,118)

	# View
	dark_theme.set(class_name='View', state='normal', key='background_color', value=None)
	dark_theme.set(class_name='View', state='focused', key='background_color', value=None)
	dark_theme.set(class_name='View', state='selected', key='background_color', value=None)
	dark_theme.set(class_name='View', state='normal', key='border_color', value=None)
	dark_theme.set(class_name='View', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='View', state='normal', key='margin', value=(6, 6))
	dark_theme.set(class_name='View', state='normal', key='padding', value=(0, 0))
	dark_theme.set(class_name='View', state='normal', key='shadowed', value=False)

	#Scene
	dark_theme.set(class_name='Scene', state='normal', key='background_color', value=None)

	#Label
	dark_theme.set(class_name='Label', state='normal', key='text_color', value=mid_gray)
	dark_theme.set(class_name='Label', state='normal', key='background_color', value=near_black)
	dark_theme.set(class_name='Label', state='selected', key='text_color', value=lemon)
	dark_theme.set(class_name='Label', state='normal', key='text_shadow_color', value=None)
	dark_theme.set(class_name='Label', state='normal', key='text_shadow_offset', value=(0,0))
	dark_theme.set(class_name='Label', state='normal', key='padding', value=(6, 6))
	dark_theme.set(class_name='Label', state='normal', key='border_color', value=None)
	dark_theme.set(class_name='Label', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='Label', state='normal', key='font', value=resource.get_font(20, use_bold=True))

	dark_theme.label_height = 16 + 6 * 2

	#HeadingOne
	dark_theme.set(class_name='HeadingOne', state='normal', key='font', value=resource.get_font(32, use_bold=True))
	dark_theme.set(class_name='HeadingOne', state='normal', key='text_color', value=light_gray)

	#Button
	dark_theme.set(class_name='Button', state='normal', key='background_color', value=near_black)
	dark_theme.set(class_name='Button', state='focused', key='background_color', value=near_black)
	dark_theme.set(class_name='Button', state='selected', key='background_color', value=near_black)
	dark_theme.set(class_name='Button', state='normal', key='text_color', value=slime)
	dark_theme.set(class_name='Button', state='selected', key='text_color', value=lemon)
	dark_theme.set(class_name='Button', state='focused', key='text_color', value=orange)
	dark_theme.set(class_name='Button', state='disabled', key='text_color', value=mid_gray)
	dark_theme.set(class_name='Button', state='normal', key='font', value=resource.get_font(19, use_bold=False))
	dark_theme.set(class_name='Button', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='Button', state='normal', key='border_color', value=None)

	dark_theme.set(class_name='Overlay', state='normal', key='background_color', value=(0,0,0,179))

	dark_theme.button_height = 16 + 6 * 2

	dark_theme.set(class_name='IconButton', state='normal', key='text_color', value=light_purple)
	dark_theme.set(class_name='IconButton', state='disabled', key='text_color', value=mid_gray)
	dark_theme.set(class_name='IconButton', state='focused', key='text_color', value=orange)
	dark_theme.set(class_name='IconButton', state='selected', key='text_color', value=lemon)
	dark_theme.set(class_name='IconButton', state='normal', key='font', value=resource.get_font(24, use_bold=False, name='glyphicons-halflings-regular'))

	dark_theme.set(class_name='ImageButton', state='normal', key='background_color', value=None)
	dark_theme.set(class_name='ImageButton', state='focused', key='background_color', value=None)
	dark_theme.set(class_name='ImageButton', state='normal', key='border_color', value=None)
	dark_theme.set(class_name='ImageButton', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='ImageButton', state='normal', key='padding', value=(0, 0))

	#Scroll
	dark_theme.set(class_name='ScrollbarThumbView', state='normal', key='background_color', value=dark_purple)
	dark_theme.set(class_name='ScrollbarThumbView', state='focused', key='background_color', value=(mid_gray, light_gray))
	dark_theme.set(class_name='ScrollbarThumbView', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='ScrollbarThumbView', state='normal', key='border_color', value=None)
	dark_theme.set(class_name='ScrollbarView', state='normal', key='background_color', value=near_black)
	dark_theme.set(class_name='ScrollbarView', state='normal', key='border_widths', value=1)
	dark_theme.set(class_name='ScrollbarView', state='normal', key='border_color', value=dark_purple)
	dark_theme.set(class_name='ScrollView', state='normal', key='hole_color', value=near_black)
	dark_theme.set(class_name='ScrollView', state='normal', key='border_widths', value=None)
	dark_theme.set(class_name='ScrollView', state='normal', key='border_color', value=None)
	dark_theme.set(class_name='ScrollView', state='normal', key='background_color', value=near_black)

	dark_theme.set(class_name='SliderTrackView', state='normal', key='background_color', value=near_black)
	dark_theme.set(class_name='SliderTrackView', state='normal', key='value_color', value=dark_purple)
	dark_theme.set(class_name='SliderTrackView', state='focused', key='value_color', value=orange)
	dark_theme.set(class_name='SliderTrackView', state='selected', key='value_color', value=dark_purple)
	dark_theme.set(class_name='SliderTrackView', state='normal', key='border_widths', value=1)
	dark_theme.set(class_name='SliderTrackView', state='normal', key='border_color', value=dark_purple)
	dark_theme.set(class_name='SliderTrackView', state='focused', key='border_color', value=orange)

	dark_theme.set(class_name='SliderView', state='normal', key='background_color', value=near_black)
	dark_theme.set(class_name='SliderView', state='normal', key='border_widths', value=None)

	dark_theme.set(class_name='ImageView', state='normal', key='background_color', value=None)
	dark_theme.set(class_name='ImageView', state='normal', key='padding', value=(0, 0))

	dark_theme.set(class_name='Checkbox', state='normal', key='background_color', value=None)
	dark_theme.set(class_name='Checkbox', state='normal', key='padding', value=(0, 0))
	dark_theme.set(class_name='Checkbox', state='focused', key='check_label.background_color', value=(mid_gray, light_gray))
	dark_theme.set(class_name='Checkbox', state='normal', key='check_label.border_widths', value=1)
	dark_theme.set(class_name='Checkbox', state='normal', key='label.background_color', value=None)

	dark_theme.set(class_name='SpinnerView', state='normal', key='border_widths', value=None)

	dark_theme.set(class_name='DialogView', state='normal', key='background_color', value=None)
	dark_theme.set(class_name='DialogView', state='normal', key='shadowed', value=False)

	dark_theme.set(class_name='DialogContent', state='normal', key='background_color', value=(32,27,29,200))
	dark_theme.set(class_name='DialogContent', state='normal', key='border_color', value=(30,30,30))
	dark_theme.set(class_name='DialogContent', state='normal', key='border_widths', value=1)

	dark_theme.shadow_size = 140

	dark_theme.set(class_name='AlertView', state='normal', key='title_label.background_color', value=None)
	dark_theme.set(class_name='AlertView', state='normal', key='title_label.text_color', value=mid_gray)
	dark_theme.set(class_name='AlertView', state='normal', key='title_label.text_shadow_offset', value=None)
	dark_theme.set(class_name='AlertView', state='normal', key='message_label.background_color', value=None)
	dark_theme.set(class_name='AlertView', state='normal', key='font', value=resource.get_font(16))
	dark_theme.set(class_name='AlertView', state='normal', key='padding', value=(6, 6))

	dark_theme.set(class_name='NotificationView', state='normal', key='background_color', value=(mid_gray, light_gray))
	dark_theme.set(class_name='NotificationView', state='normal', key='border_color', value=light_gray)
	dark_theme.set(class_name='NotificationView', state='normal', key='border_widths', value=(0, 2, 2, 2))
	dark_theme.set(class_name='NotificationView', state='normal', key='padding', value=(0, 0))
	dark_theme.set(class_name='NotificationView', state='normal', key='message_label.background_color', value=None)

	dark_theme.set(class_name='SelectView', state='normal', key='disclosure_triangle_color', value=light_gray)
	dark_theme.set(class_name='SelectView', state='normal', key='border_widths', value=1)
	dark_theme.set(class_name='SelectView', state='normal', key='top_label.focusable', value=False)

	dark_theme.set(class_name='TextField', state='focused', key='label.background_color', value=dark_brown)
	dark_theme.set(class_name='TextField', state='normal', key='placeholder_text_color', value=mid_gray)
	dark_theme.set(class_name='TextField', state='normal', key='border_widths', value=1)
	dark_theme.set(class_name='TextField', state='normal', key='text_color', value=mid_gray)
	dark_theme.set(class_name='TextField', state='disabled', key='text_color', value=light_gray)
	dark_theme.set(class_name='TextField', state='normal', key='blink_cursor', value=True)
	dark_theme.set(class_name='TextField', state='normal', key='cursor_blink_duration', value=450)

	dark_theme.set(class_name='GridView', state='normal', key='background_color', value=mid_gray)
	dark_theme.set(class_name='GridView', state='normal', key='line_color', value=light_gray)

	dark_theme.set(class_name='PiScene', state='normal', key='background_color', value=near_black)

def init():
	init_dark_theme()
