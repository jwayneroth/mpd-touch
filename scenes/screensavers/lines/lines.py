import math
import pygame
import time
import sys
import os
from random import randint
from threading import Thread

import fmuglobals

from .point3d import Point3D
from .triangle import Triangle
from .light import Light

import logging
logger = logging.getLogger('fmu_logger')

PLANE_WIDTH = 750
PLANE_DEPTH = 1000

PLEATS = 30
PLEAT_WIDTH = int( PLANE_WIDTH / PLEATS )
PLEAT_MAX_HEIGHT = 175

PLANE_X = 0 - PLANE_WIDTH / 2
PLANE_Y = 170

PLANE_FRONT = -600
PLANE_BACK = PLANE_FRONT + PLANE_DEPTH

PIPE_BUFFER_SIZE = 1048576
PIPE_SIZE = 4 * PLEATS
PIPE_NAME = "/var/lib/mpd/myfifosa"
UPDATE_UI_INTERVAL = 0.033

BIN_MAX = 100 # fft max
UPDATE_UI_INTERVAL = .033
PIPE_POLLING_INTERVAL = UPDATE_UI_INTERVAL / 10
COLOR_CHANGE_INTERVAL_SECONDS = 5
BIN_DECAY = 2 # decay smoothing
BIN_DELAY = 10 # spike smoothing

class Lines():
	def __init__(self, window) :

		self.window = window
		self.batch = None

		self.pleat_points = []
		self.pleat_triangles = []

		self.plane_color = (255,255,255)
		self.bg_color = fmuglobals.FMU_COLORS['near_black']

		self.fl = 1800
		self.vpX = 400
		self.vpY = 175

		self.view_angle_x = 0
		self.view_angle_y = 0 # self.view_angle_y = 0 - math.pi / 8
		self.view_angle_z = 0
		
		self.cos_y = math.cos(self.view_angle_y)
		self.sin_y = math.sin(self.view_angle_y)

		self.light = Light(-1000, 100, 0, 1)
		
		# self.lightPoint = Point3D(self.light.x, self.light.y, self.light.z, self.fl)
		# self.lightPoint.setVanishingPoint(self.vpX, self.vpY)
		# self.lightPoint.setCenter(0, 0, PLANE_DEPTH / 2)
		# self.lightPoint.rotateX(self.view_angle_x)
		# self.lightPoint.rotateY(self.view_angle_y)
		# self.lightPoint.rotateZ(self.view_angle_z)

		self.run_flag = False
		self.run_datasource = False
		self.pipe = None

		thread = Thread(target=self.open_pipe)
		thread.start()

		self.initPlane()

	def open_pipe(self):
		""" Open named pipe  """

		try:
			self.pipe = os.open(PIPE_NAME, os.O_RDONLY | os.O_NONBLOCK)
		except Exception as e:
			logger.debug("Cannot open named pipe: " + PIPE_NAME)
			logger.debug(e)

	def get_latest_pipe_data(self):
		""" Read from the named pipe until it's empty """

		data = [0] * PIPE_SIZE
		while True:
			try:
				tmp_data = os.read(self.pipe, PIPE_SIZE)
				if len(tmp_data) == PIPE_SIZE:
					data = tmp_data
					time.sleep(PIPE_POLLING_INTERVAL)
			except:
				break

		return data

	"""
	loopDisplay
	"""
	def loopDisplay(self) :
		self.window.fill(self.bg_color)
		self.renderPlane()
		#self.renderLight()

	"""
	initPlane
	"""
	def initPlane(self) :
		
		x = PLANE_X
		y = PLANE_Y

		# create two 3d points for each spectrum bar
		for i in range(PLEATS) :
			x = PLANE_X + (i + 1) * PLEAT_WIDTH
			self.pleat_points.append( Point3D(x,y,PLANE_FRONT, self.fl) )
			self.pleat_points.append( Point3D(x,y,PLANE_BACK, self.fl) )

		color = (randint(0,255),randint(0,255),randint(0,255))

		# init 3d vals for each point
		for point in self.pleat_points:
			point.setVanishingPoint(self.vpX, self.vpY)
			point.setCenter(0, 0, PLANE_DEPTH / 2)
			point.rotateX(self.view_angle_x)
			point.rotateY(self.view_angle_y)
			point.rotateZ(self.view_angle_z)
			
			#color = (randint(0,255),randint(0,255),randint(0,255))
			point.color = color

	"""
	renderPlane
	"""
	def renderPlane(self, firstRun=False) :

		pts_count = len( self.pleat_points )

		for i in range( int( pts_count / 2 ) - 1) :
			ax = self.pleat_points[i*2].screenX
			ay = self.pleat_points[i*2].screenY
			bx = self.pleat_points[i*2+1].screenX
			by = self.pleat_points[i*2+1].screenY
			#logger.debug("line pts %d, %d : %d, %d", ax, ay, bx, by)
			
			self.render = pygame.draw.line(self.window, self.pleat_points[i*2].color, (ax,ay), (bx,by), 3)

	def start(self):
		self.index = 0
		self.run_flag = True
		self.start_data_source()

		if hasattr(self, "callback_start"):
			self.callback_start(self)
	
	def start_data_source(self):
		""" Start data source thread. """

		self.flush_pipe_buffer()
		self.run_datasource = True
		thread = Thread(target=self.get_data)
		thread.start()
	
	def flush_pipe_buffer(self):
		""" Flush data from the pipe """

		if not self.pipe:
			return

		try:
			os.read(self.pipe, PIPE_BUFFER_SIZE)
		except Exception as e:
			logger.debug(e)

	def get_data(self):
		""" Data Source Thread method. """ 

		seconds = 0

		while self.run_datasource:
			self.set_values()
			time.sleep(fmuglobals.SS_UPDATE_INTERVAL)
			seconds += fmuglobals.SS_UPDATE_INTERVAL
			if ( seconds >= COLOR_CHANGE_INTERVAL_SECONDS ) :
				seconds = 0
				self.do_color_change()

	def do_color_change(self) :
		color = (randint(0,255),randint(0,255),randint(0,255))
		# self.bg_color = (randint(0,255),randint(0,255),randint(0,255))
		for pt in self.pleat_points :
			pt.color = color

	def set_values(self):
		""" Get signal from the named pipe and update spectrum bars. """ 

		data = []

		try:
			if self.pipe == None:
				return
			data = self.get_latest_pipe_data()
		except Exception as e:
			logger.debug(e)
			return

		length = len(data)
		
		if length == 0:
			return

		words = int(length / 4)

		for m in range(words):
			v = data[4 * m] + (data[4 * m + 1] << 8) + (data[4 * m + 2] << 16) + (data[4 * m + 3] << 24)
			v = ( v / BIN_MAX ) * PLEAT_MAX_HEIGHT

			i = m * 2
			last_val = self.pleat_points[i].y
			val = PLANE_Y - v
			
			if ( val > last_val + BIN_DECAY ) :
				val = last_val + BIN_DECAY
			elif ( val < last_val - BIN_DELAY ) :
				val = last_val - BIN_DELAY

			#logger.debug("set val %d for %d", val, i)

			self.pleat_points[i].y = val
			self.pleat_points[i+1].y = val

	def stop(self):
		""" Stop spectrum thread. """ 
		
		self.run_flag = False
		self.run_datasource = False
		self.seconds = 0

		if hasattr(self, "callback_stop"):
			self.callback_stop(self)

		if hasattr(self, "malloc_trim"):
			self.malloc_trim()
