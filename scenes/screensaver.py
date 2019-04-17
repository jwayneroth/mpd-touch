import time
import os

import fmuglobals
from piscene import *

"""
ScreensaverScene
"""
class ScreensaverScene(PiScene):
    def __init__(self, frame=None):
        ui.Scene.__init__(self, frame)
        self.name = 'Screensaver'
        self.margins = 15
        self.btn_size = 45
        self.margins_bottom = 10
        self.has_nav = False
        self.is_mpd_listener = True
        self.cover_size = 290 #160
        self.label_height = 36
        self.music_directory = '/var/lib/mpd/music/'
        self.main_active = False
        self.sidebar_index = 0
        self.active_sidebar_btn = 0
        self.sidebar = None
        self.main = self.make_main()
        self.add_child(self.main)
        self.on_nav_change = callback.Signal()
        self.image_directory = 'images/'
        self.img_size = 160
        self.vx = random.randrange(-5, 5)
        self.vy = random.randrange(-5, 5)
        if os.path.dirname(__file__) != '':
            self.image_directory = os.path.dirname(__file__) + '/../' + self.image_directory
        self.screenaver_image_directory = self.image_directory + 'screensavers'

        self.track_scroll_velocity = 1
        if fmuglobals.RUN_ON_RASPBERRY_PI == True:
            self.track_scroll_velocity = 3

        self.track_y = self.label_height * 2 + self.margins * 4 + self.cover_size

        self.track = self.make_track()

        self.make_screenaver()

    """
    make_main
    """
    def make_main(self):

        main = PiMain( #ui.View(
            ui.Rect(
                0,
                0,
                self.frame.width,
                self.frame.height
            )
        )

        return main

    """
    mouse_down
    """
    def hit(self, pt):
        pass
        #self.on_nav_change('NowPlaying', from_screensaver=True)

    """
    key_down
    """
    def key_down(self, key, code):
        if key == pygame.K_RETURN:
            self.on_nav_change('NowPlaying', from_screensaver=True)

    """
    make_screenaver
    """
    def make_screenaver(self):
        img = ScreensaverImageView(
            None,
            ui.get_image(self.get_random_screensaver_image()),
            ui.Rect(
                0,
                self.label_height * 2 + self.margins * 2,
                self.main.frame.width,
                self.img_size
            )
        )
        self.img = img
        img.updated = True
        self.main.add_child(img)

    """
    make_track
    """
    def make_track(self):
        track_x = 0
        track_y = self.track_y
        track_rect = ui.Rect(track_x, track_y, self.main.frame.width, self.label_height)
        track = ui.HeadingOne(track_rect, mpd.now_playing.title, halign=ui.CENTER)
        self.main.add_child(track)
        return track

    """
    entered
    """
    def entered(self):

        PiScene.entered(self)

        playing = mpd.now_playing

        self.track.text = playing.title

        self.resize_track()

        self.stylize()

    """
    resize_track
    """
    def resize_track(self):
        track = self.track
        track.frame.width = track.text_size[0] + 10 # + self.margins
        track.frame.left = 0
        #print 'NowPlayingScene::resize_track \t w: ' + str(track.frame.width)
        self.stylize()

    """
    exited
    """
    def exited(self):
        logger.debug('Screensaver exited')

    """
    update
    """
    def update(self):
        PiScene.update(self)
        self.img.frame.left += self.vx
        self.img.frame.top += self.vy
        if self.img.frame.left < 0:
            self.img.frame.left = 0
            self.vx *= -1
        elif self.img.frame.right > self.main.frame.right:
            self.img .frame.right = self.main.frame.right
            self.vx *= -1
        if self.img.frame.top < 0:
            self.img.frame.top = 0
            self.vy *= -1
        elif self.img.frame.bottom > self.track_y: #self.main.frame.bottom
            self.img.frame.bottom = self.track_y #self.main.frame.bottom
            self.vy *= -1

        track = self.track

        track.frame.left = track.frame.left - self.track_scroll_velocity
        if track.frame.left < -( track.frame.width ):
            track.frame.left = self.main.frame.right
            track.updated = True

        self.stylize()

    """
    on_mpd_update
    """
    def on_mpd_update(self):
        while True:
            try:

                event = mpd.events.popleft()

                if event == 'radio_mode_on':
                    self.resize_track()
                    self.stylize()
                elif event == 'radio_mode_off':
                    self.resize_track()
                    self.stylize()
                elif event == 'title_change':
                    playing = mpd.now_playing
                    self.track.text = playing.title
                    self.resize_track()
                    self.stylize()
                elif event == 'album_change':
                    playing = mpd.now_playing
                    self.resize_track()
                    self.stylize()
            except IndexError:
                break

    """
    get_random_screensaver_image
    """
    def get_random_screensaver_image(self):
        defaults = [name for name in os.listdir( self.screenaver_image_directory ) if os.path.isfile( self.screenaver_image_directory + '/' + name )]
        return self.screenaver_image_directory + '/' + defaults[random.randrange(0, len(defaults))]

"""
ScreensaverImageView
 extend ui.ImageView
"""
class ScreensaverImageView(ui.ImageView):
    def __init__(self, frame, img, parent_frame, content_mode=1):

        if img == None:
            img = resource.get_image( self.image_directory + 'defaults_covers/1.png')

        assert img is not None

        if frame is None:
            frame = pygame.Rect((0, 0), img.get_size())
        elif frame.w == 0 and frame.h == 0:
            frame.size = img.get_size()

        self._max_frame = frame

        self._enabled = False
        self.content_mode = content_mode
        self.image = img
        self.parent_frame = parent_frame

        #assert self.padding[0] == 0 and self.padding[1] == 0

        if self.content_mode == 0:
            self._image = ui.resource.scale_image(self.image, frame.size)
        elif self.content_mode == 1:
            self._image = ui.resource.scale_to_fit(self.image, frame.size)
        else:
            assert False, "Unknown content_mode"

        if self._image.get_width() < self.parent_frame.width:
            frame.left = (self.parent_frame.width - self._image.get_width()) / 2

        frame.size = self._image.get_size()

        ui.View.__init__(self, frame)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        try:
            self._image = ui.resource.scale_to_fit(new_image, self._max_frame.size)
        except:
            self._image = new_image

        try:
            pf = self.parent_frame

            try:
                f = self.frame
                if self._image.get_width() < pf.width:
                    f.left = (pf.width - self._image.get_width() ) / 2
            except:
                pass
        except:
            pass

    """
    layout
     override ui.ImageView
    """
    def layout(self):
        ui.View.layout(self)
