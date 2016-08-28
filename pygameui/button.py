import label
import callback
import theme
import pygame
import view
import imageview

CENTER = 0
LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4
WORD_WRAP = 0
CLIP = 1

"""
Button
A button with a text caption.

 Essentially an interactive label.

 Signals
  on_clicked(button, mousebutton)
"""
class Button(label.Label):
    def __init__(self, frame, caption, halign=CENTER, valign=CENTER, wrap=CLIP):
        if frame.h == 0:
            frame.h = theme.current.button_height
        label.Label.__init__(self, frame, caption,halign, valign,wrap)
        self._enabled = True
        self.on_clicked = callback.Signal()

    def layout(self):
        label.Label.layout(self)
        if self.frame.w == 0:
            self.frame.w = self.text_size[0] + self.padding[0] * 2
            label.Label.layout(self)

    def mouse_up(self, button, point):
        self.on_clicked(self, button)

"""
ImageButton
 A button that uses an image instead of a text caption.
"""
class ImageButton(view.View):
    def __init__(self, frame, image):
        if frame is None:
            frame = pygame.Rect((0, 0), image.get_size())
        elif frame.w == 0 or frame.h == 0:
            frame.size = image.get_size()

        view.View.__init__(self, frame)

        self.on_clicked = callback.Signal()

        self.image_view = imageview.ImageView(pygame.Rect(0, 0, 0, 0), image)
        self.image_view._enabled = False
        self.add_child(self.image_view)

    def layout(self):
        self.frame.w = self.padding[0] * 2 + self.image_view.frame.w
        self.frame.h = self.padding[1] * 2 + self.image_view.frame.h
        self.image_view.frame.topleft = self.padding
        self.image_view.layout()
        view.View.layout(self)

    def mouse_up(self, button, point):
        self.on_clicked(self, button)

"""
IconButton
"""
class IconButton(Button):
    def __init__(self, frame, icon_class='cd', caption=''):
        self.classes = {
            'asterisk'               : u'\u002a',
            'plus'                   : u'\u002b',
            'euro'                   : u'\u20ac',
            'eur'                    : u'\u20ac',
            'minus'                  : u'\u2212',
            'cloud'                  : u'\u2601',
            'envelope'               : u'\u2709',
            'pencil'                 : u'\u270f',
            'glass'                  : u'\ue001',
            'music'                  : u'\ue002',
            'search'                 : u'\ue003',
            'heart'                  : u'\ue005',
            'star'                   : u'\ue006',
            'star-empty'             : u'\ue007',
            'user'                   : u'\ue008',
            'film'                   : u'\ue009',
            'th-large'               : u'\ue010',
            'th'                     : u'\ue011',
            'th-list'                : u'\ue012',
            'ok'                     : u'\ue013',
            'remove'                 : u'\ue014',
            'zoom-in'                : u'\ue015',
            'zoom-out'               : u'\ue016',
            'off'                    : u'\ue017',
            'signal'                 : u'\ue018',
            'cog'                    : u'\ue019',
            'trash'                  : u'\ue020',
            'home'                   : u'\ue021',
            'file'                   : u'\ue022',
            'time'                   : u'\ue023',
            'road'                   : u'\ue024',
            'download-alt'           : u'\ue025',
            'download'               : u'\ue026',
            'upload'                 : u'\ue027',
            'inbox'                  : u'\ue028',
            'play-circle'            : u'\ue029',
            'repeat'                 : u'\ue030',
            'refresh'                : u'\ue031',
            'list-alt'               : u'\ue032',
            'lock'                   : u'\ue033',
            'flag'                   : u'\ue034',
            'headphones'             : u'\ue035',
            'volume-off'             : u'\ue036',
            'volume-down'            : u'\ue037',
            'volume-up'              : u'\ue038',
            'qrcode'                 : u'\ue039',
            'barcode'                : u'\ue040',
            'tag'                    : u'\ue041',
            'tags'                   : u'\ue042',
            'book'                   : u'\ue043',
            'bookmark'               : u'\ue044',
            'print'                  : u'\ue045',
            'camera'                 : u'\ue046',
            'font'                   : u'\ue047',
            'bold'                   : u'\ue048',
            'italic'                 : u'\ue049',
            'text-height'            : u'\ue050',
            'text-width'             : u'\ue051',
            'align-left'             : u'\ue052',
            'align-center'           : u'\ue053',
            'align-right'            : u'\ue054',
            'align-justify'          : u'\ue055',
            'list'                   : u'\ue056',
            'indent-left'            : u'\ue057',
            'indent-right'           : u'\ue058',
            'facetime-video'         : u'\ue059',
            'picture'                : u'\ue060',
            'map-marker'             : u'\ue062',
            'adjust'                 : u'\ue063',
            'tint'                   : u'\ue064',
            'edit'                   : u'\ue065',
            'share'                  : u'\ue066',
            'check'                  : u'\ue067',
            'move'                   : u'\ue068',
            'step-backward'          : u'\ue069',
            'fast-backward'          : u'\ue070',
            'backward'               : u'\ue071',
            'play'                   : u'\ue072',
            'pause'                  : u'\ue073',
            'stop'                   : u'\ue074',
            'forward'                : u'\ue075',
            'fast-forward'           : u'\ue076',
            'step-forward'           : u'\ue077',
            'eject'                  : u'\ue078',
            'chevron-left'           : u'\ue079',
            'chevron-right'          : u'\ue080',
            'plus-sign'              : u'\ue081',
            'minus-sign'             : u'\ue082',
            'remove-sign'            : u'\ue083',
            'ok-sign'                : u'\ue084',
            'question-sign'          : u'\ue085',
            'info-sign'              : u'\ue086',
            'screenshot'             : u'\ue087',
            'remove-circle'          : u'\ue088',
            'ok-circle'              : u'\ue089',
            'ban-circle'             : u'\ue090',
            'arrow-left'             : u'\ue091',
            'arrow-right'            : u'\ue092',
            'arrow-up'               : u'\ue093',
            'arrow-down'             : u'\ue094',
            'share-alt'              : u'\ue095',
            'resize-full'            : u'\ue096',
            'resize-small'           : u'\ue097',
            'exclamation-sign'       : u'\ue101',
            'gift'                   : u'\ue102',
            'leaf'                   : u'\ue103',
            'fire'                   : u'\ue104',
            'eye-open'               : u'\ue105',
            'eye-close'              : u'\ue106',
            'warning-sign'           : u'\ue107',
            'plane'                  : u'\ue108',
            'calendar'               : u'\ue109',
            'random'                 : u'\ue110',
            'comment'                : u'\ue111',
            'magnet'                 : u'\ue112',
            'chevron-up'             : u'\ue113',
            'chevron-down'           : u'\ue114',
            'retweet'                : u'\ue115',
            'shopping-cart'          : u'\ue116',
            'folder-close'           : u'\ue117',
            'folder-open'            : u'\ue118',
            'resize-vertical'        : u'\ue119',
            'resize-horizontal'      : u'\ue120',
            'hdd'                    : u'\ue121',
            'bullhorn'               : u'\ue122',
            'bell'                   : u'\ue123',
            'certificate'            : u'\ue124',
            'thumbs-up'              : u'\ue125',
            'thumbs-down'            : u'\ue126',
            'hand-right'             : u'\ue127',
            'hand-left'              : u'\ue128',
            'hand-up'                : u'\ue129',
            'hand-down'              : u'\ue130',
            'circle-arrow-right'     : u'\ue131',
            'circle-arrow-left'      : u'\ue132',
            'circle-arrow-up'        : u'\ue133',
            'circle-arrow-down'      : u'\ue134',
            'globe'                  : u'\ue135',
            'wrench'                 : u'\ue136',
            'tasks'                  : u'\ue137',
            'filter'                 : u'\ue138',
            'briefcase'              : u'\ue139',
            'fullscreen'             : u'\ue140',
            'dashboard'              : u'\ue141',
            'paperclip'              : u'\ue142',
            'heart-empty'            : u'\ue143',
            'link'                   : u'\ue144',
            'phone'                  : u'\ue145',
            'pushpin'                : u'\ue146',
            'usd'                    : u'\ue148',
            'gbp'                    : u'\ue149',
            'sort'                   : u'\ue150',
            'sort-by-alphabet'       : u'\ue151',
            'sort-by-alphabet-alt'   : u'\ue152',
            'sort-by-order'          : u'\ue153',
            'sort-by-order-alt'      : u'\ue154',
            'sort-by-attributes'     : u'\ue155',
            'sort-by-attributes-alt' : u'\ue156',
            'unchecked'              : u'\ue157',
            'expand'                 : u'\ue158',
            'collapse-down'          : u'\ue159',
            'collapse-up'            : u'\ue160',
            'log-in'                 : u'\ue161',
            'flash'                  : u'\ue162',
            'log-out'                : u'\ue163',
            'new-window'             : u'\ue164',
            'record'                 : u'\ue165',
            'save'                   : u'\ue166',
            'open'                   : u'\ue167',
            'saved'                  : u'\ue168',
            'import'                 : u'\ue169',
            'export'                 : u'\ue170',
            'send'                   : u'\ue171',
            'floppy-disk'            : u'\ue172',
            'floppy-saved'           : u'\ue173',
            'floppy-remove'          : u'\ue174',
            'floppy-save'            : u'\ue175',
            'floppy-open'            : u'\ue176',
            'credit-card'            : u'\ue177',
            'transfer'               : u'\ue178',
            'cutlery'                : u'\ue179',
            'header'                 : u'\ue180',
            'compressed'             : u'\ue181',
            'earphone'               : u'\ue182',
            'phone-alt'              : u'\ue183',
            'tower'                  : u'\ue184',
            'stats'                  : u'\ue185',
            'sd-video'               : u'\ue186',
            'hd-video'               : u'\ue187',
            'subtitles'              : u'\ue188',
            'sound-stereo'           : u'\ue189',
            'sound-dolby'            : u'\ue190',
            'sound-5-1'              : u'\ue191',
            'sound-6-1'              : u'\ue192',
            'sound-7-1'              : u'\ue193',
            'copyright-mark'         : u'\ue194',
            'registration-mark'      : u'\ue195',
            'cloud-download'         : u'\ue197',
            'cloud-upload'           : u'\ue198',
            'tree-conifer'           : u'\ue199',
            'tree-deciduous'         : u'\ue200',
            'cd'                     : u'\ue201',
            'save-file'              : u'\ue202',
            'open-file'              : u'\ue203',
            'level-up'               : u'\ue204',
            'copy'                   : u'\ue205',
            'paste'                  : u'\ue206',
            'alert'                  : u'\ue209',
            'equalizer'              : u'\ue210',
            'king'                   : u'\ue211',
            'queen'                  : u'\ue212',
            'pawn'                   : u'\ue213',
            'bishop'                 : u'\ue214',
            'knight'                 : u'\ue215',
            'baby-formula'           : u'\ue216',
            'tent'                   : u'\u26fa',
            'blackboard'             : u'\ue218',
            'bed'                    : u'\ue219',
            'apple'                  : u'\uf8ff',
            'erase'                  : u'\ue221',
            'hourglass'              : u'\u231b',
            'lamp'                   : u'\ue223',
            'duplicate'              : u'\ue224',
            'piggy-bank'             : u'\ue225',
            'scissors'               : u'\ue226',
            'bitcoin'                : u'\ue227',
            'btc'                    : u'\ue227',
            'xbt'                    : u'\ue227',
            'yen'                    : u'\u00a5',
            'jpy'                    : u'\u00a5',
            'ruble'                  : u'\u20bd',
            'rub'                    : u'\u20bd',
            'scale'                  : u'\ue230',
            'ice-lolly'              : u'\ue231',
            'ice-lolly-tasted'       : u'\ue232',
            'education'              : u'\ue233',
            'option-horizontal'      : u'\ue234',
            'option-vertical'        : u'\ue235',
            'menu-hamburger'         : u'\ue236',
            'modal-window'           : u'\ue237',
            'oil'                    : u'\ue238',
            'grain'                  : u'\ue239',
            'sunglasses'             : u'\ue240',
            'text-size'              : u'\ue241',
            'text-color'             : u'\ue242',
            'text-background'        : u'\ue243',
            'object-align-top'       : u'\ue244',
            'object-align-bottom'    : u'\ue245',
            'object-align-horizontal': u'\ue246',
            'object-align-left'      : u'\ue247',
            'object-align-vertical'  : u'\ue248',
            'object-align-right'     : u'\ue249',
            'triangle-right'         : u'\ue250',
            'triangle-left'          : u'\ue251',
            'triangle-bottom'        : u'\ue252',
            'triangle-top'           : u'\ue253',
            'console'                : u'\ue254',
            'superscript'            : u'\ue255',
            'subscript'              : u'\ue256',
            'menu-left'              : u'\ue257',
            'menu-right'             : u'\ue258',
            'menu-down'              : u'\ue259',
            'menu-up'                : u'\ue260'
        }

        self._icon_class = icon_class

        caption = self.get_caption( icon_class )

        Button.__init__(self, frame, caption)

    def __repr__(self):
        if self._icon_class is None:
            return ''
        return self._icon_class


    @property
    def icon_class(self):
        return self._icon_class

    @icon_class.setter
    def icon_class(self, icon_class):
        self._icon_class = icon_class
        caption = self.get_caption( icon_class )
        self.text = caption
        self.render()


    def get_caption(self, class_name):
        if class_name in self.classes:
            return self.classes[class_name]
        return self.classes['cd']

    def _render(self, text):

        self.text_surfaces, self.text_shadow_surfaces = [], []

        #wants_shadows = (self.text_shadow_color is not None and
        #                 self.text_shadow_offset is not None)

        self.text_size = self._render_line(self._text, None)


    def _render_line(self, line_text, wants_shadows):

        #line_text = u'\u002a'

        try:

            text_surface = self.font.render(line_text, True, self.text_color)

            self.text_surfaces.append(text_surface)

            if wants_shadows:
                text_shadow_surface = self.font.render(line_text, True, self.text_shadow_color)
                self.text_shadow_surfaces.append(text_shadow_surface)

            return text_surface.get_size()

        except:
            return (0,0)
