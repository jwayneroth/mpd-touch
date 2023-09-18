import os

RUN_ON_RASPBERRY_PI = os.uname()[4][:3] == 'arm'

HOME_DIR = os.path.expanduser("~")

SCREEN_SIZE = (800, 480)
NAV_ICON_SIZE = 34
ICON_SIZE = 24

FMU_COLORS = {
	'near_black':   (10,5,0),
	'dark_brown':   (60,44,28),
	'mid_brown':    (80,62,32),
	'slime':        (139,250,73),
	'lemon':        (246,248,63),
	'orange':       (240,140,2),
	'dark_gray':    (80,77,81),
	'mid_gray':     (188,180,192),
	'light_gray':   (180,140,190),
	'dark_purple':  (60,50,65),
	'light_purple': (124,100,118),
	'grad_dark':    (20,15,2),
	'grad_light':   (110,80,20)
}

current_cover_image = None

import logging
logger = logging.getLogger('fmu_logger')
logger.debug('HOME_DIR: {}'.format(str(HOME_DIR)))
logger.debug('RUN_ON_RASPBERRY_PI: {}'.format(str(RUN_ON_RASPBERRY_PI)))

USE_LIRCD = True
SHOW_MOUSE = False
FULLSCREEN = True
SS_DELAY = 60000
SS_UPDATE_INTERVAL = .033
TRACK_SPEED = 3
