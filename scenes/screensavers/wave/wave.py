import math
from random import randint, random
from .point3d import Point3D
from .triangle import Triangle
from .light import Light

WAVE_COLOR = (randint(200,255),randint(200,255),randint(200,255)) #(50,200,252)
BASE_COLOR = (randint(0,255),randint(0,255),randint(0,255)) #(88,99,252)

WAVE_RES = 33 #odd number please

BASE_HEIGHT = 80
BASE_WIDTH = 550
BASE_DEPTH = 150

WAVE_HEIGHT_MIN = 2
WAVE_HEIGHT_MAX = 85

#SIN256_DATA = [-1, 3, 6, 9, 12, 15, 18, 21, 24, 28,31, 34, 37, 40, 43, 46, 48, 51, 54, 57, 60, 63, 65, 68, 71, 73, 76, 78, 81, 83,85, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 109, 111, 112, 114, 115,117, 118, 119, 120, 121, 122, 123, 124, 124, 125, 126, 126, 127, 127, 127, 127,127, 127, 127, 127, 127, 127, 127, 126, 126, 125, 124, 124, 123, 122, 121, 120,119, 118, 117, 115, 114, 112, 111, 109, 108, 106, 104, 102, 100, 98, 96, 94, 92,90, 88, 85, 83, 81, 78, 76, 73, 71, 68, 65, 63, 60, 57, 54, 51, 48, 46, 43, 40,37, 34, 31, 28, 24, 21, 18, 15, 12, 9, 6, 3, 0, -4, -7, -10, -13, -16, -19, -22,-25, -29, -32, -35, -38, -41, -44, -47, -49, -52, -55, -58, -61, -64, -66, -69,-72, -74, -77, -79, -82, -84, -86, -89, -91, -93, -95, -97, -99, -101, -103,-105, -107, -109, -110, -112, -113, -115, -116, -118, -119, -120, -121, -122,-123, -124, -125, -125, -126, -127, -127, -128, -128, -128, -128, -128, -128,-128, -128, -128, -128, -128, -127, -127, -126, -125, -125, -124, -123, -122,-121, -120, -119, -118, -116, -115, -113, -112, -110, -109, -107, -105, -103,-101, -99, -97, -95, -93, -91, -89, -86, -84, -82, -79, -77, -74, -72, -69, -66,-64, -61, -58, -55, -52, -49, -47, -44, -41, -38, -35, -32, -29, -25, -22, -19,-16, -13, -10, -7, -4]
#SAW256_DATA = [-128, -127, -126, -125, -124, -123, -122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,  20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 53, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
#WAVE_WIDTH_MIN = 55
WAVE_WIDTH_MAX = 105

#WIRE_FRAME = True

sinAscDesc = 1
sinVal = 0
sinValLast = 0
sinCount = 0

BASE_TOP = 135
BASE_BOTTOM = BASE_TOP + BASE_HEIGHT
BASE_LEFT = 0 - BASE_WIDTH /2
BASE_RIGHT = BASE_WIDTH / 2
BASE_FRONT = -50 - BASE_DEPTH / 2
BASE_BACK = BASE_DEPTH / 2
BASE_MIDDLE = BASE_WIDTH / 2 - WAVE_WIDTH_MAX / 2

def sineFrequency():
	return .03 + random() * .1

def triFrequency():
	return .01 + random() * .04

WAVE_PATTERNS = [
	{
		"type": 'sine',
		"initialPlot": 2,
		"frequencyFunction": sineFrequency,
		"frequency": sineFrequency(),
		"interval": 21,
	},
	{
		"type": 'triangle',
		"initialPlot": 3,
		"frequencyFunction": triFrequency,
		"frequency": triFrequency(),
		"interval": 9
	}
]

class Wave():
	def __init__(self, window, batch) :

		self.window = window
		self.batch = batch

		print('wave init with {}'.format(self.batch))

		self.base_points = [0] * 8
		self.base_triangles = [0] * 6
		self.wave_points = []
		self.wave_triangles = []
		self.face_triangles = []

		self.fl = 500
		self.vpX = 400
		self.vpY = 100

		self.view_angle_x = 0
		self.view_angle_y = 0 #-math.pi/8
		self.view_angle_z = 0

		self.curve_alpha = randint(2,5)
		self.wave_width = WAVE_WIDTH_MAX
		self.wave_height = 0
		self.wave_x = 0
		self.wave_vx = 0
		
		self.cos_y = math.cos(self.view_angle_y)
		self.sin_y = math.sin(self.view_angle_y)

		self.lightAngle = 0
		self.lightRadius = BASE_WIDTH/2 + 10
		self.lightVx = 0.0125
		self.light = self.initLight()

		self.intervals = 0

		self.wave_pattern_idx = randint(0, len(WAVE_PATTERNS) - 1)

		sinCount = WAVE_PATTERNS[self.wave_pattern_idx]["initialPlot"]

		self.initBase()

		self.initWave()

	"""
	loopDisplay
	"""
	def loopDisplay(self) :
		self.incrementCounter()

		self.computeWave()

		self.computeLight()

		self.eraseWave()

		self.renderBase()

		self.renderWave()

		#self.light.draw()

	"""
	initLight
	"""
	def initLight(self) :
		light = Light(BASE_RIGHT + 50, BASE_TOP - WAVE_HEIGHT_MAX, -50, 1, window=self.window)
		light.point.setVanishingPoint(self.vpX, self.vpY)
		light.point.setCenter(0, 0, BASE_DEPTH / 2)
		return light

	"""
	initBase
	"""
	def initBase(self) :
		
		self.base_points[0] = Point3D( BASE_LEFT,  BASE_TOP, BASE_FRONT,     fl=self.fl)
		self.base_points[1] = Point3D( BASE_RIGHT, BASE_TOP, BASE_FRONT,     fl=self.fl)
		self.base_points[2] = Point3D( BASE_RIGHT, BASE_BOTTOM, BASE_FRONT,  fl=self.fl)
		self.base_points[3] = Point3D( BASE_LEFT,  BASE_BOTTOM, BASE_FRONT,  fl=self.fl)
		self.base_points[4] = Point3D( BASE_LEFT,  BASE_TOP,  BASE_BACK,    fl=self.fl)
		self.base_points[5] = Point3D( BASE_RIGHT, BASE_TOP,  BASE_BACK,    fl=self.fl)
		self.base_points[6] = Point3D( BASE_RIGHT, BASE_BOTTOM,  BASE_BACK, fl=self.fl)
		self.base_points[7] = Point3D( BASE_LEFT,  BASE_BOTTOM,  BASE_BACK, fl=self.fl)

		for point in self.base_points:
			point.setVanishingPoint(self.vpX, self.vpY)
			point.setCenter(0, 0, BASE_DEPTH / 2)
			# point.rotateX(self.view_angle_x)
			# point.rotateY(self.view_angle_y)
			# point.rotateZ(self.view_angle_z)
		
		self.base_triangles[0] = Triangle(self.base_points[0],   self.base_points[1],  self.base_points[3], color=BASE_COLOR, batch=self.batch, window=self.window, light=self.light)
		self.base_triangles[1] = Triangle(self.base_points[1],   self.base_points[2],  self.base_points[3], color=BASE_COLOR, batch=self.batch, window=self.window, light=self.light)
		self.base_triangles[2] = Triangle(self.base_points[4],   self.base_points[5],  self.base_points[0], color=WAVE_COLOR, batch=self.batch, window=self.window, light=self.light)
		self.base_triangles[3] = Triangle(self.base_points[5],   self.base_points[1],  self.base_points[0], color=WAVE_COLOR, batch=self.batch, window=self.window, light=self.light)
		self.base_triangles[4] = Triangle(self.base_points[1],   self.base_points[5],  self.base_points[2], color=BASE_COLOR, batch=self.batch, window=self.window, light=self.light)
		self.base_triangles[5] = Triangle(self.base_points[5],   self.base_points[6],  self.base_points[2], color=BASE_COLOR, batch=self.batch, window=self.window, light=self.light)

	"""
	renderBase
	"""
	def renderBase(self) :
		for tri in self.base_triangles:
			tri.draw()
	
	"""
	initWave
	"""
	def initWave(self) :
		for i in range(WAVE_RES * 2 + 3) :
			self.wave_points.append( Point3D(0,0,0, self.fl) )

		# front center bottom point
		self.wave_points[0].x = self.wave_vx
		self.wave_points[0].y = BASE_BOTTOM - 3
		self.wave_points[0].z = BASE_FRONT
		
		# back center bottom point
		self.wave_points[1].x = self.wave_vx
		self.wave_points[1].y = BASE_BOTTOM - 3
		self.wave_points[1].z = BASE_BACK
		
		self.setWaveEdge()
		
		for point in self.wave_points:
			point.setVanishingPoint(self.vpX, self.vpY)
			point.setCenter(0, 0, BASE_DEPTH / 2)
			# point.rotateX(self.view_angle_x)
			# point.rotateY(self.view_angle_y)
			# point.rotateZ(self.view_angle_z)
		
		# front triangles
		for i in range( WAVE_RES - 1) :
			tri = Triangle(
				self.wave_points[0],
				self.wave_points[2 + i],
				self.wave_points[3 + i],
				color=BASE_COLOR,
				batch=self.batch,
				window=self.window,
				light=self.light
			)
			#tri.debug = True
			self.face_triangles.append( tri )

		# back triangles
		for i in range( WAVE_RES - 1) :
			tri = Triangle(
				self.wave_points[1],
				self.wave_points[WAVE_RES * 2 + 1 - i],
				self.wave_points[WAVE_RES * 2 - i],
				color=BASE_COLOR,
				batch=self.batch,
				window=self.window,
				light=self.light
			)
			#tri.debug = True
			self.face_triangles.append( tri )

		# edge triangles
		for i in range( WAVE_RES ) :
			self.wave_triangles.append( Triangle(
				self.wave_points[2 + i],
				self.wave_points[2 + WAVE_RES + i],
				self.wave_points[3 + i],
				color=WAVE_COLOR,
				batch=self.batch,
				window=self.window,
				light=self.light
			) )
			self.wave_triangles.append( Triangle(
				self.wave_points[3 + i],
				self.wave_points[2 + WAVE_RES + i],
				self.wave_points[3 + WAVE_RES + i],
				color=WAVE_COLOR,
				batch=self.batch,
				window=self.window,
				light=self.light
			) )
		
		# top
		#self.wave_triangles.append( Triangle(self.wave_points[2+WAVE_RES-1], self.wave_points[2+WAVE_RES*2-1], self.base_points[1], color=WAVE_COLOR, batch=self.batch ) )
		#self.wave_triangles.append( Triangle(self.base_points[1], self.wave_points[2+WAVE_RES*2-1], self.base_points[5], color=WAVE_COLOR, batch=self.batch ) )

	"""
	computeWave
	"""
	def computeWave(self) :
		self.setWaveHeightAndX()

		self.wave_points[0].x = self.wave_vx
		self.wave_points[0].y = BASE_BOTTOM - 3
		self.wave_points[0].z = BASE_FRONT

		self.wave_points[1].x = self.wave_vx
		self.wave_points[1].y = BASE_BOTTOM - 3
		self.wave_points[1].z = BASE_BACK

		self.setWaveEdge()

		# for point in self.wave_points:
		# 	point.setVanishingPoint(self.vpX, self.vpY)
		# 	point.setCenter(0, 0, BASE_DEPTH / 2)
		# 	point.rotateX(self.view_angle_x)
		# 	point.rotateY(self.view_angle_y)
		# 	point.rotateZ(self.view_angle_z)

		return 1

	"""
	computeLight
	"""
	def computeLight(self) :
		newX = 0 + math.sin(self.lightAngle) * self.lightRadius
		newY = BASE_TOP + BASE_HEIGHT/2 + math.cos(self.lightAngle) * self.lightRadius
		self.lightAngle = self.lightAngle + self.lightVx
		self.light.setPoint(newX, newY, self.light.z)

	def incrementCounter(self) :
		global sinCount
		global sinValLast
		global sinVal

		sv = None

		pattern = WAVE_PATTERNS[self.wave_pattern_idx]

		sinCount = sinCount + pattern["frequency"]

		if ( sinCount >= pattern["interval"] ) :
			sinCount = pattern["initialPlot"]
			self.doColorChange()
			self.checkChangeWaveType()

		if (pattern["type"] == "triangle") :
			sv = abs(pow((1 - abs((sinCount % 4) - 2)), 4)) * 128
		else:
			#sv = SIN256_DATA[sinCount]
			sv = math.sin(sinCount) * 128

		sinValLast = sinVal
		sinVal = sv
	
	def checkChangeWaveType(self):
		global sinCount

		self.intervals = self.intervals + 1

		if (self.intervals < 3) :
			return

		if (random() < .5) :
			rand = True
		else :
			rand = False

		if (rand is True) :

			self.intervals = 0

			self.wave_pattern_idx = self.wave_pattern_idx + 1
			if (self.wave_pattern_idx >= len(WAVE_PATTERNS)) :
				self.wave_pattern_idx = 0

			pattern = WAVE_PATTERNS[self.wave_pattern_idx]

			pattern["frequency"] = pattern["frequencyFunction"]()

			sinCount = pattern["initialPlot"]

	def setWaveHeightAndX(self) :
		global sinVal
		global sinAscDesc
		pattern = WAVE_PATTERNS[self.wave_pattern_idx]
		
		if (pattern["type"] == "triangle") :
			self.wave_height = rangeMap(abs(sinVal), 0, 128, WAVE_HEIGHT_MIN, WAVE_HEIGHT_MAX * .5)

			if (sinVal > sinValLast) :
				sinAscDesc = 1
			elif (sinVal < sinValLast) :
				sinAscDesc = -1

			map = BASE_MIDDLE + (abs(sinVal) / 128) * (0 - BASE_MIDDLE)

			self.wave_x = BASE_LEFT + BASE_MIDDLE - sinAscDesc * map
			self.wave_vx = self.wave_x + math.ceil(((self.wave_width / WAVE_RES) * (WAVE_RES / 2)))
			return

		self.wave_height = rangeMap( sinVal, -127, 127, WAVE_HEIGHT_MAX, WAVE_HEIGHT_MIN )
		self.wave_x = rangeMap( sinVal, 127, -127, BASE_RIGHT - self.wave_width, BASE_LEFT )
		self.wave_vx = self.wave_x + math.ceil( ( ( self.wave_width / WAVE_RES ) * ( WAVE_RES / 2 ) ) )

	def setWaveEdge(self) :
		pattern = WAVE_PATTERNS[self.wave_pattern_idx]
		
		wave_vx = self.wave_vx

		if (pattern["type"] == "triangle") :
			for i in range(WAVE_RES) :
				if ( i <= WAVE_RES / 2 ) :
					inc = ( wave_vx - self.wave_x ) / ( ( WAVE_RES - 1 ) / 2 )
					px = math.ceil( self.wave_x + inc * i )
				else :
					inc = ((self.wave_width - (wave_vx - self.wave_x)) / ((WAVE_RES - 1) / 2)) * rangeMap(wave_vx, BASE_LEFT, BASE_LEFT + BASE_WIDTH, 1, .3)
					px = math.ceil( wave_vx + inc * ( i - ( ( WAVE_RES - 1 ) / 2 ) ) )
				
				if (i >= 1 and i <= WAVE_RES-2) :
					if (i <= WAVE_RES / 2) :
						curve_alpha = self.curve_alpha
						curve_pct =  ( self.wave_x - px ) / ( self.wave_x - ( self.wave_x + self.wave_width ) )
						py = math.ceil( BASE_TOP - math.pow( 4, curve_alpha ) * math.pow( ( curve_pct * ( 1.00 - curve_pct ) ), curve_alpha ) * self.wave_height )
					else:
						curve_alpha = rangeMap(self.wave_vx, BASE_LEFT, BASE_LEFT + BASE_WIDTH, 0, 10)
						curve_pct = i / (WAVE_RES - 2)
						py = math.ceil( BASE_TOP - math.pow( 4, curve_alpha ) * math.pow( ( curve_pct * ( 1.00 - curve_pct ) ), curve_alpha ) * self.wave_height )
				else :
					py = BASE_TOP #int( BASE_TOP - ( math.sin( ( i / ( WAVE_RES - 1 ) ) * math.pi ) * self.wave_height ) )
				
				# front edge points
				self.wave_points[2+i].x = px
				self.wave_points[2+i].y = py
				self.wave_points[2+i].z = BASE_FRONT
				#back edge points
				self.wave_points[2+WAVE_RES+i].x = px
				self.wave_points[2+WAVE_RES+i].y = py
				self.wave_points[2+WAVE_RES+i].z = BASE_BACK
		else :
			for i in range(WAVE_RES) :
				if ( i <= WAVE_RES / 2 ) :
					inc = ( wave_vx - self.wave_x ) / ( ( WAVE_RES - 1 ) / 2 )
					px = math.ceil( self.wave_x + inc * i )
				else :
					inc = ( self.wave_width - ( wave_vx - self.wave_x ) ) / ( ( WAVE_RES -1 ) / 2 )
					px = math.ceil( wave_vx + inc * ( i - ( ( WAVE_RES - 1 ) / 2 ) ) )
				
				if (i >= 1 and i <= WAVE_RES-2) :
					curve_pct =  ( self.wave_x - px ) / ( self.wave_x - ( self.wave_x + self.wave_width ) )
					py = math.ceil( BASE_TOP - math.pow( 4, self.curve_alpha ) * math.pow( ( curve_pct * ( 1.00 - curve_pct ) ), self.curve_alpha ) * self.wave_height )
				else :
					py = BASE_TOP #int( BASE_TOP - ( math.sin( ( i / ( WAVE_RES - 1 ) ) * math.pi ) * self.wave_height ) )
				
				# front edge points
				self.wave_points[2+i].x = px
				self.wave_points[2+i].y = py
				self.wave_points[2+i].z = BASE_FRONT
				#back edge points
				self.wave_points[2+WAVE_RES+i].x = px
				self.wave_points[2+WAVE_RES+i].y = py
				self.wave_points[2+WAVE_RES+i].z = BASE_BACK

	def eraseWave(self) :
		for tri in self.wave_triangles:
			self.window.fill(0, tri.render)

	"""
	renderWave
	"""
	def renderWave(self, firstRun=False) :
		for tri in self.wave_triangles:
			tri.draw()

		self.renderFace()

	"""
	renderFace
	"""
	def renderFace(self) :
		for tri in self.face_triangles:
			tri.draw()

	"""
	doColorChange
	"""
	def doColorChange(self) :
		base_color = (randint(200,255),randint(200,255),randint(200,255))
		wave_color = (randint(0,255),randint(0,255),randint(0,255))
		for tri in self.base_triangles :
			tri.color = base_color
		for tri in self.wave_triangles :
			tri.color = wave_color
		for tri in self.face_triangles :
			tri.color = base_color
		self.base_triangles[2].color = wave_color
		self.base_triangles[3].color = wave_color

"""
isBackFace
"""
def isBackFace(asx, asy, bsx, bsy, csx, csy) :
	
	# see http://www.jurjans.lv/flash/shape.html
	
	cax = csx - asx
	cay = csy - asy
	
	bcx = bsx - csx
	bcy = bsy - csy
	
	return cax * bcy > cay * bcx

def RGB565CONVERT(r, g, b) :
	#long RGB565
	RGB565=(((r&0xF8)<<8)|((g&0xFC)<<3)|((b&0xF8)>>3))
	return RGB565

def RGB888_to_RGB565 (rgb) :
	#long RGB565
	RGB565= (((rgb >> 19) & 0x1f) << 11)|(((rgb >> 10) & 0x3f) <<  5)|(((rgb >>  3) & 0x1f))
	return RGB565

def getHighlight(base_color) :
	
	r = base_color >> 16
	g = base_color >>  8
	b = base_color
	#wr, wg, wb
		
	wr = (r * 210) >> 8
	wg = (g * 210) >> 8
	wb = (b * 210) >> 8
	
	return (wr,wg,wb) #return RGB565CONVERT(wr,wg,wb)

def populateWaveColors(wave_color) :
	
	r = wave_color[0] #(wave_color >> 16)
	g = wave_color[1] #(wave_color >>  8)
	b = wave_color[2] #wave_color
	#wr, wg, wb
	#uint16_t wc
	#int i
	
	for i in range( int( WAVE_TRIANGLES_TOTAL/9 ) ) :

		wr = (r * (255-i*15)) >> 8
		wg = (g * (255-i*15)) >> 8
		wb = (b * (255-i*15)) >> 8
		
		wc = (abs(wr),abs(wg),abs(wb)) #RGB565CONVERT(wr,wg,wb)
		
		#print('populateWaveColors %d of %d: %s' % (i, int( WAVE_TRIANGLES_TOTAL/9 ), wc))
		
		wave_colors[i] = wc

def rangeMap(val, min1, max1, min2, max2):
	range1 = max1 - min1
	range2 = max2 - min2
	scale = float(val - min1) / float(range1)
	return min2 + (scale * range2)
