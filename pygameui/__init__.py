"""A simple GUI framework for Pygame.

This framework is not meant as a competitor to PyQt or other, perhaps more
formal, GUI frameworks. Instead, pygameui is but a simple framework for game
prototypes.

The app is comprised of a stack of scenes; the top-most or current scene is
what is displayed in the window. Scenes are comprised of Views which are
comprised of other Views. pygameui contains view classes for things like
labels, buttons, and scrollbars.

pygameui is a framework, not a library. While you write view controllers in the
form of scenes, pygameui will run the overall application by running a loop
that receives device events (mouse button clicks, keyboard presses, etc.) and
dispatches the events to the relevant view(s) in your scene(s).

Each view in pygameui is rectangular in shape and whose dimensions are
determined by the view's "frame". A view is backed by a Pygame surface.
Altering a view's frame requires that you call 'relayout' which will resize the
view's backing surface and give each child view a chance to reposition and/or
resize itself in response.

Events on views can trigger response code that you control. For instance, when
a button is clicked, your code can be called back. The click is a "signal" and
your code is a "slot". The view classes define various signals to which you
connect zero or more slots.

    a_button.on_clicked.connect(click_callback)

"""

AUTHOR = 'Brian Hammond <brian@fictorial.com>'
COPYRIGHT = 'Copyright (C) 2012 Fictorial LLC.'
LICENSE = 'MIT'

__version__ = '0.2.0'

import pygame
import time

from .button import *
from .callback import *
from .dialog import *
from .imageview import *
from .label import *
from .modal import *
from .render import *
from .resource import *
from .scroll import *
from .slider import *
from .view import *

from . import focus
from . import scene
from . import theme

from .scene import Scene

Rect = pygame.Rect
