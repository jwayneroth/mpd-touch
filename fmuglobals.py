import os

RUN_ON_RASPBERRY_PI = os.uname()[4][:3] == 'arm'

HOME_DIR = os.path.expanduser("~")

print 'HOME_DIR: ' + str(HOME_DIR)
print 'RUN_ON_RASPBERRY_PI: ' + str(RUN_ON_RASPBERRY_PI)