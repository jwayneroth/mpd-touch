import math
#import pyglet
import pygame

VIEW_ANGLE_Y = - (math.pi) / 6

VPX = 160
VPY = 70
FOCAL_LENGTH = 500

BASE_HEIGHT = 40
BASE_WIDTH = 250
BASE_DEPTH = 250

BASE_CENTER = BASE_DEPTH / 2
BASE_TOP = 100
BASE_BOTTOM = BASE_TOP + BASE_HEIGHT
BASE_LEFT = 0 - BASE_WIDTH /2 - 5
BASE_RIGHT = BASE_WIDTH / 2 + 30
BASE_FRONT = 0 - BASE_DEPTH / 2
BASE_BACK = BASE_DEPTH / 2

BASE_POINTS_TOTAL = 24
BASE_TRIANGLES_TOTAL = 54
BASE_LINES_TOTAL = int( BASE_TRIANGLES_TOTAL / 9 ) * 6 

RES = 13 # odd number please

WAVE_POINTS_TOTAL = ( RES * 2 + 1 ) * 3
WAVE_TRIANGLES_TOTAL = (( RES - 1 ) * 2 + 2 ) * 9
WAVE_LINES_TOTAL = int( WAVE_TRIANGLES_TOTAL / 9 ) * 6
FACE_TRIANGLES_TOTAL = ( RES - 1 ) * 9
FACE_LINES_TOTAL = ( RES - 1 ) * 6

BASE_COLOR = None
BASE_HIGHLIGHT_COLOR = None
WAVE_COLOR = None
BG_COLOR = None

wave_colors = [0] * int(WAVE_TRIANGLES_TOTAL/9)

WAVE_HEIGHT_MIN = 2
WAVE_HEIGHT_MAX = 60

WAVE_WIDTH_MIN = 30
WAVE_WIDTH_MAX = 65

WAVE_Y = BASE_TOP

cos_y = math.cos(VIEW_ANGLE_Y)
sin_y = math.sin(VIEW_ANGLE_Y)

base_left_slope = None
base_left_intercept = None
base_back_slope = None
base_back_intercept = None

wave_height = WAVE_HEIGHT_MAX
wave_width = WAVE_WIDTH_MAX
wave_x = BASE_LEFT
wave_x_last = 0

wave_points = [0] * WAVE_POINTS_TOTAL

wave_triangles = [0] * WAVE_TRIANGLES_TOTAL
face_triangles = [0] * FACE_TRIANGLES_TOTAL

wave_lines = [0] * WAVE_LINES_TOTAL
base_lines = [0] * BASE_LINES_TOTAL
face_lines = [0] * FACE_LINES_TOTAL

base_points = [
	BASE_LEFT,  BASE_TOP,    BASE_FRONT,    # pt0 0,1,2 x,y,z
	BASE_RIGHT, BASE_TOP,    BASE_FRONT,    # pt1 3,4,5
	BASE_RIGHT, BASE_BOTTOM, BASE_FRONT,    # pt2 6,7,8
	BASE_LEFT,  BASE_BOTTOM, BASE_FRONT,    # pt3 9,10,11
	BASE_LEFT,  BASE_TOP,    BASE_BACK,     # pt4 12,13,14
	BASE_RIGHT, BASE_TOP,    BASE_BACK,     # pt5 15,16,17
	BASE_RIGHT, BASE_BOTTOM, BASE_BACK,     # pt6 18,19,20
	BASE_LEFT,  BASE_BOTTOM, BASE_BACK      # pt7 21,22,23
]

base_triangles = [
	base_points[0],  base_points[1],  base_points[2],   # tri0 a pt0
	base_points[3],  base_points[4],  base_points[5],   # tri0 b pt1
	base_points[9],  base_points[10], base_points[11],  # tri0 c pt3
	
	base_points[3],  base_points[4],  base_points[5],   # tri1 a pt1
	base_points[6],  base_points[7],  base_points[8],   # tri1 b pt2
	base_points[9],  base_points[10], base_points[11],  # tri1 c pt3
	
	base_points[12], base_points[13], base_points[14],  # tri2 a pt4
	base_points[15], base_points[16], base_points[17],  # tri2 b pt5
	base_points[0],  base_points[1],  base_points[2],   # tri2 c pt0
	
	base_points[15], base_points[16], base_points[17],  # tri3 a pt5
	base_points[3],  base_points[4],  base_points[5],   # tri3 b pt1
	base_points[0],  base_points[1],  base_points[2],   # tri3 c pt0
	
	base_points[3],  base_points[4],  base_points[5],   # tri4 a pt1
	base_points[15], base_points[16], base_points[17],  # tri4 b pt5
	base_points[18], base_points[19], base_points[20],  # tri4 c pt6
	
	base_points[3],  base_points[4],  base_points[5],   # tri5 a pt1
	base_points[18], base_points[19], base_points[20],  # tri5 b pt6
	base_points[6],  base_points[7],  base_points[8]    # tri5 c pt2
]

HYSTERESIS = 10

last_ui_val = -HYSTERESIS

lfo_one_val = -127

class Wave():
	def __init__(self, window, batch) :

		self.window = window
		self.batch = batch

		print('wave init with {}'.format(self.batch))

		self.setupDisplay();

		return None

	"""
	setupDisplay
	"""
	def setupDisplay(self) :
		
		global BG_COLOR, BASE_COLOR, BASE_HIGHLIGHT_COLOR, WAVE_COLOR
		
		BG_COLOR = (159,167,203) #'#9fa7cb'                           #RGB888_to_RGB565(0x9fa7cb)
		BASE_COLOR = (0,172,153) #'#00ac98'                         #RGB888_to_RGB565(0x00ac98)
		BASE_HIGHLIGHT_COLOR = (129,172,152) #getHighlight((0,172,152)) #'#00ac98') #0x00ac98)
		WAVE_COLOR = (88,99,252) #'#5863fc'                         #RGB888_to_RGB565(0x5863fc)
		
		populateWaveColors((88,99,252)) #0x5863fc)
		
		cos_y = math.cos(VIEW_ANGLE_Y)
		sin_y = math.sin(VIEW_ANGLE_Y)
		
		self.base_renders = [0] * int( BASE_LINES_TOTAL / 6 ) * 4
		self.wave_renders = [0] * int( WAVE_TRIANGLES_TOTAL / 9 )
		self.face_renders = [0] * (RES - 1);

		#tft.begin()
		#tft.setRotation(3)
		#tft.fillScreen(BG_COLOR)
		#tft.setTextSize(1)
		#tft.setTextColor(ILI9341_WHITE)
		
		self.initWave()
		
		self.initBase()

		#self.renderBase()
		
		#self.renderWave(True)

	"""
	loopDisplay
	"""
	def loopDisplay(self) :
		
		self.computeWave()

		#if ( self.computeWave() ) :
			
		#tft.fillScreen(BG_COLOR)
		
		#checkTestUI()
		
		#eraseWave()
		
		self.renderWave()
		
		self.renderBase()

	"""
	initBase
	"""
	def initBase(self) :
		
		#int i,pax,pay,paz,pbx,pby,pbz,pcx,pcy,pcz,ax,ay,bx,by,cx,cy
		#float scaleA,scaleB,scaleC
		
		for i in range( int( BASE_TRIANGLES_TOTAL / 9 ) ) :
			
			pax = base_triangles[i * 9 + 0] * cos_y - base_triangles[i * 9 + 2] * sin_y
			pay = base_triangles[i * 9 + 1]
			paz = base_triangles[i * 9 + 2] * cos_y + base_triangles[i * 9 + 0] * sin_y
			
			pbx = base_triangles[i * 9 + 3] * cos_y - base_triangles[i * 9 + 5] * sin_y
			pby = base_triangles[i * 9 + 4]
			pbz = base_triangles[i * 9 + 5] * cos_y + base_triangles[i * 9 + 3] * sin_y
			
			pcx = base_triangles[i * 9 + 6] * cos_y - base_triangles[i * 9 + 8] * sin_y
			pcy = base_triangles[i * 9 + 7]
			pcz = base_triangles[i * 9 + 8] * cos_y + base_triangles[i * 9 + 6] * sin_y
			
			scaleA = FOCAL_LENGTH / ( FOCAL_LENGTH + paz + BASE_CENTER )
			scaleB = FOCAL_LENGTH / ( FOCAL_LENGTH + pbz + BASE_CENTER )
			scaleC = FOCAL_LENGTH / ( FOCAL_LENGTH + pcz + BASE_CENTER )
			
			ax = int(VPX + pax * scaleA)
			ay = int(VPY + pay * scaleA)
			
			bx = int(VPX + pbx * scaleB)
			by = int(VPY + pby * scaleB)
			
			cx = int(VPX + pcx * scaleC)
			cy = int(VPY + pcy * scaleC)
			
			base_lines[i* 6 + 0] = ax
			base_lines[i* 6 + 1] = ay
			base_lines[i* 6 + 2] = bx
			base_lines[i* 6 + 3] = by
			base_lines[i* 6 + 4] = cx
			base_lines[i* 6 + 5] = cy
		
		base_left_slope = (base_lines[13] - base_lines[1]) / (base_lines[12] - base_lines[0])
		
		base_left_intercept = base_left_slope * base_lines[0] - base_lines[1]
		
		base_back_slope = (base_lines[15] - base_lines[13]) / (base_lines[14] - base_lines[12])
		
		base_back_intercept = base_back_slope * base_lines[12] - base_lines[13]

	"""
	renderBase
	"""
	def renderBase(self) :
		#int i, ax, ay, bx, by, cx, cy
		#uint16_t color
		
		for i in range( int( BASE_LINES_TOTAL / 6 ) ) :
			ax = base_lines[i* 6 + 0]
			ay = base_lines[i* 6 + 1]
			bx = base_lines[i* 6 + 2]
			by = base_lines[i* 6 + 3]
			cx = base_lines[i* 6 + 4]
			cy = base_lines[i* 6 + 5]
			
			#color = BASE_HIGHLIGHT_COLOR if ( i > int( BASE_LINES_TOTAL / 6 ) - 4 ) else BASE_COLOR
			
			if ( i > int( BASE_LINES_TOTAL / 6 ) - 4 ) :
				color = BASE_HIGHLIGHT_COLOR
			else :
				color = BASE_COLOR
			
			#print('pyglet.shapes.Triangle({}, {}, {}, {}, {}, {}, color={}, batch=self.batch)'.format(ax, ay, bx, by, cx, cy, color))

			# self.base_renders[i*4+0] = pyglet.shapes.Triangle(ax, ay, bx, by, cx, cy, color=color, batch=self.batch)
			
			# self.base_renders[i*4+1] = pyglet.shapes.Line(ax, ay, bx, by, color=BASE_COLOR, batch=self.batch)
			# self.base_renders[i*4+2] = pyglet.shapes.Line(bx, by, cx, cy, color=BASE_COLOR, batch=self.batch)
			# self.base_renders[i*4+3] = pyglet.shapes.Line(cx, cy, ax, ay, color=BASE_COLOR, batch=self.batch)
			
			self.base_renders[i*4+0] = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)
			# self.base_renders[i*4+0] = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)
			# self.base_renders[i*4+0] = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)
			# self.base_renders[i*4+0] = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)

	"""
	initWave
	TODO: simplify  - this is only used to fill the arrays and set up triangle references AND point z-indices
	"""
	def initWave(self) :
		
		"""
		int i
		int px
		int py
		int ti
		
		float inc
		int tsx
		"""

		wave_cx = wave_x + wave_width/2

		# front center
		wave_points[0] = wave_cx    # pt0 x
		wave_points[1] = WAVE_Y     # pt0 y
		wave_points[2] = BASE_FRONT # pt0 z

		# points on the edge, front and back
		for i in range(RES) :

			if( i <= (RES-1) / 2 ) :
				inc = ( wave_cx - wave_x ) / (( RES - 1 ) / 2 )
				px = wave_x + inc * i
			else :
				inc = ( wave_width - ( wave_cx - wave_x )) / (( RES -1 ) / 2 )
				px = wave_cx + inc * ( i - ((RES-1)/2) )
			
			py = WAVE_Y - (math.sin((i/(RES-1))  * 3.14)) * wave_height
			
			# front edge
			wave_points[3 + i * 3 + 0] = px                # pt(2 + 2 * i) x
			wave_points[3 + i * 3 + 1] = py                # pt(2 + 2 * i) y
			wave_points[3 + i * 3 + 2] = BASE_FRONT        # pt(2 + 2 * i) z
			
			# back edge
			wave_points[3 + RES * 3 + 0 + i * 3] = px        # pt(3 + 2 * i) x
			wave_points[3 + RES * 3 + 1 + i * 3] = py        # pt(3 + 2 * i) y
			wave_points[3 + RES * 3 + 2 + i * 3] = BASE_BACK # pt(3 + 2 * i) z
		
		"""
		for(i=0i<(WAVE_POINTS_TOTAL/3)i++) :
			Serial.print(i)
			Serial.print("\t x: ")Serial.print(wave_points[i * 3 + 0])
			Serial.print("\t y: ")Serial.print(wave_points[i * 3 + 1])
			Serial.print("\t z: ")Serial.println(wave_points[i * 3 + 2])
		"""
		
		# front triangles
		for i in range(RES - 1) :
			# a
			face_triangles[i * 9 + 0] = wave_points[0]            # pt0 x
			face_triangles[i * 9 + 1] = wave_points[1]            # pt0 y
			face_triangles[i * 9 + 2] = wave_points[2]            # pt0 z
			# b
			face_triangles[i * 9 + 3] = wave_points[3 + i* 3 + 0] # pt2 + i x
			face_triangles[i * 9 + 4] = wave_points[3 + i* 3 + 1] # pt2 + i y
			face_triangles[i * 9 + 5] = wave_points[3 + i* 3 + 2] # pt2 + i z
			# c
			face_triangles[i * 9 + 6] = wave_points[3 + i* 3 + 3] # pt3 + i
			face_triangles[i * 9 + 7] = wave_points[3 + i* 3 + 4] # pt3 + i
			face_triangles[i * 9 + 8] = wave_points[3 + i* 3 + 5] # pt3 + i
		
		tsx =  int( 3 + ((RES - 1)/2) * 3 )
		
		# edge triangles
		for i in range( int( (RES - 1) / 2 ) ) :
			
			#wave_triangles[] = wave_points[2 + i], wave_points[2 + RES + i], wave_points[3 + i]
			#wave_triangles[] = wave_points[3 + i], wave_points[2 + RES + i], wave_points[3 + RES + i]

			# a
			wave_triangles[ i * 18 + 0] =  wave_points[tsx + i* 3 + 0]               # pt 2+i
			wave_triangles[ i * 18 + 1] =  wave_points[tsx + i* 3 + 1]
			wave_triangles[ i * 18 + 2] =  wave_points[tsx + i* 3 + 2]
			# b
			wave_triangles[ i * 18 + 3] =  wave_points[tsx + RES* 3 + i* 3 + 0]      # pt 2 + RES + i
			wave_triangles[ i * 18 + 4] =  wave_points[tsx + RES* 3 + i* 3 + 1] 
			wave_triangles[ i * 18 + 5] =  wave_points[tsx + RES* 3 + i* 3 + 2] 
			# c
			wave_triangles[ i * 18 + 6] =  wave_points[tsx + 3 + i* 3 + 0]           # pt 3+i
			wave_triangles[ i * 18 + 7] =  wave_points[tsx + 3 + i* 3 + 1] 
			wave_triangles[ i * 18 + 8] =  wave_points[tsx + 3 + i* 3 + 2] 
			
			# a
			wave_triangles[ i * 18 + 9] =  wave_points[tsx + 3 + i* 3 + 0]           # pt 3+i 
			wave_triangles[ i * 18 + 10] = wave_points[tsx + 3 + i* 3 + 1]
			wave_triangles[ i * 18 + 11] = wave_points[tsx + 3 + i* 3 + 2]
			#b
			wave_triangles[ i * 18 + 12] = wave_points[tsx + RES* 3 + i* 3 + 0]      # pt 2 + RES + i
			wave_triangles[ i * 18 + 13] = wave_points[tsx + RES* 3 + i* 3 + 1] 
			wave_triangles[ i * 18 + 14] = wave_points[tsx + RES* 3 + i* 3 + 2] 
			#c
			wave_triangles[ i * 18 + 15] = wave_points[tsx + 3 + RES* 3 + i* 3 + 0]  # pt 3 + RES + i
			wave_triangles[ i * 18 + 16] = wave_points[tsx + 3 + RES* 3 + i* 3 + 1] 
			wave_triangles[ i * 18 + 17] = wave_points[tsx + 3 + RES* 3 + i* 3 + 2]
		
		# base top right of wave ( two triangles )
		ti = (RES - 2) * 18 + 18
		
		#wave_triangles.push( new Triangle( wave_points[2+RES-1],      wave_points[2+RES*2-1], base_points[1], BASE_COLOR ))
		#wave_triangles.push( new Triangle( base_points[1],            wave_points[2+RES*2-1], base_points[5], BASE_COLOR ))
		
		#a
		wave_triangles[ti + 0] =  wave_points[3 + (RES-2)* 3 + 3]
		wave_triangles[ti + 1] =  wave_points[3 + (RES-2)* 3 + 4]
		wave_triangles[ti + 2] =  wave_points[3 + (RES-2)* 3 + 5]
		#b
		wave_triangles[ti + 3] =  wave_points[6 + RES* 3 + (RES-2)* 3 + 0]
		wave_triangles[ti + 4] =  wave_points[6 + RES* 3 + (RES-2)* 3 + 1]
		wave_triangles[ti + 5] =  wave_points[6 + RES* 3 + (RES-2)* 3 + 2]
		#c
		wave_triangles[ti + 6] =  base_points[3]
		wave_triangles[ti + 7] =  base_points[4]
		wave_triangles[ti + 8] =  base_points[5]
		
		#a
		wave_triangles[ti + 9] =  base_points[3]
		wave_triangles[ti + 10] = base_points[4]
		wave_triangles[ti + 11] = base_points[5]
		#b
		wave_triangles[ti + 12] = wave_points[6 + RES* 3 + (RES-2)* 3 + 0]
		wave_triangles[ti + 13] = wave_points[6 + RES* 3 + (RES-2)* 3 + 1]
		wave_triangles[ti + 14] = wave_points[6 + RES* 3 + (RES-2)* 3 + 2]
		#c
		wave_triangles[ti + 15] = base_points[15]
		wave_triangles[ti + 16] = base_points[16]
		wave_triangles[ti + 17] = base_points[17]
		
		for i in range(WAVE_LINES_TOTAL) :
			wave_lines[i] = -1

	"""
	computeWave
	"""
	def computeWave(self) :
		
		global wave_x, lfo_one_val, wave_points, wave_lines, WAVE_Y, wave_height, wave_width, BASE_RIGHT, BASE_LEFT

		#int i, point_y, line_x, width_max
		#float curve_alpha, curve_pct, inc
		#int i, px, py, wave_cx, wx
		
		lfo_one_val = lfo_one_val + 1 if ( lfo_one_val < 127 ) else -127

		#print('lfo {}'.format(lfo_one_val))

		curve_alpha = 2.5
		
		#width_max = map( drone1.getFrequency(), 100, 2000, 80, 20 )
		
		#wave_height = map( drone1.getAmp(), 0, 200, WAVE_HEIGHT_MAX, 0 )
		
		wave_height = rangeMap( lfo_one_val, -127, 127, WAVE_HEIGHT_MAX, WAVE_HEIGHT_MIN )
		
		#wave_width = map( lfo_one_val, -128, 128, WAVE_WIDTH_MAX, WAVE_WIDTH_MIN  )
		
		#make sure wave_width is divisible by two
		#if(wave_width % 2) wave_width ++
		
		wx = rangeMap( lfo_one_val, 128, -128, BASE_RIGHT - wave_width, BASE_LEFT ) #wave_x = map( lfo_one_val, 127, -127, 128 - wave_width, 0 )
		
		#if(abs(wx - wave_x_last) < 2) return 0
		
		wave_x_last = wave_x
		
		wave_x = wx
		
		#curve_alpha = map( wave_x, BASE_LEFT, BASE_RIGHT - wave_width, 5.0, 2.0)
			
		wave_cx = int( wave_x + wave_width/2 ) #(( wave_width / RES ) * ( RES / 2 )) // - wave_center_offset
		
		wave_points[0] = wave_cx
		wave_points[1] = WAVE_Y
		
		for i in range(RES) :
			
			if ( i <= (RES-1) / 2 ) :
				inc = ( wave_cx - wave_x ) / (( RES - 1 ) / 2 )
				px = int (wave_x + inc * i )
			else :
				inc = ( wave_width - ( wave_cx - wave_x )) / (( RES -1 ) / 2 )
				px = int (wave_cx + inc * ( i - ((RES-1)/2) ) )
			
			curve_pct =  max(0, min( 1, ( wave_x - px ) / ( wave_x - ( wave_x + wave_width ) ) ) )
			
			#py = WAVE_Y - (sin((i/(RES-1))  * 3.14)) * wave_height
			
			py1 = pow( ( curve_pct * ( 1.00 - curve_pct ) ), curve_alpha )
			py2 = pow( 4.00, curve_alpha ) * py1 * wave_height
			
			#print('curve_pct: {} curve_alpha: {} 1: {} 2: {}'.format(curve_pct,curve_alpha,py1,py2))
			
			py = int( WAVE_Y - py2 )
			
			# front edge
			wave_points[3 + i * 3 + 0] = px
			wave_points[3 + i * 3 + 1] = py
			
			# back edge
			wave_points[3 + RES * 3 + i* 3 + 0] = px
			wave_points[3 + RES * 3 + i* 3 + 1] = py
		
		# front edge
		wave_points[3 + (RES-1) * 3 + 1] = WAVE_Y
			
		# back edge
		wave_points[3 + RES * 3 + (RES-1)* 3 + 1] = WAVE_Y
		
		return 1

	"""
	renderWave
	"""
	def renderWave(self, firstRun=False) :
		
		"""
		int i,pax,pay,paz,pbx,pby,pbz,pcx,pcy,pcz,ax,ay,bx,by,cx,cy
		float scaleA, scaleB, scaleC
		uint16_t color
		"""

		#print('renderWave {}'.format(firstRun))

		for i in range( int( WAVE_TRIANGLES_TOTAL / 9 ) ) :

			pax = wave_triangles[i* 9 + 0] * cos_y - wave_triangles[i * 9 + 2] * sin_y
			pay = wave_triangles[i* 9 + 1]
			paz = wave_triangles[i* 9 + 2] * cos_y + wave_triangles[i * 9 + 0] * sin_y
			
			pbx = wave_triangles[i* 9 + 3] * cos_y - wave_triangles[i * 9 + 5] * sin_y
			pby = wave_triangles[i* 9 + 4]
			pbz = wave_triangles[i* 9 + 5] * cos_y + wave_triangles[i * 9 + 3] * sin_y
			
			pcx = wave_triangles[i* 9 + 6] * cos_y - wave_triangles[i * 9 + 8] * sin_y
			pcy = wave_triangles[i* 9 + 7]
			pcz = wave_triangles[i* 9 + 8] * cos_y + wave_triangles[i * 9 + 6] * sin_y
			
			scaleA = FOCAL_LENGTH / ( FOCAL_LENGTH + paz + BASE_CENTER )
			scaleB = FOCAL_LENGTH / ( FOCAL_LENGTH + pbz + BASE_CENTER )
			scaleC = FOCAL_LENGTH / ( FOCAL_LENGTH + pcz + BASE_CENTER )
			
			ax = int(VPX + pax * scaleA)
			ay =  int(VPY + pay * scaleA)
			
			bx = int(VPX + pbx * scaleB)
			by =  int(VPY + pby * scaleB)
			
			cx = int(VPX + pcx * scaleC)
			cy =  int(VPY + pcy * scaleC)
			
			# save lines for erasure
			wave_lines[i * 6 + 0] = ax
			wave_lines[i * 6 + 1] = ay
			
			wave_lines[i * 6 + 2] = bx
			wave_lines[i * 6 + 3] = by
			
			wave_lines[i * 6 + 4] = cx
			wave_lines[i * 6 + 5] = cy
			
			#tft.drawLine( ax, ay, bx, by, ILI9341_WHITE )
			#tft.drawLine( bx, by, cx, cy, ILI9341_WHITE )
			#tft.drawLine( cx, cy, ax, ay, ILI9341_WHITE )
			
			color = WAVE_COLOR if ( i >= int( WAVE_TRIANGLES_TOTAL / 9) - 2 ) else wave_colors[int(i/2)]
			
			#tft.fillTriangle( ax, ay, bx, by, cx, cy, color ) #(i>=(WAVE_TRIANGLES_TOTAL / 9)-2) ? BASE_COLOR : WAVE_COLOR )
			# if (firstRun is True) :
			# 	self.wave_renders[i] = pyglet.shapes.Triangle(ax, ay, bx, by, cx, cy, color=color, batch=self.batch)
			# else:
			# 	self.wave_renders[i].position = (ax, ay, bx, by, cx, cy)
			
			self.wave_renders[i] = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)

			# if i is 0:
			# 	print(ax, ay, bx, by, cx, cy)

		self.renderFace()

	"""
	renderFace
	"""
	def renderFace(self) :
		"""
		int i,pax,pay,paz,pbx,pby,pbz,pcx,pcy,pcz,ax,ay,bx,by,cx,cy
		float scaleA, scaleB, scaleC
		"""

		# front triangles
		for i in range( RES - 1 ) :
		
			pax = face_triangles[i* 9 + 0] * cos_y - face_triangles[i * 9 + 2] * sin_y
			pay = face_triangles[i* 9 + 1]
			paz = face_triangles[i* 9 + 2] * cos_y + face_triangles[i * 9 + 0] * sin_y
			
			pbx = face_triangles[i* 9 + 3] * cos_y - face_triangles[i * 9 + 5] * sin_y
			pby = face_triangles[i* 9 + 4]
			pbz = face_triangles[i* 9 + 5] * cos_y + face_triangles[i * 9 + 3] * sin_y
			
			pcx = face_triangles[i* 9 + 6] * cos_y - face_triangles[i * 9 + 8] * sin_y
			pcy = face_triangles[i* 9 + 7]
			pcz = face_triangles[i* 9 + 8] * cos_y + face_triangles[i * 9 + 6] * sin_y
			
			scaleA = FOCAL_LENGTH / ( FOCAL_LENGTH + paz + BASE_CENTER )
			scaleB = FOCAL_LENGTH / ( FOCAL_LENGTH + pbz + BASE_CENTER )
			scaleC = FOCAL_LENGTH / ( FOCAL_LENGTH + pcz + BASE_CENTER )
			
			ax = int(VPX + pax * scaleA)
			ay =  int(VPY + pay * scaleA)
			
			bx = int(VPX + pbx * scaleB)
			by =  int(VPY + pby * scaleB)
			
			cx = int(VPX + pcx * scaleC)
			cy =  int(VPY + pcy * scaleC)
			
			face_lines[i * 6 + 0] = ax
			face_lines[i * 6 + 1] = ay
			
			face_lines[i * 6 + 2] = bx
			face_lines[i * 6 + 3] = by
			
			face_lines[i * 6 + 4] = cx
			face_lines[i * 6 + 5] = cy
			
			#tft.fillTriangle( ax, ay+1, bx, by, cx, cy, BASE_COLOR ) #WAVE_COLOR )
			#self.face_renders[i] = pyglet.shapes.Triangle(ax, ay+1, bx, by, cx, cy, color=BASE_COLOR, batch=self.batch)
			self.face_renders[i] = pygame.draw.polygon(self.window, BASE_COLOR, [(ax,ay+1),(bx,by),(cx,cy)], 0)

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