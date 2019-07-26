import pygame
import render
import theme
import callback
import resource
import kvc

class View(object):
    """A rectangular portion of the window.

    Views may have zero or more child views contained within it.

    Signals

        on_mouse_down(view, button, point)
        on_mouse_up(view, button, point)
        on_mouse_motion(view, point)
        on_mouse_drag(view, point, delta)

        on_key_down(view, key, code)
        on_key_up(view, key)

        on_parented(view)
        on_orphaned(view) (from parent view)

        on_focused(view)
        on_blurred(view)

        on_selected(view)
        on_enabled(view)
        on_disabled(view)
        on_state_changed(view)

    All mouse points passed to event methods and to slots are in local
    view coordinates. Use `to_parent` and `to_window` to convert.

    """

    def __init__(self, frame=None):
        self.frame = frame

        self.parent = None
        self.children = []  # back->front

        self._state = 'normal'
        self._enabled = True
        self.hidden = False
        self.draggable = False

        self.updated = True

        self.shadowed = False
        self.shadow_image = None

        self.on_focused = callback.Signal()
        self.on_blurred = callback.Signal()

        self.on_selected = callback.Signal()
        self.on_enabled = callback.Signal()
        self.on_disabled = callback.Signal()
        self.on_state_changed = callback.Signal()

        self.on_mouse_up = callback.Signal()
        self.on_mouse_down = callback.Signal()
        self.on_mouse_motion = callback.Signal()
        self.on_mouse_drag = callback.Signal()
        self.on_key_down = callback.Signal()
        self.on_key_up = callback.Signal()

        self.on_parented = callback.Signal()
        self.on_orphaned = callback.Signal()

        self.class_name = self.__class__
        
    def layout(self):
        """Call to have the view layout itself.

        Subclasses should invoke this after laying out child
        views and/or updating its own frame.
        """
        
        self.surface = pygame.Surface(self.frame.size, pygame.SRCALPHA, 32)
        self.updated = True

    def size_to_fit(self):
        rect = self.frame
        for child in self.children:
            rect = rect.union(child.frame)
        self.frame = rect
        self.layout()

    def update(self, dt):
        for child in self.children:
            child.update(dt)

    def to_parent(self, point):
        return (point[0] + self.frame.topleft[0],
                point[1] + self.frame.topleft[1])

    def from_parent(self, point):
        return (point[0] - self.frame.topleft[0],
                point[1] - self.frame.topleft[1])

    def from_window(self, point):
        curr = self
        ancestors = [curr]
        while curr.parent:
            ancestors.append(curr.parent)
            curr = curr.parent
        for a in reversed(ancestors):
            point = a.from_parent(point)
        return point

    def to_window(self, point):
        curr = self
        while curr:
            point = curr.to_parent(point)
            curr = curr.parent
        return point

    def mouse_up(self, button, point):
        self.on_mouse_up(self, button, point)

    def mouse_down(self, button, point):
        self.on_mouse_down(self, button, point)

    def mouse_motion(self, point):
        self.on_mouse_motion(self, point)

    # only called on drag event if .draggable is True

    def mouse_drag(self, point, delta):
        self.on_mouse_drag(self, point, delta)

        self.frame.topleft = (self.frame.topleft[0] + delta[0],
                              self.frame.topleft[1] + delta[1])

        if self.parent:
            self.parent._child_dragged(self)

    def key_down(self, key, code):
        self.on_key_down(self, key, code)

    def key_up(self, key):
        self.on_key_up(self, key)

    @property
    def state(self):
        """The state of the view.

        Potential values are 'normal', 'focused', 'selected', 'disabled'.
        """
        return self._state

    @state.setter
    def state(self, new_state):
        if self._state != new_state:
            self._state = new_state
            self.stylize()
            self.on_state_changed()

    def focus(self):
        pass

    def has_focus(self):
        return False

    def focused(self):
        self.state = 'focused'
        self.on_focused()

    def blurred(self):
        self.state = 'normal'
        self.on_blurred()

    def selected(self):
        self.state = 'selected'
        self.on_selected()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, yesno):
        if self._enabled != yesno:
            self._enabled = yesno
            if yesno:
                self.enabled()
            else:
                self.disabled()

    def enabled(self):
        self.state = 'normal'
        self.on_enabled()

    def disabled(self):
        self.state = 'disabled'
        self.on_disabled()

    def stylize(self):
        """Apply theme style attributes to this instance and its children.

        This also causes a relayout to occur so that any changes in padding
        or other stylistic attributes may be handled.
        """
        # do children first in case parent needs to override their style
        for child in self.children:
            child.stylize()
        style = theme.current.get_dict(self)
        for key, val in style.iteritems():
            kvc.set_value_for_keypath(self, key, val)
        self.layout()

    """
    draw
     if we have been updated or force is True, force children to redraw and blit them
     else
      if we have a bg, blit all children if ANY redraw
      else no bg, blit ONLY redrawn children
    """
    def draw(self, force=False):
        if self.hidden:
            return False

        if self.updated or force:
            self.updated = False
           
            if self.background_color is not None:
                    render.fillrect(self.surface, self.background_color, rect=pygame.Rect((0, 0), self.frame.size))

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
           
            if self.background_color is not None:                
                for child in self.children:
                    if not child.hidden:
                        if child.draw():
                            drawn = True

                if drawn:
                    render.fillrect(self.surface, self.background_color, rect=pygame.Rect((0, 0), self.frame.size))

                    for child in self.children:
                        if not child.hidden:
                        
                            self.surface.blit(child.surface, child.frame.topleft)

                            if child.border_color and child.border_widths is not None:
                                if (type(child.border_widths) is int and child.border_widths > 0):
                                    pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)
            
            else:

                for child in self.children:
                    if not child.hidden:
                        if child.draw():
                            drawn = True
                            self.surface.blit(child.surface, child.frame.topleft)

                            if child.border_color and child.border_widths is not None:
                                if (type(child.border_widths) is int and child.border_widths > 0):
                                    pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)

            return drawn

    def get_border_widths(self):
        """Return border width for each side top, left, bottom, right."""
        if type(self.border_widths) is int:   # uniform size
            return [self.border_widths] * 4
        return self.border_widths

    def hit(self, pt):
        """Find the view (self, child, or None) under the point `pt`."""

        if self.hidden or not self._enabled:
            return None

        if not self.frame.collidepoint(pt):
            return None

        local_pt = (pt[0] - self.frame.topleft[0],
                    pt[1] - self.frame.topleft[1])

        for child in reversed(self.children):   # front to back
            hit_view = child.hit(local_pt)
            if hit_view is not None:
                return hit_view

        return self

    def center(self):
        if self.parent is not None:
            self.frame.center = (self.parent.frame.w // 2,
                                 self.parent.frame.h // 2)

    def add_child(self, child):
        assert child is not None
        self.rm_child(child)
        self.children.append(child)
        child.parent = self
        child.parented()
        #import scene
        #if scene.current is not None:
        child.stylize()

    def rm_child(self, child):
        for index, ch in enumerate(self.children):
            if ch == child:
                ch.orphaned()
                del self.children[index]
                break

    def rm(self):
        if self.parent:
            self.parent.rm_child(self)

    def parented(self):
        self.on_parented()

    def orphaned(self):
        self.on_orphaned()

    def iter_ancestors(self):
        curr = self
        while curr.parent:
            yield curr.parent
            curr = curr.parent

    def iter_children(self):
        for child in self.children:
            yield child

    def bring_to_front(self):
        """TODO: explain depth sorting"""
        if self.parent is not None:
            ch = self.parent.children
            index = ch.index(self)
            ch[-1], ch[index] = ch[index], ch[-1]

    def move_to_back(self):
        if self.parent is not None:
            ch = self.parent.children
            index = ch.index(self)
            ch[0], ch[index] = ch[index], ch[0]
