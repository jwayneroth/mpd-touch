import pygameui as ui
import fmuglobals

class Fmutheme(ui.theme.Theme):
	def __init__(self):
		ui.theme.Theme.__init__(self)
		self.debug = False
		self.init_styles()

	def init_styles(self):
		near_black = fmuglobals.FMU_COLORS['near_black']
		dark_brown = fmuglobals.FMU_COLORS['dark_brown']
		mid_brown = fmuglobals.FMU_COLORS['mid_brown']
		slime = fmuglobals.FMU_COLORS['slime']
		lemon = fmuglobals.FMU_COLORS['lemon']
		orange = fmuglobals.FMU_COLORS['orange']
		dark_gray = fmuglobals.FMU_COLORS['dark_gray']
		mid_gray = fmuglobals.FMU_COLORS['mid_gray']
		light_gray = fmuglobals.FMU_COLORS['light_gray']
		dark_purple = fmuglobals.FMU_COLORS['dark_purple']
		light_purple = fmuglobals.FMU_COLORS['light_purple']
		grad_dark = fmuglobals.FMU_COLORS['grad_dark']
		grad_light = fmuglobals.FMU_COLORS['grad_light']
		
		# View
		self.set(class_name='View', state='normal', key='background_color', value=None)
		self.set(class_name='View', state='focused', key='background_color', value=None)
		self.set(class_name='View', state='selected', key='background_color', value=None)
		self.set(class_name='View', state='normal', key='border_color', value=light_gray) #value=None)
		if self.debug:
			self.set(class_name='View', state='normal', key='border_widths', value=1)
		else:
			self.set(class_name='View', state='normal', key='border_widths', value=None)
		self.set(class_name='View', state='normal', key='margin', value=(6, 6))
		self.set(class_name='View', state='normal', key='padding', value=(0, 0))
		self.set(class_name='View', state='normal', key='shadowed', value=False)

		#Scene
		self.set(class_name='Scene', state='normal', key='background_color', value=None)

		#Label
		self.set(class_name='Label', state='normal', key='text_color', value=mid_gray)
		self.set(class_name='Label', state='normal', key='background_color', value=near_black)
		self.set(class_name='Label', state='selected', key='text_color', value=lemon)
		self.set(class_name='Label', state='normal', key='text_shadow_color', value=None)
		self.set(class_name='Label', state='normal', key='text_shadow_offset', value=(0,0))
		self.set(class_name='Label', state='normal', key='padding', value=(6, 6))
		self.set(class_name='Label', state='normal', key='border_color', value=None)
		self.set(class_name='Label', state='normal', key='border_widths', value=None)
		self.set(class_name='Label', state='normal', key='font', value=ui.resource.get_font(32, use_bold=True)) #20, use_bold=True))

		self.label_height = 16 + 6 * 2

		#HeadingOne
		self.set(class_name='HeadingOne', state='normal', key='font', value=ui.resource.get_font(32, use_bold=True))
		self.set(class_name='HeadingOne', state='normal', key='text_color', value=mid_gray)
		
		self.set(class_name='DialogLabel', state='normal', key='background_color', value=None)
		
		#Button
		self.set(class_name='Button', state='normal', key='background_color', value=near_black)
		self.set(class_name='Button', state='focused', key='background_color', value=near_black)
		self.set(class_name='Button', state='selected', key='background_color', value=near_black)
		self.set(class_name='Button', state='normal', key='text_color', value=slime)
		self.set(class_name='Button', state='selected', key='text_color', value=lemon)
		self.set(class_name='Button', state='focused', key='text_color', value=orange)
		self.set(class_name='Button', state='disabled', key='text_color', value=mid_gray)
		self.set(class_name='Button', state='normal', key='font', value=ui.resource.get_font(32, use_bold=False)) #19, use_bold=False))
		self.set(class_name='Button', state='normal', key='border_widths', value=None)
		self.set(class_name='Button', state='normal', key='border_color', value=None)

		self.set(class_name='Overlay', state='normal', key='background_color', value=(0,0,0,179))

		self.button_height = 16 + 6 * 2

		self.set(class_name='IconButton', state='normal', key='text_color', value=light_purple)
		self.set(class_name='IconButton', state='disabled', key='text_color', value=mid_gray)
		self.set(class_name='IconButton', state='focused', key='text_color', value=orange)
		self.set(class_name='IconButton', state='selected', key='text_color', value=lemon)
		self.set(class_name='IconButton', state='normal', key='font', value=ui.resource.get_font(fmuglobals.ICON_SIZE, use_bold=False, name='glyphicons-halflings-regular'))

		self.set(class_name='NavIconButton', state='normal', key='font', value=ui.resource.get_font(fmuglobals.NAV_ICON_SIZE, use_bold=False, name='glyphicons-halflings-regular'))
		
		self.set(class_name='DialogButton', state='normal', key='font', value=ui.resource.get_font(fmuglobals.NAV_ICON_SIZE, use_bold=False, name='glyphicons-halflings-regular'))
		self.set(class_name='DialogButton', state='focused', key='background_color', value=None)
		self.set(class_name='DialogButton', state='selected', key='background_color', value=None)
		self.set(class_name='DialogButton', state='normal', key='background_color', value=None)
		
		self.set(class_name='ImageButton', state='normal', key='background_color', value=None)
		self.set(class_name='ImageButton', state='focused', key='background_color', value=None)
		self.set(class_name='ImageButton', state='normal', key='border_color', value=None)
		self.set(class_name='ImageButton', state='normal', key='border_widths', value=None)
		self.set(class_name='ImageButton', state='normal', key='padding', value=(0, 0))

		#Scroll
		self.set(class_name='ScrollbarThumbView', state='normal', key='background_color', value=dark_purple)
		self.set(class_name='ScrollbarThumbView', state='focused', key='background_color', value=(mid_gray, light_gray))
		self.set(class_name='ScrollbarThumbView', state='normal', key='border_widths', value=None)
		self.set(class_name='ScrollbarThumbView', state='normal', key='border_color', value=None)
		self.set(class_name='ScrollbarView', state='normal', key='background_color', value=near_black)
		self.set(class_name='ScrollbarView', state='normal', key='border_widths', value=1)
		self.set(class_name='ScrollbarView', state='normal', key='border_color', value=dark_purple)
		self.set(class_name='ScrollView', state='normal', key='hole_color', value=near_black)
		self.set(class_name='ScrollView', state='normal', key='border_widths', value=None)
		self.set(class_name='ScrollView', state='normal', key='border_color', value=None)
		self.set(class_name='ScrollView', state='normal', key='background_color', value=near_black)

		self.set(class_name='SliderTrackView', state='normal', key='background_color', value=near_black)
		self.set(class_name='SliderTrackView', state='normal', key='value_color', value=dark_purple)
		self.set(class_name='SliderTrackView', state='focused', key='value_color', value=orange)
		self.set(class_name='SliderTrackView', state='selected', key='value_color', value=dark_purple)
		self.set(class_name='SliderTrackView', state='normal', key='border_widths', value=1)
		self.set(class_name='SliderTrackView', state='normal', key='border_color', value=dark_purple)
		self.set(class_name='SliderTrackView', state='focused', key='border_color', value=orange)

		self.set(class_name='SliderView', state='normal', key='background_color', value=None)
		self.set(class_name='SliderView', state='normal', key='border_widths', value=None)

		self.set(class_name='ImageView', state='normal', key='background_color', value=None)
		self.set(class_name='ImageView', state='normal', key='padding', value=(0, 0))

		self.set(class_name='Checkbox', state='normal', key='background_color', value=None)
		self.set(class_name='Checkbox', state='normal', key='padding', value=(0, 0))
		self.set(class_name='Checkbox', state='focused', key='check_label.background_color', value=(mid_gray, light_gray))
		self.set(class_name='Checkbox', state='normal', key='check_label.border_widths', value=1)
		self.set(class_name='Checkbox', state='normal', key='label.background_color', value=None)

		self.set(class_name='SpinnerView', state='normal', key='border_widths', value=None)

		self.set(class_name='DialogView', state='normal', key='background_color', value=None)
		self.set(class_name='DialogView', state='normal', key='shadowed', value=False)

		self.set(class_name='DialogContent', state='normal', key='border_color', value=light_purple)
		self.set(class_name='DialogContent', state='normal', key='border_widths', value=2)
		self.set(class_name='DialogContent', state='normal', key='background_color', value=(grad_dark,grad_light))
		
		self.shadow_size = 140

		self.set(class_name='AlertView', state='normal', key='title_label.background_color', value=None)
		self.set(class_name='AlertView', state='normal', key='title_label.text_color', value=mid_gray)
		self.set(class_name='AlertView', state='normal', key='title_label.text_shadow_offset', value=None)
		self.set(class_name='AlertView', state='normal', key='message_label.background_color', value=None)
		self.set(class_name='AlertView', state='normal', key='font', value=ui.resource.get_font(16))
		self.set(class_name='AlertView', state='normal', key='padding', value=(6, 6))

		self.set(class_name='NotificationView', state='normal', key='background_color', value=(mid_gray, light_gray))
		self.set(class_name='NotificationView', state='normal', key='border_color', value=light_gray)
		self.set(class_name='NotificationView', state='normal', key='border_widths', value=(0, 2, 2, 2))
		self.set(class_name='NotificationView', state='normal', key='padding', value=(0, 0))
		self.set(class_name='NotificationView', state='normal', key='message_label.background_color', value=None)

		self.set(class_name='SelectView', state='normal', key='disclosure_triangle_color', value=light_gray)
		self.set(class_name='SelectView', state='normal', key='border_widths', value=1)
		self.set(class_name='SelectView', state='normal', key='top_label.focusable', value=False)

		self.set(class_name='TextField', state='focused', key='label.background_color', value=dark_brown)
		self.set(class_name='TextField', state='normal', key='placeholder_text_color', value=mid_gray)
		self.set(class_name='TextField', state='normal', key='border_widths', value=1)
		self.set(class_name='TextField', state='normal', key='text_color', value=mid_gray)
		self.set(class_name='TextField', state='disabled', key='text_color', value=light_gray)
		self.set(class_name='TextField', state='normal', key='blink_cursor', value=True)
		self.set(class_name='TextField', state='normal', key='cursor_blink_duration', value=450)

		self.set(class_name='GridView', state='normal', key='background_color', value=mid_gray)
		self.set(class_name='GridView', state='normal', key='line_color', value=light_gray)

		self.set(class_name='PiScene', state='normal', key='background_color', value=near_black)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
