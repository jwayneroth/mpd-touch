import os

RUN_ON_RASPBERRY_PI = os.uname()[4][:3] == 'arm'

HOME_DIR = os.path.expanduser("~")

SCREEN_SIZE = (800, 480)
NAV_ICON_SIZE = 34
ICON_SIZE = 24

current_cover_image = None

print 'HOME_DIR: ' + str(HOME_DIR)
print 'RUN_ON_RASPBERRY_PI: ' + str(RUN_ON_RASPBERRY_PI)
