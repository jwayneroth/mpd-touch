import fmuglobals
from piscene import *
import thread
import time
import os

"""
NowPlayingScene
 displays cover art, if available
 and playback controls
"""
class NowPlayingScene(PiScene):
    def __init__(self, frame=None):

        PiScene.__init__(self, frame, 'NowPlaying')

        self.has_nav = True
        self.is_mpd_listener = True
        self.cover_size = 160
        self.label_height = 20
        self.track_scroll_velocity = 1
        if fmuglobals.RUN_ON_RASPBERRY_PI == True:
            self.track_scroll_velocity = 3
        self.main_active = False
        self.components = {}
        self.image_directory = 'images/'
        if os.path.dirname(__file__) != '':
            self.image_directory = os.path.dirname(__file__) + '/' + self.image_directory
        self.default_cover_image_directory = self.image_directory + 'default_covers'
        self.cover_image_directory = self.image_directory + 'covers'

        self.make_labels()

        #self.scroller = TrackScroller(self.components['track'], 1, self.frame.right)

        #self.main.add_child(self.labels)

    """
    key_down
    """
    def key_down(self, key, code):
        ui.Scene.key_down(self,key,code)

        if key == pygame.K_RIGHT or  key == pygame.K_LEFT or key == pygame.K_RETURN:
            self.key_down_sidebar(key)

    """
    make_labels
    """
    def make_labels(self):
        comp_labels = {
            'artist': [
                ui.Rect( 0,0, self.main.frame.width,self.label_height ),
                mpd.now_playing.artist
            ],
            'album': [
                ui.Rect( 0, self.label_height + self.margins, self.main.frame.width, self.label_height ),
                mpd.now_playing.album
            ],
            'track': [
                ui.Rect( 0, self.label_height * 2 + self.margins * 3 + self.cover_size, self.main.frame.width, self.label_height ),
                mpd.now_playing.title
            ]
        }


        for key, val in comp_labels.iteritems():
            label = ui.Label( val[0], val[1], halign=ui.CENTER )
            self.main.add_child(label)
            self.components[key] = label

        cover = CoverView(
            ui.Rect(
                0,
                self.label_height * 2 + self.margins * 2,
                self.main.frame.width,
                self.cover_size
            ),
            self.get_cover_image(),
            ui.Rect(
                0,
                self.label_height * 2 + self.margins * 2,
                self.main.frame.width,
                self.cover_size
            )
        )
        cover.updated = True
        self.main.add_child(cover)
        self.components['album_cover'] = cover

    """
    entered
    """
    def entered(self):

        PiScene.entered(self)

        playing = mpd.now_playing

        self.components['artist'].text = playing.artist
        self.components['album'].text = playing.album
        self.components['album_cover'].image = self.get_cover_image()
        self.components['album_cover'].updated = True
        self.components['track'].text = playing.title
        #self.labels.components['track'].shrink_wrap()

        if mpd.now_playing.playing_type == 'radio':
            self.radio_track_settings(True)
        else:
            self.radio_track_settings(False)

        #self.scroller.start()

        self.stylize()

        #PiScene.entered(self)

    """
    exited
    """
    def exited(self):
        logger.debug('NowPlaying exited')
        #self.scroller.stop()

    """
    radio_track_settings
    """
    def radio_track_settings(self, on_off):

        track = self.components['track']

        if on_off == True:
            track.halign = ui.LEFT
            self.resize_track()
        else:
            track.halign = ui.CENTER
            track.frame.left = 10
            track.frame.width = self.main.frame.width

        self.stylize()

    """
    resize_track
    """
    def resize_track(self):
        track = self.components['track']
        track.frame.width = track.text_size[0] + 10 # + self.margins
        track.frame.left = 0
        print 'NowPlayingScene::resize_track \t w: ' + str(track.frame.width)
        self.stylize()

    """
    update
    """
    def update(self):
        PiScene.update(self)
        if mpd.now_playing.playing_type == 'radio':
        #if 1:
            track = self.components['track']
            track.frame.left = track.frame.left - self.track_scroll_velocity
            if track.frame.left < -( track.frame.width ):
                #print 'looping scroller'
                track.frame.left = self.main.frame.right
            track.updated = True

    """
    on_mpd_update
    """
    def on_mpd_update(self):
        while True:
            try:

                event = mpd.events.popleft()

                #print 'NowPlaying::on_mpd_update \t ' + event

                if event == 'radio_mode_on':
                    print 'NowPlayingScene::on_mpd_update: \t radio_mode_on'
                    self.radio_track_settings(True)
                #elif event == 'time_elapsed':
                #    print 'NowPlayingScene::on_mpd_update: \t time_elapsed'
                #    break
                elif event == 'radio_mode_off':
                    print 'NowPlayingScene::on_mpd_update: \t radio_mode_off'
                    self.radio_track_settings(False)
                elif event == 'title_change':
                    print 'NowPlayingScene::on_mpd_update: \t title_change'
                    playing = mpd.now_playing
                    self.components['track'].text = playing.title
                    if playing.playing_type == 'radio':
                        self.resize_track()
                elif event == 'album_change':
                    print 'NowPlayingScene::on_mpd_update: \t album_change'
                    playing = mpd.now_playing
                    self.components['artist'].text = playing.artist
                    self.components['album'].text = playing.album
                    self.components['album_cover'].image = self.get_cover_image()
                    self.stylize()
                """
                elif event == 'volume':
                    print 'NowPlayingScene::on_mpd_update: \t volume: ' + str(mpd.volume)
                    self.controls.volume_slider.value = mpd.volume
                elif event == 'player_control':
                    state = mpd.player_control_get()
                    play_btn = self.controls.buttons['play_pause']
                    print 'NowPlayingScene::on_mpd_update: \t state: ' + state
                    if play_btn.icon_class != 'play' and state == 'play':
                        play_btn.icon_class = 'play'
                    if play_btn.icon_class != 'pause' and state == 'pause':
                        play_btn.icon_class = 'pause'
                    break
                """
            except IndexError:
                break

        #print 'on_mpd_update'

    """
    get_cover_image
    """
    def get_cover_image(self):
        if mpd.now_playing.playing_type == 'radio':
            if mpd.now_playing.file.find('wfmu.org') != -1:
                return ui.get_image(self.image_directory + '/wfmu.png')
            else:
                return ui.get_image(self.get_default_cover_image())


        file_dir = self.music_directory + os.path.dirname(mpd.now_playing.file)
        file_name = file_dir + '/' + 'cover_art.jpg'

        print 'NowPlaying::get_cover_image: ' + file_name

        if os.path.isfile(file_name) == False:
            print '\t no existing image'
            try:
                music_file = File(self.music_directory + mpd.now_playing.file)
                if 'covr' in music_file:
                    try:
			art_data = music_file.tags['covr'].data
                    except:
			return ui.get_image( self.get_default_cover_image() )		
		elif 'APIC:' in music_file:
                    try:
			art_data = music_file.tags['APIC:'].data
                    except:
			return ui.get_image( self.get_default_cover_image() )
		else:
                    print '\t no cover art data'
                    return ui.get_image( self.get_default_cover_image() )

                with open(file_name, 'wb') as img:
                    img.write(art_data)

            except IOError, e:
                print '\t no music file'
                return ui.get_image( self.get_default_cover_image() )

        print '\t returning: ' + file_name

        return ui.get_image( file_name )

    """
    get_default_cover_image
    """
    def get_default_cover_image(self):
        defaults = [name for name in os.listdir( self.default_cover_image_directory ) if os.path.isfile( self.default_cover_image_directory + '/' + name )]
        return self.default_cover_image_directory + '/' + defaults[random.randrange(0, len(defaults))]

"""
CoverView
 extend ui.ImageView
"""
class CoverView(ui.ImageView):
    def __init__(self, frame, img, parent_frame, content_mode=1):

        #ui.ImageView.__init__(self, frame, img)

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

"""
TrackScroller
"""

class TrackScroller():
    def __init__(self, view, vel=2, right=100):
        self.scrollee = view
        self.vel = vel
        self.right = right
        self.scrolling = True
        self.start_thread()

    def stop(self):
        self.scrolling = False

    def start(self):
        self.scrolling = True

    def start_thread(self):
        try:
            self.thread = thread.start_new_thread( self.scroll, ())
        except:
            print 'TrackScroller unable to start thread'

    def scroll(self):
        while 1:
            if self.scrolling == True:
                self.scrollee.frame.left = self.scrollee.frame.left - self.vel
                if self.scrollee.frame.left < -( self.scrollee.frame.width ):
                    self.scrollee.frame.left = self.right
                self.scrollee.updated = True
            time.sleep(.012)
