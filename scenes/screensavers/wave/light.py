import pygame
import math
from .point3d import Point3D

class Light() :
	def __init__(self, x= -100, y = -100, z = -100, brightness = 1, window=None) :
		self.x = x
		self.y = y
		self.z = z
		self.brightness = brightness
		self.color = '#ffffff'
		self.point = Point3D(x,y,z)
		self.window = window

	def setPoint(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		self.point.x = x
		self.point.y = y
		self.point.z = z

	def brightness(self, b) :
		self.brightness = math.max(b, 0)
		self.brightness = math.min(self.brightness, 1)
	
	def brightness(self) :
		return self.brightness

	def draw(self):
		x = self.point.screenX
		y = self.point.screenY
		self.render = pygame.draw.circle(self.window, self.color, [x, y], 10, 0)