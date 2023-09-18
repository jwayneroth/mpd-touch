import pygame
import math
#from pyglet import shapes

import logging
logger = logging.getLogger('fmu_logger')

class Triangle() :
	def __init__(self, a, b, c, color=(255,255,255), batch=None, window=None, light=None, wireframe=False) :
		self.pointA = a
		self.pointB = b
		self.pointC = c
		self.color = color
		self.batch = batch
		self.window = window
		self.light = light
		#self.yOffset = int( window.get_size()[0] / 2 )
		self.debug = False
		self.render = None

	def draw(self) : 
		
		# if ( self.isBackFace() ) :
		# 	return None
		
		ax = self.pointA.screenX
		ay = self.pointA.screenY #self.yOffset - self.pointA.screenY
		bx = self.pointB.screenX
		by = self.pointB.screenY #self.yOffset - self.pointB.screenY
		cx = self.pointC.screenX
		cy = self.pointC.screenY #self.yOffset - self.pointC.screenY
		
		#g.drawLine( ax, ay, bx, by, WHITE )
		#g.drawLine( bx, by, cx, cy, WHITE )
		#g.drawLine( cx, cy, ax, ay, WHITE )

		color = self.getAdjustedColor()

		# TODO: fake the color based on the angle of the triangle's (front or back) edge
		#color = self.getAdjustedColorAlt(ax,ay,cx,cy)
		
		# override color for backface triangles
		if ( self.isBackFace() ) :
			color = [self.color[0] * .15, self.color[1] * .15, self.color[2] * .15]

		#print('adjusted color {}'.format(color))
		
		if (self.debug):
			print('ax: {} ay: {}'.format(ax,ay))
		
		#self.render = shapes.Triangle(ax,ay,bx,by,cx,cy,color=color,batch=self.batch)
		self.render = pygame.draw.polygon(self.window, color, [(ax,ay),(bx,by),(cx,cy)], 0)

	def getDepth(self) : 
		zpos = min( self.pointA.getZ(), self.pointB.getZ() )
		zpos = min(zpos, self.pointC.getZ())
		return zpos

	def isBackFace(self) : 
		# see http://www.jurjans.lv/flash/shape.html

		cax = self.pointC.screenX - self.pointA.screenX
		cay = self.pointC.screenY - self.pointA.screenY
				
		bcx = self.pointB.screenX - self.pointC.screenX
		bcy = self.pointB.screenY - self.pointC.screenY
		
		return cax * bcy > cay * bcx

	# TODO: use angle, not slope.
	def getAdjustedColorAlt(self, ax, ay, cx, cy) :
		red = self.color[0]
		green = self.color[1]
		blue = self.color[2]

		slope = (cy - ay) / (cx - ax)

		lightFactor = min(1, max(0, abs(slope)))

		logger.debug("lightFactor: %s", lightFactor)

		red = int( red * lightFactor )
		green = int( green * lightFactor )
		blue = int( blue * lightFactor )
		
		return (red, green, blue )

	def getAdjustedColor(self) :
		
		red = self.color[0]
		green = self.color[1]
		blue = self.color[2]
		
		#print ('red {} green {} blue {}'.format(red, green, blue))

		lightFactor = self.getLightFactor()
		
		#print ('lightFactor {}'.format(lightFactor))

		red = int( red * lightFactor )
		green = int( green * lightFactor )
		blue = int( blue * lightFactor )
		
		return (red, green, blue )
	
	def getLightFactor(self) :
		ab = (
			self.pointA.x - self.pointB.x,
			self.pointA.y - self.pointB.y,
			self.pointA.z - self.pointB.z
		)
		
		bc = (
			self.pointB.x - self.pointC.x,
			self.pointB.y - self.pointC.y,
			self.pointB.z - self.pointC.z
		)
		
		norm = (
			( ( ab[1] * bc[2] ) - ( ab[2] * bc[1] ) ),
			-( ( ab[0] * bc[2] ) - ( ab[2] * bc[0] ) ),
			( ( ab[0] * bc[1] ) - ( ab[1] * bc[0] ) )
		)

		dotProd = norm[0] * self.light.x + norm[1] * self.light.y + norm[2] * self.light.z
		
		normMag = math.sqrt( norm[0] * norm[0] + norm[1] * norm[1] + norm[2] * norm[2] )
		
		lightMag = math.sqrt( self.light.x * self.light.x + self.light.y * self.light.y + self.light.z * self.light.z )
		
		#print ('dotProd {} normMag {} blue {}'.format(dotProd, normMag, lightMag))
		
		if normMag == 0 or lightMag == 0:
			return 0
		
		return ( math.acos( dotProd / ( normMag * lightMag ) ) / math.pi ) * self.light.brightness



























