from ..lib.mpd_client import *
from .. import pygameui as ui

"""
PiScene
 pygameui.Scene subclass
 parent class for all fmulcd scenes
"""
class PiScene(ui.Scene):
    def __init__(self, frame=None, name='PiScene'):

        ui.Scene.__init__(self, frame)

        self.name = name
        self.margins = 15
        self.btn_size = 45
        self.margins_bottom = 10
        self.has_nav = False
        self.is_mpd_listener = False
        self.label_height = 45
        self.controls_on = False
        self.modal_left_right_margin = 0
        self.modal_top_bottom_margin = 0
        self.music_directory = '/var/lib/mpd/music/'
        self.main_active = False
        self.sidebar_index = 0
        self.active_sidebar_btn = 0

        self.sidebar = self.make_sidebar()
        self.main = self.make_main()
        #self.controls = self.make_controls()

        self.add_child(self.sidebar)
        self.add_child(self.main)

        self.on_nav_change = callback.Signal()

    """
    make_sidebar
    """
    def make_sidebar(self):

        self.sidebar_btns = []

        sidebar = ui.View(
            ui.Rect(
                self.margins,
                self.margins,
                self.frame.width,
                self.btn_size
            )
        )

        btns = [
            ('NowPlaying','cd'),
            ('Albums','list'),
            ('Radio','music'),
            ('Settings','cog'),
            ('Controls','volume-down')
        ]

        btn_x = 0

        for btn_data in btns:
            btn = ui.IconButton(
                ui.Rect(
                    btn_x,0,
                    self.btn_size,
                    self.btn_size
                ),
                btn_data[1]
            )
            btn_x = btn_x + self.btn_size + self.margins
            btn.on_clicked.connect(self.sidebar_btn_clicked)
            btn.tag_name = btn_data[0]

            if btn_data[0] == self.name:
                btn.state = 'selected'
            sidebar.add_child(btn)
            self.sidebar_btns.append(btn)

        return sidebar

    """
    make_main
    """
    def make_main(self):

        main = PiMain( #ui.View(
            ui.Rect(
                0,
                self.sidebar.frame.bottom,
                self.frame.width,
                self.frame.height - self.sidebar.frame.height # - self.margins - self.margins
            )
        )

        return main

    """
    make_controls
    """
    def make_controls(self):

        controls = PiControls(ui.Rect(
            self.modal_left_right_margin,
            self.modal_top_bottom_margin,
            self.frame.width - self.modal_left_right_margin * 2,
            self.frame.height - self.modal_top_bottom_margin * 2
        ))

        controls.on_dismissed.connect(self.onControlsDismissed)

        return controls

    """
    onControlsDismissed
    """
    def onControlsDismissed(self):
        self.controls_on = False

    """
    sidebar_btn_clicked
    """
    def sidebar_btn_clicked(self, btn, mouse_btn):
        btn.state = 'normal'
        self.main_active = True
        self.on_main_active()
        self.on_nav_change(btn.tag_name)

    """
    key_down
    """
    def key_down(self, key, code):
        #print 'key_down key: ' + str(key) + ' code: ' + str(code)

        ui.Scene.key_down(self,key,code)

        if self.main_active == True:
            self.key_down_main(key)
        else:
            self.key_down_sidebar(key)

    """
    key_down_main
    """
    def key_down_main(self, key):
        if key == pygame.K_LEFT:
            self.main_active = False
            self.active_sidebar_btn = 0
            self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

    """
    key_down_sidebar
    """
    def key_down_sidebar(self, key):
        if key == pygame.K_LEFT:
            if self.active_sidebar_btn > 0:
                if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
                    self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
                else:
                    self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
                self.active_sidebar_btn = self.active_sidebar_btn - 1
                self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

        elif key == pygame.K_RIGHT:
            if self.active_sidebar_btn < (len(self.sidebar_btns) - 1):
                if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
                    self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
                else:
                    self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
                self.active_sidebar_btn = self.active_sidebar_btn + 1
                self.sidebar_btns[self.active_sidebar_btn].state = 'focused'

        elif key == pygame.K_UP:
            pass

        elif key == pygame.K_DOWN:
            self.main_active = True
            if self.sidebar_btns[self.active_sidebar_btn].tag_name == self.name:
                self.sidebar_btns[self.active_sidebar_btn].state = 'selected'
            else:
                self.sidebar_btns[self.active_sidebar_btn].state = 'normal'
            self.on_main_active()

        elif key == pygame.K_RETURN:
            self.sidebar_btn_clicked(self.sidebar_btns[self.active_sidebar_btn], False)

    """
    on_main_active
    """
    def on_main_active(self):
        pass

    """
    refresh
    """
    def refresh(self):
        self.active_sidebar_btn = self.sidebar_index
        self.main_active = True
        self.on_main_active()

    """
    entered
    """
    def entered(self):
        logger.debug(self.name + ' entered.')
        ui.Scene.entered(self)

    """
    update
    """
    def update(self):
        #ui.Scene.update(self, dt)
        if self.is_mpd_listener == True:
            if mpd.status_get():
                self.on_mpd_update()

    """
    on_mpd_update
    """
    def on_mpd_update(self):
        pass

class PiMain(ui.View):
    def __init__(self, frame=None):
        ui.View.__init__(self, frame)

    """
    draw
     if we have been updated or forced, force children to redraw and redraw ourselves
     else only redraw if any children have been redrawn themselves
    """
    def draw(self, force=False):
        if self.hidden:
            return False

        if self.updated or force:
            self.updated = False

            for child in self.children:
                if not child.hidden:
                    child.draw(True)
                    self.surface.blit(child.surface, child.frame.topleft)
                    if child.border_color and child.border_widths is not None:
                        if (type(child.border_widths) is int and child.border_widths > 0):
                            pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)
            return True

        else:
            drawn = False

            for child in self.children:
                if not child.hidden:
                    if child.draw():
                        #if child.__class__.__name__ != 'View':
                        #print 'Pi Main redrawing ' + child.__class__.__name__
                        drawn = True
                        self.surface.blit(child.surface, child.frame.topleft)
                        if child.border_color and child.border_widths is not None:
                            if (type(child.border_widths) is int and child.border_widths > 0):
                                pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)

            return drawn
