#!/usr/bin/python

import random
import sys
from signal import alarm, signal, SIGALRM, SIGKILL
import os
import subprocess
import logging
from mpd_client import *
import fmuglobals
import buttons
import pygameui as ui

from albumlist import *
from controls import *
from nowplaying import *
from radio import *
from settings import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger('fmu_logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler(fmuglobals.HOME_DIR + '/fmulcd.log','a')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

class FMU(object):
    def __init__(self):
        self.current = False
        self.screen_dimensions = (320,480)
        self.screen = False

        if not mpd.connect():
            print 'failed to connect to mpd once'
            cmd = 'service mpd start'
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            print p.communicate()[0]
            
            if not mpd.connect():
                print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'sudo service mpd status'.")
                sys.exit()

        if fmuglobals.RUN_ON_RASPBERRY_PI:
            os.environ['SDL_FBDEV'] = '/dev/fb1'
            os.environ["SDL_NOMOUSE"] = "1"
            os.environ['SDL_MOUSEDEV'] = '/dev/input/touchscreen'
            os.environ['SDL_MOUSEDRV'] = 'TSLIB'

        self.init_pygame()
        
        ui.theme.init()
        ui.theme.use_theme(ui.theme.dark_theme)

        rect = pygame.Rect((0,0),self.screen_dimensions)

        self.scenes = { 
            'NowPlaying': NowPlayingScene(rect), 
            'Albums': AlbumListScene(rect), 
            'Radio': RadioScene(rect),
            'Settings': SettingsScene(rect),
            'Controls': ControlsScene(rect)
        }

        for name,scene in self.scenes.iteritems():
            scene.on_nav_change.connect(self.change_scene)

        print 'created scenes'

        self.make_current_scene(self.scenes['NowPlaying'])

        self.ab = buttons.AnalogButtons()

    """
    init_pygame
    """
    def init_pygame(self):
        # this section is an unbelievable nasty hack - for some reason Pygame
        # needs a keyboardinterrupt to initialise in some limited circs (second time running)
        class Alarm(Exception):
            pass
        
        def alarm_handler(signum, frame):
            raise Alarm
        
        signal(SIGALRM, alarm_handler)
        
        alarm(3)
        
        try:
            pygame.init()

            if fmuglobals.RUN_ON_RASPBERRY_PI:
                pygame.mouse.set_visible(False)
                display_flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.ANYFORMAT
                self.screen = pygame.display.set_mode( (self.screen_dimensions), display_flags )
            else:
                self.screen = pygame.display.set_mode(self.screen_dimensions)

            alarm(0)

        except Alarm:
            raise KeyboardInterrupt

        logger.debug('paygame inited on rpi?: %s' % fmuglobals.RUN_ON_RASPBERRY_PI)

        pygame.key.set_repeat(300,180)
        pygame.display.set_caption('Raspberry Pi UI')
        #pygame.event.set_allowed(None)
        #pygame.event.set_allowed(( pygame.QUIT, pygame.KEYDOWN ))

    """
    signal_handler
    """
    def signal_handler(self, signal, frame):
        print '\nFMULCD::signal_handler: {}'.format(signal)
        time.sleep(1)
        pygame.display.quit()
        pygame.quit()
        sys.exit(0)


    """
    change_scene
    """
    def make_current_scene(self, scene):
        print 'FMULCD::make_current_scene \t' + scene.name
        #if self.current == scene:
        #    return
        if self.current:
            self.current.exited()
        self.current = scene
        self.current.entered()
        self.current.refresh()

    """
    change_scene
     called from a PiScene on_nav_change
     push requested scene to ui and refresh it
    """
    def change_scene(self, scene_name, refresh=False):
        if refresh == True:
            self.scenes['Albums'].populate_artists_view()
        self.make_current_scene(self.scenes[scene_name])

"""
main
"""
if __name__ == '__main__':
    logger.debug('fmulcd started')
    fmu = FMU()
    clock = pygame.time.Clock()
    fps = 12 if fmuglobals.RUN_ON_RASPBERRY_PI else 30

    while True:
        clock.tick(fps)
        down_in_view = None
        
        for e in pygame.event.get():
            
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
                break
            
            mousepoint = pygame.mouse.get_pos()

            if e.type == pygame.KEYDOWN:
                if (( e.key == pygame.K_ESCAPE )):
                    pygame.quit()
                    sys.exit(0)
                else:
                    fmu.current.key_down(e.key, e.unicode)
                    break
           
            elif e.type == pygame.MOUSEBUTTONDOWN:
                hit_view = fmu.current.hit(mousepoint)
                
                logger.debug('hit %s at %s' % (hit_view, mousepoint))
                
                if (hit_view is not None and
                    not isinstance(hit_view, ui.Scene)
                ):
                    ui.focus.set(hit_view)
                    down_in_view = hit_view
                    pt = hit_view.from_window(mousepoint)
                    hit_view.mouse_down(e.button, pt)
                else:
                    ui.focus.set(None)
            
            elif e.type == pygame.MOUSEBUTTONUP:
                hit_view = fmu.current.hit(mousepoint)
                if hit_view is not None:
                    if down_in_view and hit_view != down_in_view:
                        down_in_view.blurred()
                        ui.focus.set(None)
                    pt = hit_view.from_window(mousepoint)
                    hit_view.mouse_up(e.button, pt)
                down_in_view = None
            
            elif e.type == pygame.MOUSEMOTION:
                if down_in_view and down_in_view.draggable:
                    pt = down_in_view.from_window(mousepoint)
                    down_in_view.mouse_drag(pt, e.rel)
                else:
                    fmu.current.mouse_motion(mousepoint)

        fmu.current.update()
        
        if fmu.current.draw():
        
            fmu.screen.blit(fmu.current.surface, (0, 0))
        
            pygame.display.flip()
        
        #time.sleep(.05)
    