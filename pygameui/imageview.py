import pygame
import view
import resource

SCALE_TO_FILL = 0
SCALE_TO_FIT = 1

class ImageView(view.View):
    """A view for displaying an image.

    The only 'content scaling mode' currently supported is 'scale-to-fill'.

    """

    def __init__(self, frame, img, content_mode=SCALE_TO_FIT):
        """Create an image view from an image.

        frame.topleft

            where to position the view.

        frame.size

            if (0, 0) the frame.size is set to the image's size;
            otherwise, the image is scaled to this size.

        """

        if img == None:
            img = resource.get_image('images/default_cover_art.png')

        assert img is not None

        if frame is None:
            frame = pygame.Rect((0, 0), img.get_size())
        elif frame.w == 0 and frame.h == 0:
            frame.size = img.get_size()

        view.View.__init__(self, frame)

        self._enabled = False
        self.content_mode = content_mode
        self.image = img

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        #print 'ImageView: new image'
        self._image = new_image

    def layout(self):
        
        assert self.padding[0] == 0 and self.padding[1] == 0
        
        if self.content_mode == SCALE_TO_FILL:
            self._image = resource.scale_image(self._image, self.frame.size)
        elif self.content_mode == SCALE_TO_FIT:
            self._image = resource.scale_to_fit(self._image, self.frame.size)
        else:
            assert False, "Unknown content_mode"
        
        view.View.layout(self)

    def draw(self, force=False):
        self.surface = self._image
        if self.updated or force:
            self.updated = False
            #print 'ImageView::draw returning True'
            return True


def view_for_image_named(image_name):
    """Create an ImageView for the given image."""

    image = resource.get_image(image_name)

    if not image:
        return None

    return ImageView(pygame.Rect(0, 0, 0, 0), image)
