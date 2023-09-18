import math

class Point3D() :
	def __init__(self, x, y, z, fl=250) :
		self._x = x
		self._y = y
		self._z = z
		self._fl = fl
		self._color = (255,255,255)
	
	def setVanishingPoint(self, vpX, vpY) :
		self._vpX = vpX
		self._vpY = vpY

	def setCenter(self, cX, cY, cZ) :
		self._cX = cX
		self._cY = cY
		self._cZ = cZ
	
	def rotateX(self, angleX) :
		
		cosX = math.cos(angleX)
		sinX = math.sin(angleX)
		
		y1 = self._y * cosX - self._z * sinX
		z1 = self._z * cosX + self._y * sinX
		
		self._y = y1
		self._z = z1

	def rotateY(self, angleY) :
		cosY = math.cos(angleY)
		sinY = math.sin(angleY)
		
		x1 = self._x * cosY - self._z * sinY
		z1 = self._z * cosY + self._x * sinY
		
		self._x = x1
		self._z = z1
	
	def rotateZ(self, angleZ) :
		cosZ = math.cos(angleZ)
		sinZ = math.sin(angleZ)
		
		x1 = self._x * cosZ - self._y * sinZ
		y1 = self._y * cosZ + self._x * sinZ
		
		self._x = x1
		self._y = y1

	@property
	def screenX(self) :
		scale = self._fl / (self._fl + self._z + self._cZ)
		return self._vpX + (self._cX + self._x) * scale

	@property
	def screenY(self) :
		scale = self._fl / (self._fl + self._z + self._cZ)
		return self._vpY + (self._cY + self._y) * scale
	
	@property
	def x(self) :
		return self._x

	@property
	def color(self) :
		return self._color

	@x.setter
	def x(self, x) :
		self._x = x
	
	@property
	def y(self) :
		return self._y

	@y.setter
	def y(self, y) :
		self._y = y

	@property
	def z(self) :
		return self._z

	@z.setter
	def z(self, z) :
		self._z = z
	
	@color.setter
	def color(self, color) :
		self._color = color