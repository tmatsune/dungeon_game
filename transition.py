from settings import * 
from utils import render_text_2

class Transition():
    def __init__(self, type) -> None:
        self.type = type

class SweepIn(Transition):
    def __init__(self, type) -> None:
        super().__init__(type)
        self.fade_surf = pg.Surface((WIDTH + 300, HEIGHT))
        self.alpha = 255
        self.fade_speed = 500
        self.x_offset = -WIDTH - 300
        self.full_screen = False

    def render(self, surf):
        self.fade_surf.fill(BLACK)
        self.fade_surf.set_alpha(self.alpha)
        surf.blit(self.fade_surf, (self.x_offset,0))

    def update(self, delta):
        done = False
        self.x_offset += 40
        #self.alpha -= self.fade_speed * delta
        if self.x_offset > -10: self.full_screen = True
        if self.x_offset > WIDTH: done = True
        return done
    
class FadeOut(Transition):
    def __init__(self, type) -> None:
        super().__init__(type)
        self.fade_surf = pg.Surface((WIDTH, HEIGHT))
        self.alpha = 255
        self.fade_speed = 900

    def render(self, surf):
        self.fade_surf.fill(BLACK)
        self.fade_surf.set_alpha(self.alpha)
        surf.blit(self.fade_surf, (0,0))

    def update(self, delta):
        done = False
        self.alpha -= self.fade_speed * delta
        if self.alpha < 0:
            done = True
        return done
    
class ResetTransition(Transition):
    def __init__(self, type, player) -> None:
        super().__init__(type)
        self.player = player
        self.fade_surf = pg.Surface((WIDTH, HEIGHT))
        self.alpha = 0
        self.fade_out_speed = 400
        self.fade_in_speed = 600
        self.state = 'fade_in'
        self.font_color_1 = [0, 0, 0]
        self.font_color_2 = [0, 0, 0]
        self.first = True

    def render(self, surf):
        self.fade_surf.fill(BLACK)
        self.fade_surf.set_alpha(self.alpha)
        surf.blit(self.fade_surf, (0, 0))
        render_text_2(surf=surf, text='YOU DIED', pos=vec2(HALF_WIDTH - 180, HALF_HEIGHT - 122), offset=vec2(0, 0), size=70, italic=False, rgb=(self.font_color_1[0], self.font_color_1[1], self.font_color_1[2]),  font='font/test.ttf')
        render_text_2(surf=surf, text='YOU DIED', pos=vec2(HALF_WIDTH - 180, HALF_HEIGHT - 130), offset=vec2(0, 0), size=70, italic=False, rgb=self.font_color_2,  font='font/test.ttf')

    def update(self, delta):
        done = False
        if self.state == 'fade_in':
            if self.font_color_1[0] != LIGHT_RED[0]: self.font_color_1[0] += 1
            if self.font_color_1[1] != LIGHT_RED[1]: self.font_color_1[1] += 1
            if self.font_color_1[2] != LIGHT_RED[2]: self.font_color_1[2] += 1
            self.alpha += self.fade_in_speed * delta

            if self.alpha >= 255:
                self.state = 'fade_out'
                if self.player.dead: 
                    self.player.reset()

        elif self.state == 'fade_out':
            self.alpha -= self.fade_out_speed * delta
            if self.alpha < 0:
                done = True
        return done



