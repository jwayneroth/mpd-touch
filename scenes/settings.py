import socket
import subprocess

import fmuglobals
from .piscene import *

#if fmuglobals.RUN_ON_RASPBERRY_PI:
#	 import RPi.GPIO as GPIO

"""
SettingsScene
 app settings
"""
class SettingsScene(PiScene):
	def __init__(self, frame, name):

		PiScene.__init__(self, frame, name)

		self.sidebar_index = 3
		self.active_sidebar_btn = 3

		self.active_btn_index = 0
		self.active_btn = False

		self.btn_data = [
			{ 'name':'settings', 'icon_class':'cog', 'text':'Settings' },
			#{ 'name':'brightness', 'icon_class':'subglasses', 'text':'Brightness' },
			{ 'name':'update', 'icon_class':'hdd', 'text':'Update Music DB' },
			{ 'name':'restart', 'icon_class':'repeat', 'text':'Restart Player' },
			{ 'name':'quit', 'icon_class':'remove', 'text':'Quit Player' },
			{ 'name':'reboot', 'icon_class':'signal', 'text':'Restart Pi' },
			{ 'name':'shutdown', 'icon_class':'off', 'text':'Shutdown' }
		]

		self.btns = []

		self.make_buttons()

	"""
	on_main_active
	"""
	def on_main_active(self):
		self.active_btn_index = 0
		self.active_btn = self.btns[self.active_btn_index]
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
			self.active_btn = self.btns[new_index]
			self.active_btn.state = 'focused'
			self.active_btn_index = new_index
			self.sibling_active = False

		#
		# down
		#
		elif key == pygame.K_DOWN:

			new_index = self.active_btn_index + 1

			if new_index >= len(self.btns):
				return

			self.active_btn.state = 'normal'
			self.active_btn = self.btns[new_index]
			self.active_btn.state = 'focused'
			self.active_btn_index = new_index
			self.sibling_active = False

		#
		# left
		#
		elif key == pygame.K_LEFT:
			self.active_btn.state = 'normal'
			self.active_btn_index = 0
			self.main_active = False
			self.active_sidebar_btn = 0
			self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

		#
		# right
		#
		elif key == pygame.K_RIGHT:
			pass

		#
		# return
		#
		elif key == pygame.K_RETURN:

			self.active_btn.on_clicked(self.active_btn, False)

	"""
	make_buttons
	"""
	def make_buttons(self):

		btn_data = self.btn_data

		scr_y = 0

		for data in btn_data:

			icon = ui.IconButton(
				ui.Rect(
					self.margins,
					scr_y,
					self.btn_size,
					self.btn_size
				),
				data['icon_class']
			)
			icon.name = data['name']
			icon.on_clicked.connect(self.on_btn_clicked)

			btn = ui.Button(
				ui.Rect(icon.frame.right + self.margins, scr_y, 0, self.label_height),
				data['text'],
				halign=ui.LEFT,
				valign=ui.CENTER
			)
			btn.name = data['name']
			btn.on_clicked.connect(self.on_btn_clicked)
			btn.sibling = False

			self.btns.append(btn)
			self.main.add_child(icon)
			self.main.add_child(btn)

			scr_y = scr_y + self.label_height

		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(('google.com', 0))
			ip_address = s.getsockname()[0]

			#print 'SettingsScene::make_buttons \t ip: ' + ip_address

			self.main.add_child(ui.Label(
				ui.Rect(icon.frame.right + self.margins,scr_y,self.main.frame.width,self.label_height),
				"IP: " + ip_address,
				halign=ui.LEFT,
				valign=ui.CENTER
			))
		except Exception:
			#print 'SettingsScene::make_buttons \t couldnt get ip'
			pass

	"""
	on_btn_clicked
	"""
	def on_btn_clicked(self, btn, mouse_btn):
		logger.debug("Settings::on_btn_clicked %s", btn.name)

		if btn.name == 'settings':
			pass

		if btn.name == 'shutdown':
			if fmuglobals.RUN_ON_RASPBERRY_PI:
				#GPIO.output(18, GPIO.LOW)
				logger.debug('calling shutdown')
				subprocess.Popen('sudo shutdown -h now', shell=True, stdout=subprocess.PIPE)
			else:
				import pygame
				import sys
				pygame.quit()
				sys.exit(0)

		elif btn.name == 'reboot':
			if fmuglobals.RUN_ON_RASPBERRY_PI:
				logger.debug('calling reboot now')
				subprocess.Popen('sudo shutdown -r now', shell=True, stdout=subprocess.PIPE)
			else:
				import pygame
				import sys
				pygame.quit()
				sys.exit(0)

		elif btn.name == 'update':
			import pygame
			mpd.library_rescan()
			pygame.time.wait(5000)
			self.on_nav_change('Albums', True)

		elif btn.name == 'restart':
			if fmuglobals.RUN_ON_RASPBERRY_PI:
				#pygame.display.quit()
				#os.system("sudo service fmulcd restart")
				logger.debug('requesting fmulcd service restart')
				subprocess.Popen('sudo service fmulcd restart', shell=True, stdout=subprocess.PIPE)
			else:
				import pygame
				import sys
				pygame.quit()
				sys.exit(0)

		elif btn.name == 'quit':
			logger.debug('quitting fmulcd')
			if fmuglobals.RUN_ON_RASPBERRY_PI:
				import pygame
				pygame.quit()
				try:
					subprocess.Popen('sudo service fmulcd stop', shell=True, stdout=subprocess.PIPE)
				except:
					pass
				import sys
				sys.exit(0)
			else:
				import pygame
				import sys
				pygame.quit()
				sys.exit(0)

		elif btn.name == 'brightness':
			self.open_dialog('Brightness')
