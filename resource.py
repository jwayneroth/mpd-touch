#import pygame
#import pkg_resources
import os
import weakref
from PIL import Image

import logging
logger = logging.getLogger('fmu_logger')

image_cache = weakref.WeakValueDictionary()
#font_cache = weakref.WeakValueDictionary()
#sound_cache = weakref.WeakValueDictionary()

def get_image(fullpath):
	logger.debug('get_image: ' + fullpath)

	path_file = os.path.split(fullpath) # ( path, filename )
	name_ext = os.path.splitext(path_file[1]) # ( name, ext ) 
	
	try:
		img = image_cache[ path_file[0] + '_'  + name_ext[0] ]
		logger.debug('got cache ' + path_file[0] + '_'  + name_ext[0])
	except KeyError:
		try:
			logger.debug('loading image %s' % fullpath)
			img = Image.open(fullpath)
		except e:
			logger.warn('failed to load image: %s: %s' % (fullpath, e))
			img = None
		else:
			#img = img.convert_alpha()
			image_cache[ path_file[0] + '_' + name_ext[0] ] = img
	return img

def scale_image(image, size):
	return image
	#return pygame.transform.smoothscale(image, size)

def scale_to_fit(image, size):
	
	iw = image.get_width()
	ih = image.get_height()

	sw = size[0]
	sh = size[1]

	wp = float(sw) / float(iw)
	hp = float(sh) / float(ih)

	#print '%.2f'%wp
	#print '%.2f'%hp

	ratio = min(wp,hp)
	size = (int( ratio * iw ), int( ratio * ih ))

	#print 'scale_to_fit \t iw: ' + str(iw) + ' ih: ' + str(ih) + ' sw: ' + str(sw) + ' sh: ' + str(sh)
	#print '\t\t ip: ' + str(ip) + ' sp: ' + str(sp)
	#print '\t\t size: ' + str(size)

	return self.scale_image(image, size)

"""
def get_sound(name):
	class NoSound:
		def play(self):
			pass
	if not pygame.mixer or not pygame.mixer.get_init():
		return NoSound()
	try:
		sound = sound_cache[name]
	except KeyError:
		path = HOME_DIR + '/pygameui/resources/sounds/%s.ogg' % name
		try:
			sound = pygame.mixer.Sound(path)
		except pygame.error, e:
			logger.warn('failed to load sound: %s: %s' % (path, e))
			sound = NoSound()
		else:
			sound_cache[path] = sound
	return sound
"""

"""
def get_font(size=16, use_bold=False, name='regular'):
	filename = name
	if use_bold:
		filename = 'bold'
	key = '%s:%d' % (filename, size)
	try:
		font = font_cache[key]
	except KeyError:
		path = 'resources/fonts/%s.ttf' % filename
		path = pkg_resources.resource_filename(package_name, path)
		print 'resource::get_font \t font: ' + path
		try:
			logger.debug('loading font %s' % path)
			font = pygame.font.Font(path, size)
		except pygame.error, e:
			logger.warn('failed to load font: %s: %s' % (path, e))
			backup_fonts = 'helvetica,arial'
			font = pygame.font.SysFont(backup_fonts, size, use_bold)
		else:
			font_cache[key] = font
	return font
"""