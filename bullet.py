from settings import * 
from utils import mask_collision
from effects import Effect

class Bullet():
    def __init__(self, app, pos, vel, dur, speed, image) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.vel: vec2 = vel
        self.dur: float = dur
        self.image = image
        self.speed: float = speed
        self.mask = pg.mask.from_surface(self.image)
        self.done = False
        self.size: list = [20, 20]
        self.damage = 40

    def render(self, surf):
        surf.blit(self.image, (self.pos.x, self.pos.y))

    def rect(self):
        return pg.Rect(self.pos.x + 2, self.pos.y + 2, self.size[0], self.size[1])

    def update(self):
        done = False
        self.dur -= self.app.delta_time
        self.pos += self.vel * self.speed * self.app.delta_time

        player_rect = self.rect()
        nearby_tiles = self.get_nearby_tiles()
        for tile_rect in nearby_tiles:
            if player_rect.colliderect(tile_rect[0]):
                self.done = True
                if tile_rect[1]:
                    tile_rect[2].health -= self.damage
                    tile_rect[2].tile_hit(self.vel)
                break

        if self.dur <= 0:
            done = True
        if self.done: 
            done = True
            smoke = Effect(pos=vec2(self.pos.x + 2, self.pos.y - 4), vel=vec2(0), size=[0,0], anim=self.app.assets['effects']['smoke'][0])
            self.app.effects.add(smoke)
        return done
    
    def check_collision(self, enemy):
        bullet_mask, bullet_pos = self.mask_and_pos()
        enemy_mask, enemy_pos = enemy.mask_and_pos()
        if mask_collision(bullet_mask, bullet_pos, enemy_mask, enemy_pos) and not self.done:
            self.done = True
            enemy.take_damage(self)

    def mask_and_pos(self):
        return self.mask, self.pos.copy()

    def get_nearby_tiles(self) -> list:
        nearby_tiles = []
        for offset in [[-1, 0], [-1, -1], [0, -1], [1, -1], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]:
            key = f'{int((self.pos.x + 2) // CELL_SIZE + offset[0])},{int(int((self.pos.y + 2) // CELL_SIZE + offset[1]))}'
            if key in self.app.tile_map.tiles: nearby_tiles.append((self.app.tile_map.tiles[key].rect(), self.app.tile_map.tiles[key].breakable, self.app.tile_map.tiles[key]))
        return nearby_tiles

