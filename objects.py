from settings import * 
from utils import distance

class Door():
    def __init__(self, app, pos, size, next_scene, door_id, vertical, key,hidden=False) -> None:
        self.app = app
        self.pos = pos
        self.size = size
        self.next_scene = next_scene
        self.hidden = hidden
        self.door_id = door_id
        self.vertical = vertical
        self.can_change_timer = .2
        self.anim = app.assets['door'][door_id]
        self.door_image = self.anim.image()
        self.size = [self.door_image.get_width(), self.door_image.get_height()]
        self.target = app.player
        self.key = key
        self.breakable = False

    def update(self):
        self.can_change_timer = max(self.can_change_timer - self.app.delta_time, 0)
        self.anim.update(self.app.delta_time)
        door_rect = self.rect()
        target_rect = self.target.rect()
        if door_rect.colliderect(target_rect) and self.can_change_timer <= 0 and len(self.app.enemies) == 0:
            if not self.vertical:
                if self.target.pos.x > HALF_WIDTH:
                    self.target.pos.x = 80
                    self.target.pos.y = self.pos.y + (self.size[1] / 2)
                else:
                    self.target.pos.x = WIDTH - 80
                    self.target.pos.y = self.pos.y + (self.size[1] / 2)
            self.app.transition_to_new_scene(self.next_scene)

        if len(self.app.enemies) == 0:
            if self.key in self.app.tile_map.tiles:
                del self.app.tile_map.tiles[self.key]

    def render(self, surf):
        image = self.anim.image()
        surf.blit(image, (self.pos.x, self.pos.y))

    def player_distance(self):
        dist = distance(self.target.pos.copy(), self.pos.copy())

    def rect(self): return pg.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

class Gem():
    def __init__(self, app, pos, vel, image) -> None:
        self.app = app
        self.pos = pos
        self.vel = vel
        self.image = image
        self.image = pg.transform.scale(image, (24, 24))
        self.target = self.app.player
        self.angle = 0
        self.bounces = -10
        self.dur = 2

    def render(self, surf):
        image = pg.transform.rotate(self.image, self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)

    def update(self):
        done = False
        self.angle += 22
        dist = distance(self.target.pos.copy(), self.pos.copy())

        if dist < 30:
            done = True
        elif dist < 80:
            self.pos += (self.target.pos.copy() - self.pos.copy()).normalize() * 6
        else:
            self.pos.x += self.vel.x
            gem_rect = self.rect()
            nearby_tiles = self.get_nearby_tiles()
            for tile_rect in nearby_tiles:
                if gem_rect.colliderect(tile_rect):
                    self.vel.x *= -.4
                    self.pos.x += self.vel.x * 2 
                    break

            self.vel.y += 1
            self.pos.y += self.vel.y
            gem_rect = self.rect()
            nearby_tiles = self.get_nearby_tiles()
            for tile_rect in nearby_tiles:
                if gem_rect.colliderect(tile_rect):
                    self.vel.y = self.bounces
                    self.bounces += 1
                    self.pos.y += self.vel.y * 2
                    break

        self.dur -= self.app.delta_time
        if self.bounces >= 0:
            self.vel.y = 0
        if self.dur <= 0:
            return True
        return done
    
    def rect(self):
        return pg.Rect((self.pos.x, self.pos.y, 24, 24))

    def get_nearby_tiles(self) -> list:
        nearby_tiles = []
        for offset in [[0, 0]]:
            key = f'{int((self.pos.x) // CELL_SIZE + offset[0])},{int(int((self.pos.y) // CELL_SIZE + offset[1]))}'
            if key in self.app.tile_map.tiles:
                nearby_tiles.append(self.app.tile_map.tiles[key].rect())
        return nearby_tiles
