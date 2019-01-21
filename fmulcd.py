#!/usr/bin/python

import random
import sys
from signal import alarm, signal, SIGALRM, SIGKILL
import os
import time
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
from screensaver import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger('fmu_logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/fmulcd.log', 'a')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

class FMU(object):
    def __init__(self):
        self.current = False
        self.last = False
        self.screen_dimensions = (320,480)
        self.screen = False
        self.ss_timer = 0
        self.ss_timer_on = False
        self.ss_delay = 60000

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
            'Controls': ControlsScene(rect),
            'Screensaver': ScreensaverScene(rect)
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

        logger.debug('pygame inited on rpi?: %s' % fmuglobals.RUN_ON_RASPBERRY_PI)

        pygame.key.set_repeat(300,180)
        pygame.display.set_caption('Raspberry Pi UI')
        #pygame.event.set_allowed(None)
        #pygame.event.set_allowed(( pygame.QUIT, pygame.KEYDOWN ))

    """
    signal_handler
    """
    def signal_handler(self, signal, frame):
        print '\FMU::signal_handler: {}'.format(signal)
        time.sleep(1)
        pygame.display.quit()
        fmu.kill_app()


    """
    make_current_scene
    """
    def make_current_scene(self, scene):
        logger.debug('FMU::make_current_scene \t' + scene.name)
        #if self.current == scene:
        #    return
        if self.current:
            self.current.exited()
            self.last = self.current
        self.current = scene
        self.current.entered()
        self.current.refresh()

    """
    change_scene
     called from a PiScene on_nav_change
     push requested scene to ui and refresh it
    """
    def change_scene(self, scene_name, refresh=False, from_screensaver=False):
        if from_screensaver:
            self.ss_timer_on = True
            if self.last:
                self.make_current_scene(self.last)
                return
        if refresh == True:
            self.scenes['Albums'].populate_artists_view()
        self.make_current_scene(self.scenes[scene_name])

    def screensaver_tick(self, ms, activity):
        if activity:
            self.ss_timer = 0
        else:
            self.ss_timer += ms
            if self.ss_timer >= self.ss_delay:
                logger.debug('going to screensaver')
                self.ss_timer_on = False
                self.ss_timer = 0
                self.change_scene('Screensaver')

    def kill_app(self):
        #if fmuglobals.RUN_ON_RASPBERRY_PI:
        #    GPIO.output(18, GPIO.LOW)
        pygame.quit()
        sys.exit(0)


"""
main
"""
if __name__ == '__main__':
    logger.debug('fmulcd started')
    fmu = FMU()
    clock = pygame.time.Clock()
    fps = 12 if fmuglobals.RUN_ON_RASPBERRY_PI else 30
    ticks = 0

    while True:
        ticks = clock.tick(fps)

        down_in_view = None
        user_active = False

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                fmu.kill_app()
                break

            mousepoint = pygame.mouse.get_pos()

            if e.type == pygame.KEYDOWN:
                user_active = True
                if (( e.key == pygame.K_ESCAPE )):
                    fmu.kill_app()
                else:
                    fmu.current.key_down(e.key, e.unicode)
                    break

            elif e.type == pygame.MOUSEBUTTONDOWN:
                user_active = True

                hit_view = fmu.current.hit(mousepoint)

                #logger.debug('hit %s at %s' % (hit_view, mousepoint))

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
                user_active = True
                hit_view = fmu.current.hit(mousepoint)
                logger.debug('click %s at %s' % (hit_view, mousepoint))

                if fmu.current == fmu.scenes['Screensaver']:
                    fmu.change_scene('NowPlaying', False, True)
                    break

                if hit_view is not None:
                    if down_in_view and hit_view != down_in_view:
                        down_in_view.blurred()
                        ui.focus.set(None)
                    pt = hit_view.from_window(mousepoint)
                    hit_view.mouse_up(e.button, pt)
                down_in_view = None

            elif e.type == pygame.MOUSEMOTION:
                user_active = True
                if down_in_view and down_in_view.draggable:
                    pt = down_in_view.from_window(mousepoint)
                    down_in_view.mouse_drag(pt, e.rel)
                else:
                    fmu.current.mouse_motion(mousepoint)

        if fmu.ss_timer_on:
            fmu.screensaver_tick(ticks, user_active)

        fmu.current.update()

        if fmu.current.draw():

            fmu.screen.blit(fmu.current.surface, (0, 0))

            pygame.display.flip()

        #time.sleep(.05)
