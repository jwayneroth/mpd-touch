import os

RUN_ON_RASPBERRY_PI = os.uname()[4][:3] == 'arm'

HOME_DIR = os.path.expanduser("~")

COLORS = {
	'near_black': '#%02x%02x%02x' % (10,5,0),
	'dark_brown': '#%02x%02x%02x' % (60,44,28),
	'mid_brown': '#%02x%02x%02x' % (80,62,32),
	'slime': '#%02x%02x%02x' % (139,250,73),
	'lemon': '#%02x%02x%02x' % (246,248,63),
	'orange': '#%02x%02x%02x' % (240,140,2),
	'dark_gray': '#%02x%02x%02x' % (80,77,81),
	'mid_gray': '#%02x%02x%02x' % (124,120,132),
	'light_gray': '#%02x%02x%02x' % (180,140,190),
	'dark_purple': '#%02x%02x%02x' % (60,50,65),
	'light_purple': '#%02x%02x%02x' % (124,100,118)
}


print 'HOME_DIR: ' + str(HOME_DIR)
print 'RUN_ON_RASPBERRY_PI: ' + str(RUN_ON_RASPBERRY_PI)