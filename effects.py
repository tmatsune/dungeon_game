from settings import *
from particles import Spark

class Effect():
    def __init__(self, pos: vec2, vel: vec2, size: list, anim) -> None:
        self.pos: vec2 = pos
        self.vel: vec2 = vel
        self.size: list[int] = size
        self.anim = anim.copy()
        self.disp_image = self.anim.image()
        self.size = [self.disp_image.get_width(), self.disp_image.get_height()]

    def update(self, delta):
        done = False
        anim_done = self.anim.update(delta)
        if anim_done: done = True
        return done

    def render(self, surf):
        eff_image = self.anim.image()
        surf.blit(eff_image, (self.pos.x, self.pos.y))

class AfterEffect():
    def __init__(self, app, pos, vel, image, dur = 0.08) -> None:
        self.app = app
        self.pos = pos
        self.vel = vel
        self.image = image.image()
        self.dur = dur

    def render(self, surf):
        surf.blit(self.image, (self.pos.x, self.pos.y))

    def update(self, delta):
        done = False
        self.dur -= delta
        if self.dur <= 0:
            done = True
        return done
    
class Flash():
    def __init__(self, user) -> None:
        self.user = user
        self.dur = .1
        self.rad_1 = 14
        self.rad_2 = 10

    def render(self, surf):
        x_offset = -8 if self.user.flip else 34
        pg.draw.circle(surf, LIGHT_RED, (self.user.pos.x + x_offset, self.user.pos.y + 20), self.rad_1)
        pg.draw.circle(surf, WHITE, (self.user.pos.x + x_offset, self.user.pos.y + 20), self.rad_2)

    def update(self, delta):
        self.rad_1 += 1
        self.rad_2 += 1
        if self.rad_1 > 16:
            return True
        return False

class Background():
    def __init__(self, app) -> None:
        self.app = app
        self.bg_surf = pg.Surface((WIDTH, HEIGHT))
        self.alpha = 0

    def render(self, surf):
        if self.alpha > 10:
            self.bg_surf.fill(LIGHT_RED)
            self.bg_surf.set_alpha(self.alpha)
            surf.blit(self.bg_surf, (0, 0))

    def update(self):
        if self.alpha > 0:
            self.alpha -= 10

    def flash(self):
        self.alpha = 120

class Explosion():
    def __init__(self, app, pos) -> None:
        self.app = app
        self.pos = pos
        self.parts = []
        self.sparks = set()
        self._init_parts()
    
    def _init_parts(self):
        circle_1 = {'type': 'circle', 'radius': 8, 'target_radius': 110, 'color': WHITE, 'color_2': RED, 'inc': 6, 'width': 3}
        circle_2 = {'type': 'circle', 'radius': 8, 'target_radius': 70, 'color': WHITE, 'color_2': RED, 'inc': 7, 'width': 2}
        self.parts.append(circle_1)
        self.parts.append(circle_2)
        for i in range(12):
            angle = random.uniform(0, 2*math.pi)
            speed = random.randrange(10, 14)
            color = WHITE
            spark = Spark(vec2(self.pos.x, self.pos.y), angle, speed, color, dec=-.6)
            self.sparks.add(spark)
        self.app.screenshake = 8

        for c in range( int( (self.pos.x - 64) // CELL_SIZE ), int( (self.pos.x + 128) // CELL_SIZE) ):
            for r in range( int((self.pos.y - 64) // CELL_SIZE), int((self.pos.y + 128) // CELL_SIZE) ):
                key = f'{c},{r}'
                if key in self.app.tile_map.tiles:
                    if self.app.tile_map.tiles[key].breakable:
                        self.app.tile_map.tiles[key].health = 0
                        self.app.tile_map.tiles[key].tile_destroyed()
        hit_box = pg.Rect(self.pos.x - 64, self.pos.y - 64, 128, 128)
        for e in self.app.enemies:
            if hit_box.colliderect(e.rect()):
                e.health = 0

    def render(self, surf):
        #pg.draw.rect(surf, ORANGE, (self.pos.x - 64, self.pos.y - 64, 128, 128), 2)
        for part in self.parts.copy():
            #pg.draw.circle(surf, RED, (self.pos.x + 1, self.pos.y + 1), part['radius'] - 2, 2)
            pg.draw.circle(surf, part['color'], (self.pos.x, self.pos.y), part['radius'], part['width'])
            part['radius'] += (part['target_radius'] - part['radius']) / part['inc']
            if abs(part['target_radius'] - part['radius']) < 2:
                self.parts.remove(part)
        for spark in self.sparks.copy():
            spark.render(surf)
            done = spark.update()
            if done: 
                self.sparks.remove(spark)

    def update(self, delta):
        return len(self.sparks) == 0 and len(self.parts) == 0


class CloudExplosion():
    def __init__(self, app, pos) -> None:
        self.app = app
        self.pos = pos

    def render(self, surf):
        pass

    def update(self):
        pass
    


    