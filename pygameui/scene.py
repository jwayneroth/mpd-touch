import view
import callback
import render
import pygame

class Scene(view.View):
    """A view that takes up the entire window content area."""

    def __init__(self, frame=None):
        view.View.__init__(self, frame)

    def key_down(self, key, code):
        import pygame

        if key == pygame.K_ESCAPE:
            pop()

    def exited(self):
        #print 'ui.Scene::exited'
        pass

    """
    draw
     override for scene
     if we have been updated or forced, force children to redraw and redraw ourselves
     else only redraw if any children have been redrawn themselves
     ONLY FILL BG IF WE HAVE BEEN UPDATED
    """
    def draw(self, force=False):
        if self.hidden:
            return False

        if self.updated or force:
            self.updated = False
           
            if self.background_color is not None:
                #print 'Scene filling BG'
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

            for child in self.children:
                if not child.hidden:
                    if child.draw():
                        drawn = True
                        self.surface.blit(child.surface, child.frame.topleft)
                        if child.border_color and child.border_widths is not None:
                            if (type(child.border_widths) is int and child.border_widths > 0):
                                pygame.draw.rect(self.surface, child.border_color, child.frame, child.border_widths)

            return drawn


    def entered(self):
        self.updated = True
        self.stylize()
