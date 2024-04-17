from settings import * 
from utils import render_text_2

class UI():
    def __init__(self, app, user) -> None:
        self.app = app
        self.user = user
        self.user_weapon = user.weapon
        self.bullets = self.user_weapon.magazine
        self.bar_image = pg.transform.scale(self.app.assets['ui']['bar'], (480, 80))
        self.shell_image = pg.transform.scale(self.app.assets['ui']['shell'], (36, 26))

        self.bar_target_y = 26

    def render(self, surf):
        bar = 90 * (self.user.health / 100)
        pg.draw.rect(surf, RED, (30, 20, bar, 38), 0, 2, 2, 2, 2)
        pg.draw.rect(surf, WHITE, (30, 20, 90, 38), 3, 2, 2, 2, 2)
        x_pos = 58
        if self.user.health < 100 and self.user.health > 10:
            x_pos = 62
        elif self.user.health < 10:
            x_pos = 66
        render_text_2(surf=surf, text=str(self.user.health), pos=vec2(x_pos, 24), offset=vec2(0,0), size=24,italic=False, rgb=BLACK, font=self.app.fonts['bold'])
        render_text_2(surf=surf, text=str(self.user.health), pos=vec2(x_pos - 2, 22), offset=vec2(0,0), size=24,italic=False, rgb=WHITE, font=self.app.fonts['bold'])


        pg.draw.rect(surf, WHITE, (156, self.bar_target_y, 320, 14), 0, 2, 2, 2, 2)
        pg.draw.rect(surf, RED, (156, self.bar_target_y, 320, 14), 2, 2, 2, 2, 2)
        render_text_2(surf=surf, text='aMMo ' + str(self.user_weapon.magazine), pos=vec2(260, 15), offset=vec2(0,0), size=30,italic=False, rgb=BLACK, font=self.app.fonts['bold'])
        render_text_2(surf=surf, text='aMMo ' + str(self.user_weapon.magazine), pos=vec2(264, 18), offset=vec2(0,0), size=28,italic=False, rgb=RED, font=self.app.fonts['bold'])
        render_text_2(surf=surf, text='aMMo ' + str(self.user_weapon.magazine), pos=vec2(263, 16), offset=vec2(0,0), size=28,italic=False, rgb=WHITE, font=self.app.fonts['bold'])


        render_text_2(surf=surf, text=str(self.user.gems), pos=vec2(513, 20), offset=vec2(0,0), size=34,italic=False, rgb=RED, font=self.app.fonts['bold'])
        render_text_2(surf=surf, text=str(self.user.gems), pos=vec2(511, 18), offset=vec2(0,0), size=34,italic=False, rgb=WHITE, font=self.app.fonts['bold'])
        pg.draw.rect(surf, RED, (510, 56, 110, 2), 0, 1, 1, 1, 1)
        surf.blit(self.app.assets['objects']['gem_1'], (570, 20))

    def update(self):
        self.easing_func()

    def easing_func(self):
        if self.user_weapon.fired:
            self.bar_target_y += (40 - self.bar_target_y) / 1
            self.user_weapon.fired = False
        else:
            self.bar_target_y += (26 - self.bar_target_y) / 1