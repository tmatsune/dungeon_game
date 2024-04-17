from settings import *
from utils import render_text_2

class Particle():
    def __init__(self, app, pos: vec2, vel: vec2, rad: int, speed: float, dec: int) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.vel: vec2 = vel
        self.speed: float = speed
        self.rad: int = rad
        self.dec: int = dec
        self.done = False

    def update(self, d):
        done = False
        self.pos += self.vel * self.speed
        self.rad += self.dec
        if self.rad <= 0:
            done = True
        return done

    def render(self, surf):
        #pg.draw.circle(surf, RED, (self.pos.x, self.pos.y), self.rad)
        pg.draw.rect(surf, RED, (self.pos.x, self.pos.y, self.rad, self.rad))

class ImgParticle(Particle):
    def __init__(self, app, pos: vec2, vel: vec2, rad: int, speed: float, dec: int, image, rot, scale) -> None:
        super().__init__(app, pos, vel, rad, speed, dec)
        self.image = image
        self.rot = rot
        self.angle = 0
        self.scale = scale

    def render(self, surf):
        img_rect = self.image.get_rect(center = (self.pos.x, self.pos.y))
        image = pg.transform.rotate(self.image, self.angle)
        image = pg.transform.scale(self.image, (self.scale, self.scale))
        surf.blit(image, img_rect)
        
    def update(self):
        self.angle += self.rot
        self.scale += self.dec
        self.pos += self.vel * self.speed
        return self.scale < 6


class FloatParticle():
    def __init__(self, app, vel, pos, speed, image=None) -> None:
        self.app = app
        self.vel = vel
        self.pos = pos
        self.image = image
        self.speed = speed
        self.angle = 0
        self.rot = random.randrange(-4, 4)

    def render(self, surf):
        img_rect = self.image.get_rect(center = (self.pos.x % WIDTH, self.pos.y % HEIGHT))
        image = pg.transform.rotate(self.image, self.angle)
        surf.blit(image, img_rect)

    def update(self):
        done = False
        self.angle += self.rot
        self.pos += self.vel * self.speed
        return done

class DustParticle():
    def __init__(self, app, pos: vec2, vel: vec2) -> None:
        self.app = app
        self.pos = pos
        self.vel = vel
        self.done = False
        self.dur = 0.1
        self.rad = 4
    def update(self):
        done = False
        self.pos += self.vel
        self.dur -= self.app.delta_time
        self.rad -= 1
        if self.rad <= 0:
            done = True

        if self.done: 
            done = True

        return done
    def render(self, surf):
        pg.draw.circle(surf, WHITE, (self.pos.x, self.pos.y), self.rad)


class Spark():
    def __init__(self, pos, angle, speed, color, dec=-.8) -> None:
        self.pos = pos
        self.angle = angle
        self.speed = speed
        self.color = color
        self.dec = dec

    def update(self):
        self.pos.x += self.speed * math.cos(self.angle)
        self.pos.y += self.speed * math.sin(self.angle)

        self.speed = max(0, self.speed + self.dec)
        return not self.speed

    def render(self, surf):
        render_points = [
            (self.pos.x + math.cos(self.angle) * self.speed * 3,
             self.pos.y + math.sin(self.angle) * self.speed * 3),
            (self.pos.x + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5,
             self.pos.y + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5),
            (self.pos.x + math.cos(self.angle + math.pi) * self.speed * 3,
             self.pos.y + math.sin(self.angle + math.pi) * self.speed * 3),
            (self.pos.x + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5,
             self.pos.y + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5),
        ]

        pg.draw.polygon(surf, self.color, render_points)

class TextParticle():
    def __init__(self, pos, text: str, target_pos, n, font) -> None:
        self.pos = pos
        self.text: str = text
        self.target_pos = target_pos
        self.n = n
        self.font = font

    def render(self, surf):
        render_text_2( surf=surf, text=self.text, pos=self.pos, offset=vec2(2,2), size=20, italic=False, rgb=RED, font=self.font)
        render_text_2( surf=surf, text=self.text, pos=self.pos, offset=vec2(0,0), size=20, italic=False, rgb=WHITE, font=self.font)

    def update(self):
        done = False
        self.pos.y += (self.target_pos.y - self.pos.y) / self.n
        if abs(self.pos.y - self.target_pos.y) < 2:
            done = True
        return done

class Shell():
    def __init__(self, app, pos, vel, image) -> None:
        self.app = app
        self.pos = pos
        self.vel = vel
        self.image = image
        self.angle = 0
        self.dur = .4

    def render(self, surf):
        image = pg.transform.rotate(self.image, self.angle)
        img_rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y 
        self.vel.y += .6
        self.angle -= 20
        self.dur -= self.app.delta_time
        return self.dur <= 0

