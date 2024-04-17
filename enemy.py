from entity import *
from state_machine import *
from particles import Spark, Particle
from objects import Gem
from utils import distance

class Enemy():
    def __init__(self, app, pos, size, entity_type) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.size: tuple = size
        self.enemy_id: int = entity_type
        self.flip = False
        self.vel = vec2(0)
        self.gravity = PLAYER_GRAVITY
        self.velocity = 50
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
        self.directions = [(-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        self.target = app.player
        self.knock_back_vel: vec2 = vec2(0)
        self.knock_back_speed = 400
        self.mask = pg.mask.from_surface(app.assets['enemy'][self.enemy_id]['idle'].image())
        self.health = 100
        self.done = False
        self.hurt = False
        self.hurt_time = 0.2
        self.damage = 20
        self.state_machine: EnemyStateMachine = EnemyStateMachine(app, self)
        self.y_mask_offset = 0

    def update(self): 
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}

    def check_horizontal_collisions(self):
        nearby_tiles = self.get_nearby_tiles()
        player_rect: pg.rect = self.rect()
        for tile_rect in nearby_tiles:
            if player_rect.colliderect(tile_rect):
                self.jumps = 1
                if self.vel.x > 0:
                    player_rect.right = tile_rect.left
                    self.collisions['right'] = True
                if self.vel.x < 0:
                    player_rect.left = tile_rect.right
                    self.collisions['left'] = True
                self.pos.x = player_rect.x
                self.can_jump_time = 0.2

    def check_vertical_collisions(self):
        nearby_tiles = self.get_nearby_tiles()
        player_rect: pg.rect = self.rect()
        for tile_rect in nearby_tiles:
            if player_rect.colliderect(tile_rect):
                if self.vel.y > 0:
                    player_rect.bottom = tile_rect.top
                    self.collisions['down'] = True
                    self.can_jump_time = 0.2
                    self.jumps = 1
                    self.pos.y = player_rect.y
                    self.gravity = 0
                if self.vel.y < 0:
                    player_rect.top = tile_rect.bottom
                    self.collisions['up'] = True
                    self.pos.y = player_rect.y

    def render(self, surf):
        image = self.state_machine.render()
        img_rect = image.get_rect(center = (self.pos.x, self.pos.y))
        if self.hurt and random.random() > .5: image = self.app.assets['ui']['empty']
        surf.blit(image, img_rect)

    def get_nearby_tiles(self) -> list:
        nearby_tiles = []
        for offset in self.directions:
            key = f'{int(self.pos.x // CELL_SIZE + offset[0])},{int(int(self.pos.y // CELL_SIZE + offset[1]))}'
            if key in self.app.tile_map.tiles: nearby_tiles.append(self.app.tile_map.tiles[key].rect())
        return nearby_tiles
    
    def get_nearby_tiles_with_offsets(self):
        nearby_tiles = []
        tile_offsets = set()
        for offset in self.directions:
            key = f'{int(self.pos.x // CELL_SIZE + offset[0])},{int(int(self.pos.y // CELL_SIZE + offset[1]))}'
            if key in self.app.tile_map.tiles: 
                nearby_tiles.append(self.app.tile_map.tiles[key].rect())
                tile_offsets.add(offset)
        return nearby_tiles, tile_offsets
    
    def take_damage(self, bullet):
        self.knock_back_speed = 8
        self.knock_back_vel = bullet.vel.copy().normalize()
        self.health -= bullet.damage
        self.hurt = True

    def hurt_timer(self):
        if self.hurt:
            self.hurt_time -= self.app.delta_time
            if self.hurt_time <= 0:
                self.hurt = False
                self.hurt_time = .2

    def get_angle(self):
        return math.atan2(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
    
    def check_player_collision(self):
        enemy_mask, enemy_pos = self.mask_and_pos()
        player_mask, player_pos = self.target.mask_and_pos()
        if mask_collision(enemy_mask, enemy_pos, player_mask, player_pos) and not self.target.hurt and not self.target.dead:
            p_pos = self.target.pos.y + 16
            e_pos = self.pos.y - self.y_mask_offset
            if self.target.vel.y > 0 and p_pos < e_pos:
                self.knock_back_speed = 8
                self.knock_back_vel = self.target.vel.copy().normalize()
                self.health -= 1000
                self.target.jump_attack()
            else:
                self.target.enemy_hit(math.atan2(self.target.pos.y - self.pos.y, self.target.pos.x - self.pos.x), self.damage)
                self.target.knock_back_speed = 28
                vel = (self.middle_pos() - self.target.middle_pos()).normalize()
                self.target.knock_back_vel = vel * -1
                self.app.screenshake = 8
                self.app.state_machine.state.flash()

    def is_on_floor(self): return self.collisions['down']
    def is_on_wall(self): return self.collisions['left'] or self.collisions['right']
    def is_on_ceiling(self): return self.collisions['up']
    def rect(self): return pg.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])
    def mask_and_pos(self): return self.mask, vec2(self.pos.x, self.pos.y)
    def state_type(self): return self.state_machine.state.state_type
    def should_flip(self):
        if self.target.pos.x > self.pos.x: self.flip = True
        else:self.flip = False

    def middle_pos(self): return vec2(self.pos.x + 16, self.pos.y + 16)
        
'''
    for flying enemy
    1. start with patrol state
    2. if line of sight:
        - change state to chase state
        - will follow last known position(maybe use raycast) 
    3. if collision with tile occurs:
        - if collision is on top or bottom:
            -collison with top or bottom will remain true until (player is on inverse side or going down/up is possible) conditions are met
            - move right or left
            - once time runs out for breadcrumb go back to patrol state
'''
class LandEnemy(Enemy):
    def __init__(self, app, pos, size, entity_type) -> None:
        super().__init__(app, pos, size, entity_type)
        self.enemy_speed = 100
        self.movement = [1, 0]
        self.land_directions = [(-1, 0), (1, 0), (-1, 1),(1, 1)]
        self.y_mask_offset = 0
    
    def render(self, surf):
        image = self.state_machine.render()
        if self.hurt and random.random() > .5: image = self.app.assets['ui']['empty']

        image = pg.transform.flip(image, not self.flip, False)
        img_rect = image.get_rect(center=(self.pos.x + 16, self.pos.y + 16))
        surf.blit(image, img_rect)

        pg.draw.rect(surf, RED, (self.pos.x, self.pos.y, 32, 32), 1)
        self.mask = pg.mask.from_surface(image)

    def update(self):
        done = False
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}

        self.land_movement()
        self.vel.x += self.knock_back_vel.x * self.knock_back_speed
        self.pos.x += self.vel.x
        self.check_horizontal_collisions()
        
        self.gravity += self.velocity
        self.vel.y = min(2500, self.gravity) * self.app.delta_time 
        self.vel.y += self.knock_back_vel.y * self.knock_back_speed
        self.pos.y += self.vel.y 
        self.check_vertical_collisions()
        

        if self.collisions['left']:
            self.movement[0] = 1
            self.movement[1] = 0
        if self.collisions['right']:
            self.movement[0] = 0
            self.movement[1] = 1

        self.knock_back_speed = max(0, self.knock_back_speed - .8)

        if self.health <= 0:
            self.death_animation()
            done = True

        self.check_player_collision()
        self.should_flip()
        return done

    def land_movement(self):
        self.vel.x = (self.movement[0] - self.movement[1]) * self.enemy_speed * self.app.delta_time

        nearby_tiles = set()
        for offset in self.land_directions:
            key = f'{int(self.pos.x // CELL_SIZE + offset[0])},{int(self.pos.y // CELL_SIZE + offset[1])}'
            if key in self.app.tile_map.tiles: 
                nearby_tiles.add(offset)

        if self.movement[0] and (1, 1) not in nearby_tiles:
            self.movement[0] = 0
            self.movement[1] = 1
        elif self.movement[1] and (-1, 1) not in nearby_tiles:
            self.movement[1] = 0
            self.movement[0] = 1

    def should_flip(self):
        if self.movement[0]: self.flip = True
        else: self.flip = False

    def death_animation(self):
        for i in range(12):
            angle = random.random() * math.pi * 2
            speed = random.randrange(8, 10)
            color = WHITE
            spark = Spark(vec2(self.pos.x + 8, self.pos.y + 8), angle, speed, color, dec=-.4)
            self.app.particles.add(spark)
            self.app.play_sound('enemy_exp', 1)
            self.app.screenshake = 6
            self.app.state_machine.state.flash()
        gem = Gem(app=self.app, pos=self.pos.copy(), vel=vec2(random.randrange(-5, 5), -10), image=self.app.assets['objects']['gem_1'])
        self.app.particles.add(gem)

class Grunt(Enemy):
    def __init__(self, app, pos, size, entity_type) -> None:
        super().__init__(app, pos, size, entity_type)
        self.target = app.player
        self.enemy_speed = 100
        self.health = 50
        self.angle = 0
        self.particles = []
        self.part_timer = 0.2 
        self.damage = 100
        self.y_mask_offset = -16
        self.movement = [1, 0]
        self.line_of_sight = False
        self.last_known_pos = None
        self.last_pos_timer = 1.2
        self.patrol_timer = 1.6
    
    def update(self):
        done = False
        #self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}

        self.vel = self.enemy_movement()
        self.vel.x += self.knock_back_vel.x * self.knock_back_speed
        self.pos.x += self.vel.x * self.enemy_speed * self.app.delta_time
        self.check_horizontal_collisions()

        self.vel.y += self.knock_back_vel.y * self.knock_back_speed
        self.pos.y += self.vel.y * self.enemy_speed * self.app.delta_time
        self.check_vertical_collisions()

        self.knock_back_speed = max(0, self.knock_back_speed - .8)

        self.hurt_timer()
        if self.health <= 0:
            self.done = True
        if self.done: 
            done = True
            self.death_animation()

        self.part_timer -= self.app.delta_time
        if self.part_timer < 0:
            self.add_paritcle(radius=random.randrange(5, 7), speed=1)
            self.part_timer = 0.04
        
        self.check_player_collision()
        self.raycast()
        return done

    def enemy_movement(self):
        vel = vec2(0)
        if self.line_of_sight:
            vel = (self.target.pos - self.pos).normalize()
            self.last_known_pos = self.target.pos.copy()
        elif self.last_known_pos and not self.line_of_sight:
            vel = (self.last_known_pos - self.pos).normalize()
        else:
            self.patrol_timer -= self.app.delta_time
            if self.movement[0]:
                self.angle = 0
            else:
                self.angle = 180
            if self.part_timer <= 0:
                self.patrol_timer = 1.6
                if self.movement[0]:
                    self.movement[0] = 0
                    self.movement[1] = 1
                else:
                    self.movement[0] = 1
                    self.movement[1] = 0
            vel.x = (self.movement[0] - self.movement[1])
            vel.y = 0

        if self.last_known_pos and self.last_pos_timer > 0 and not self.line_of_sight:
            self.last_pos_timer -= self.app.delta_time
            if self.last_pos_timer <= 0:
                self.last_known_pos = None
                self.last_pos_timer = 1.2
        return vel
    
    def death_animation(self):
        for i in range(12):
            angle = random.random() * math.pi * 2
            speed = random.randrange(8, 10)
            color = WHITE
            spark = Spark(vec2(self.pos.x + 8, self.pos.y + 8), angle, speed, color, dec=-.4)
            self.app.particles.add(spark)
            self.app.play_sound('enemy_exp', 1)
            self.app.screenshake = 6
            self.app.state_machine.state.flash()
        gem = Gem(app=self.app, pos=self.pos.copy(), vel=vec2(random.randrange(-5, 5), -10), image=self.app.assets['objects']['gem_1'])
        self.app.particles.add(gem)
    
    def ease_angle(self):
        target = math.degrees(self.get_angle()) - 90
        if not self.line_of_sight and self.last_known_pos:
            angle = math.atan2(self.last_known_pos.x - self.pos.x, self.last_known_pos.y - self.pos.y)
            target = math.degrees(angle) - 90
        if not self.line_of_sight and not self.last_known_pos:
            target = self.angle

        self.angle = target
        self.angle += ( (target) - self.angle) / 10

    def get_angle(self):
        if self.line_of_sight:
            return math.atan2(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
        elif self.last_known_pos:
            return math.atan2(self.last_known_pos.x - self.pos.x, self.last_known_pos.y - self.pos.y)
        else:
            return self.angle
    
    def add_paritcle(self,radius, speed, dec=-.4):
        for i in range(2):
            pos = vec2(random.randrange(-6, 6) + 16 + self.pos.x + math.cos(self.get_angle() - THREEFORTH) * 14, 
                       random.randrange(-6, 6) + 16 + self.pos.y + math.sin(self.get_angle() - THREEFORTH) * -14)
            part = Particle(app=self.app, pos=pos, vel=self.vel * -1, rad=radius, speed=speed, dec=dec)
            self.app.background_effects.add(part)

    def render(self, surf):
        self.ease_angle()
        image = self.state_machine.render()
        img_rect = image.get_rect(center=(self.pos.x + 16, self.pos.y + 16))
        image = pg.transform.rotate(image, self.angle)
        if self.hurt and random.random() > .5: image = self.app.assets['ui']['empty']
        surf.blit(image, img_rect)
        self.mask = pg.mask.from_surface(image)

    def mask_and_pos(self): return self.mask, vec2(self.pos.x, self.pos.y)

    def check_horizontal_collisions(self):
        nearby_tiles, nearby_offsets = self.get_nearby_tiles_with_offsets()
        player_rect: pg.rect = self.rect()
        for tile_rect in nearby_tiles:
            if player_rect.colliderect(tile_rect):
                self.jumps = 1
                if self.vel.x > 0:
                    player_rect.right = tile_rect.left
                    self.collisions['right'] = True
                    self.movement[0] = 0
                    self.movement[1] = 1

                if self.vel.x < 0:
                    player_rect.left = tile_rect.right
                    self.collisions['left'] = True
                    self.movement[0] = 1
                    self.movement[1] = 0

                self.pos.x = player_rect.x
                self.can_jump_time = 0.2

    def check_vertical_collisions(self):
        nearby_tiles, nearby_offsets = self.get_nearby_tiles_with_offsets()
        player_rect: pg.rect = self.rect()
        for tile_rect in nearby_tiles:
            if player_rect.colliderect(tile_rect):
                if self.vel.y > 0:
                    player_rect.bottom = tile_rect.top
                    self.collisions['down'] = True
                    self.pos.y = player_rect.y

                if self.vel.y < 0:
                    player_rect.top = tile_rect.bottom
                    self.collisions['up'] = True
                    self.pos.y = player_rect.y

        down_offsets = {(0,1),(1,1),(-1,1)}
        count = 3
        for offset in down_offsets:
            if offset not in nearby_offsets:
                count -= 1
        if count == 0:
            self.collisions['down'] = False
        if not (self.angle > -180 and self.angle < 0):
            #print(self.angle)
            self.collisions['down'] = False


    def raycast(self):
        angle = math.atan2(self.target.pos.y - self.pos.y, self.target.pos.x - self.pos.x) + .0001
        if angle < 0: angle += 2 * math.pi
        if angle > math.pi * 2: angle -= 2 * math.pi

        horiz_dist = float('inf')
        vert_dist = float('inf')

        player_pos = self.pos.copy()

        horiz_x, horiz_y, horiz_hit = self.check_horizontal(angle, player_pos)
        vert_x, vert_y, vert_hit = self.check_vertical(angle, player_pos)

        horiz_dist = self.distance(player_pos.x, horiz_x, player_pos.y, horiz_y)
        vert_dist = self.distance(player_pos.x, vert_x, player_pos.y, vert_y)
        end_x = 0
        end_y = 0

        if vert_dist < horiz_dist:
            end_x, end_y = vert_x, vert_y
        if horiz_dist < vert_dist:
            end_x, end_y = horiz_x, horiz_y

        if not horiz_hit and not vert_hit:
            tile_key = f'{int(end_x // CELL_SIZE)},{int(end_y // CELL_SIZE)}'
            if tile_key in self.app.tile_map.tiles:
                pass
               #self.app.tile_map.tiles[tile_key].highlight(self.app.display)
            self.line_of_sight = False
        else:
            self.line_of_sight = True


    def check_horizontal(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        a_tan = -1 / math.tan(ray_angle)
        dof = 16
        player_hit = False
    
        if ray_angle > PI: # looking up
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = -CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle < PI: # looking down
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE), int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 15 or ray_pos[1] < -1 or ray_pos[1] > 15:
                break
            if str_ray_pos in self.app.tile_map.tiles:
                break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit
    
    def check_vertical(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        n_tan = -math.tan(ray_angle)
        dof = 16
        player_hit = False

        P2 = math.pi / 2
        P3 = (math.pi * 3) / 2

        if ray_angle > P2 and ray_angle < P3:  # looking left
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = -CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle < P2 or ray_angle > P3:  # looking right
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE), int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            if str_ray_pos in self.app.tile_map.tiles:
                break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit
    
    def distance(self, px1, px2, py1, py2):
        return math.sqrt(pow(px1 - px2, 2) + pow(py1 - py2, 2))

