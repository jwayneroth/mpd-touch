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
        self.cover_size = 399 #290 #160
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
        self.img = None
        self.vx = 0
        self.vy = 0

        self.set_vels()

        if os.path.dirname(__file__) != '':
            self.image_directory = os.path.dirname(__file__) + '/../' + self.image_directory
        self.screenaver_image_directory = self.image_directory + 'screensavers'

        self.draw_color = fmuglobals.FMU_COLORS['near_black']
        self.erase_mode = True

        self.track_scroll_velocity = 1
        if fmuglobals.RUN_ON_RASPBERRY_PI == True:
            self.track_scroll_velocity = 3

        self.track_y = self.margins * 2 + self.cover_size #self.label_height * 2 + self.margins * 4 + self.cover_size

        self.track = self.make_track()

        self.cover = self.make_cover()

        self.buffer_image = self.cover.image.copy()

        self.make_screenaver()

        print 'ScreensaverScene inited!'

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
    make_cover
    """
    def make_cover(self):
        cover = CoverView(
            ui.Rect(
                0,
                self.margins, #self.label_height * 2 + self.margins * 3,
                self.main.frame.width,
                self.cover_size
            ),
            fmuglobals.current_cover_image,
            ui.Rect(
                0,
                self.label_height * 2 + self.margins * 2,
                self.main.frame.width,
                self.cover_size
            )
        )
        cover.updated = True
        self.main.add_child(cover)
        return cover

    """
    set_vels
    """
    def set_vels(self):
        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-10, 10)
        if self.vx is 0:
            self.vx = 5
        if self.vy is 0:
            self.vy = 5

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
        img.frame.left = random.randint(0, self.main.frame.width)
        img.frame.top = random.randint(0, self.main.frame.height)
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

        current_cover = fmuglobals.current_cover_image

        #self.draw_color = self.get_random_color()

        logger.debug('ss entered %s' % self.cover.image)

        if self.cover.image is not current_cover:
            logger.debug('does not match %s' % fmuglobals.current_cover_image)
            self.cover.image = current_cover
            self.buffer_image = self.cover.image.copy()

        self.track.text = playing.title

        self.resize_track()

        self.set_vels()
        self.img.frame.left = random.randint(0, self.main.frame.width)
        self.img.frame.top = random.randint(0, self.main.frame.height)

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

        #move the bouncing image and do wall check
        bouncer = self.img.frame

        bouncer.left += self.vx
        bouncer.top += self.vy
        if bouncer.left < 0:
            bouncer.left = 0
            self.vx *= -1
        elif bouncer.right > self.main.frame.right:
            bouncer.right = self.main.frame.right
            self.vx *= -1
        if bouncer.top < 0:
            bouncer.top = 0
            self.vy *= -1
        elif bouncer.bottom > self.track_y:
            bouncer.bottom = self.track_y
            self.vy *= -1

        #check intersection btw bouncer and cover
        cover = self.cover.frame
        cl = cover.left
        cr = cover.right
        ct = cover.top
        cb = cover.top + self.cover.image.get_height()
        first_hit = None
        last_hit = None
        for x in range(bouncer.left, bouncer.right):
            for y in range(bouncer.top, bouncer.bottom):
                if x >= cl and x <= cr and y >= ct and y <= cb:
                    if first_hit is None:
                        first_hit = (x,y)
                    last_hit = (x,y)
        if first_hit is not None:
            draw_left = first_hit[0] - cl
            draw_top = first_hit[1] - ct
            draw_w = last_hit[0] - first_hit[0]
            draw_h = last_hit[1] - first_hit[1]

            erased = self.is_cover_erased()

            #we are erasing the cover image
            if self.erase_mode == True:

                #its fully erased, start redrawing it
                if erased == 1:
                    #print 'fully erased, start, drawing'
                    self.erase_mode = False
                    self.cover.image.blit(self.buffer_image, (draw_left, draw_top), [draw_left, draw_top, draw_w, draw_h])
                #continue erasing
                else:
                    self.cover.image.fill(self.draw_color, [draw_left, draw_top, draw_w, draw_h])

            #we are redrawing the cover image
            else:

                #its fully redrawn, start erasing it
                if erased == -1:
                    #print 'fully drawn, start erasing'
                    self.erase_mode = True
                    self.cover.image.fill(self.draw_color, [draw_left, draw_top, draw_w, draw_h])
                #continue redrawing
                else:
                    self.cover.image.blit(self.buffer_image, (draw_left, draw_top), [draw_left, draw_top, draw_w, draw_h])

        #scroll the track info
        track = self.track

        track.frame.left = track.frame.left - self.track_scroll_velocity
        if track.frame.left < -( track.frame.width ):
            track.frame.left = self.main.frame.right
            track.updated = True

        #render
        self.stylize()

    """
    is_cover_erased
    return 1 for completely erased
    return 0 for partly erased
    return -1 for completely original
    """
    def is_cover_erased(self):
        cover = self.cover.image

        cw = cover.get_width()
        ch = cover.get_height()

        has_diff = False
        has_orig = False

        step = 20
        x = 0
        y = 0
        diffs = 0

        for i in range(0, int(cw/step)):
            for j in range(0, int(ch/step)):

                x = i * step
                y = j * step

                pixel = cover.get_at((x,y))
                orig_pixel = self.buffer_image.get_at((x,y))

                if pixel.r != orig_pixel.r or pixel.g != orig_pixel.g or pixel.b != orig_pixel.b:
                    diffs = diffs +1
                    has_diff = True
                    if has_orig == True:
                        return 0
                else:
                    has_orig = True
                    if has_diff == True:
                        return 0

        if has_diff is True:
            if has_orig is False:
                return 1
            return 0
        return -1

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
    get_random_color
    """
    def get_random_color(self):
        return (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))

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
