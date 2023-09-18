
import math

class Light() :
	def __init__(self, x= -100, y = -100, z = -100, brightness = 1) :
		self.x = x
		self.y = y
		self.z = z
		self.brightness = brightness
	
	def brightness(self, b) :
		self.brightness = math.max(b, 0)
		self.brightness = math.min(self.brightness, 1)
	
	def brightness(self) :
		return self.brightness