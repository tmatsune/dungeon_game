from settings import * 
from state_machine import * 
from bullet import Bullet
from effects import AfterEffect, Flash, Effect
from particles import Spark, TextParticle
from utils import distance, mask_collision

class Entity():
    def __init__(self, app, pos, size, entity_type) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.size: tuple = size
        self.state_machine: StateMachine = StateMachine(app, self)
        self.entity_type: str = entity_type
        self.flip = False
        self.vel = vec2(0)
        self.gravity = PLAYER_GRAVITY
        self.velocity = 50
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
        self.directions = [[-1, 0], [-1, -1], [0, -1], [1, -1], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        self.jump_used: bool = False
        self.can_jump_time: float = 0.2

    def update(self):
        self.state_machine.update()

        nearby_tiles = self.get_nearby_tiles()
        
    
    def render(self, surf):
        image = self.state_mcahine.render()
        image = pg.transform.flip(image, self.flip, False)
        surf.blit(image, (self.pos.x, self.pos.y))

        pg.draw.rect(surf, 'red', (self.pos.x, self.pos.y, 40, 40), 2)

    
    def get_nearby_tiles(self) -> list:
        nearby_tiles = []
        for offset in self.directions:
            key = f'{int(self.pos.x // CELL_SIZE + offset[0])},{int(int(self.pos.y // CELL_SIZE + offset[1]))}'
            if key in self.app.tile_map.tiles:
                nearby_tiles.append(self.app.tile_map.tiles[key])
        return nearby_tiles
    
    def rect(self):
        return pg.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])
    
    def jump(self):
        if self.is_on_floor() or self.is_on_wall() or self.can_jump_time > 0:
            self.gravity = -1200
            self.jump_used = True
            if self.is_on_wall():
                if not self.flip:
                    self.x_left = 1.4
                    self.x_right = 0
                if self.flip:
                    self.x_right = 1.4 
                    self.x_left = 0
 
    def add_gravity(self):
        if self.is_on_floor() or self.is_on_wall():
            self.jump_used = False

    def is_on_floor(self): return self.collisions['down']
    def is_on_wall(self): return self.collisions['left'] or self.collisions['right']
    def is_on_ceiling(self): return self.collisions['up']

class Player(Entity):
    def __init__(self, app, pos, size, entity_type) -> None:
        super().__init__(app, pos, size, entity_type)
        self.speed = PLAYER_SPEED
        self.gravity: float = PLAYER_GRAVITY
        self.attack_speed = PLAYER_ATTACK_SPEED
        self.velocity: float = 110
        self.x_left: float = 0
        self.x_right: float = 0
        self.y_up: float = 0
        self.y_down: float = 0
        self.acceleration: float = 1
        self.jump_used: bool= False
        self.dash_timer: float = .4
        self.energy: int = 100
        self.movement: list = [0,0,0,0]
        self.image_scale: vec2 = vec2(1,1)
        self.image_scale_stretched_vertical = vec2(26, 32)
        self.image_offset: vec2 = vec2(14, 0)
        self.jumped: bool = False
        self.dashed: bool = False
        self.jumps: int = 1
        self.zero_gravity_states: set = {'climb', 'dash'}
        self.normal_vel_states: set = {'run', 'idle', 'fall', 'jump'}
        self.attack_angle: float = 0
        self.attack_mask = pg.mask.from_surface(app.assets['effects']['slash']['slash_1'].image())
        self.mask = pg.mask.from_surface(app.assets['player']['idle'].image())
        self.after_timer = 0
        self.effects: set = set()
        self.rotation_angle = 0
        self.weapon = None
        self.hover_timer = 0
        self.health = 100
        self.gems = 0
        self.score = 0
        self.knock_back_vel = vec2(0)
        self.knock_back_speed = 0
        self.hurt = False
        self.hurt_time = 0.6
        self.dead = False

    def update(self):
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}

        if self.movement[0]:
            self.x_right = 1
        if self.movement[1]:
            self.x_left = 1
        
        self.x_left = max(0, self.x_left - 0.1)
        self.x_right = max(0, self.x_right - 0.1)

        self.vel.x = (self.x_right - self.x_left) * self.speed * self.app.delta_time 
        state_type = self.state_type()
        if state_type == 'attack' or state_type == 'climb':
            self.vel.x = 0

        self.vel.x += self.knock_back_vel.x * self.knock_back_speed
        self.pos.x += self.vel.x
        nearby_tiles = self.get_nearby_tiles()
        player_rect = self.rect()
        for tile in nearby_tiles:
            tile_rect = tile.rect()
            if player_rect.colliderect(tile_rect):
                self.can_jump_time = 0.2
                self.jumps = 1
                if self.vel.x > 0:
                    self.collisions['right'] = True
                    player_rect.right = tile_rect.left
                elif self.vel.x < 0:
                    self.collisions['left'] = True
                    player_rect.left = tile_rect.right
                self.pos.x = player_rect.x
        
        self.gravity += self.velocity
        self.vel.y = min(2500, self.gravity) * self.app.delta_time
        if state_type == 'attack' or state_type == 'climb':
            self.gravity = 0
            self.vel.y = 0
        self.vel.y += self.knock_back_vel.y * self.knock_back_speed
        self.pos.y += self.vel.y
        nearby_tiles = self.get_nearby_tiles()
        player_rect = self.rect()
        for tile in nearby_tiles:
            tile_rect = tile.rect()
            if player_rect.colliderect(tile_rect):
                if self.vel.y > 0:
                    self.collisions['down'] = True
                    player_rect.bottom = tile_rect.top
                    self.can_jump_time = 0.2
                    self.jumps = 2
                    self.pos.y = player_rect.y
                elif self.vel.y < 0:
                    self.collisions['up'] = True
                    player_rect.top = tile_rect.bottom
                    self.pos.y = player_rect.y
        
        self.knock_back_speed = max(0, self.knock_back_speed - 2)

        if self.collisions['down']:
            self.vel.y = 0
            self.gravity = 0
        elif self.collisions['up']:
            self.vel.y = 0

        anim_done = self.state_machine.update()
        if anim_done: 
            self.state_machine.change_state('idle')

        self.dash()
        self.squash_effect()
        self.add_gravity()
        state_type = self.state_type()
        self.can_jump_time -= 0.02

        self.hover()
        self.hurt_timer()
        self.weapon.update()
        self.check_health()
    
    def hover(self):
        self.hover_timer -= self.app.delta_time
        self.hover_timer = max(0, self.hover_timer)

    def render(self, surf):
        for e in self.effects.copy():
            e.render(surf)
            done = e.update(self.app.delta_time)
            if done: self.effects.remove(e)

        image = self.state_machine.render()
        if self.hurt and random.random() > .6:
            image = self.app.assets['ui']['empty']
        image = pg.transform.flip(image, self.flip, False)
        image = pg.transform.scale(image, (self.image_scale.x, self.image_scale.y))
        image = pg.transform.rotate(image, self.rotation_angle)

        img_rect = image.get_rect(center=(self.pos.x + self.image_offset.x, self.pos.y + self.image_offset.y))
        surf.blit(image, img_rect)
        pg.draw.rect(surf, RED, (self.pos.x, self.pos.y, 32, 32), 3)
        self.mask = pg.mask.from_surface(image)

    def jump_attack(self):
        self.gravity = -1200
        self.jumps = 2
        self.weapon.magazine = self.weapon.clip_size
 
    def dash(self):
        self.acceleration = max(1, self.acceleration - .4)
        self.dash_timer -= self.app.delta_time
        if self.dash_timer <= 0 and self.can_dash:
            self.dashed = True

            self.dash_timer = 0.16
            self.app.screenshake = 0

            if self.x_left > self.x_right: self.x_right = 0
            if self.x_right > self.x_left: self.x_left = 0

            self.state_machine.change_state("dash")
            self.energy -= 34
 
        self.can_dash = False

    def state_type(self): return self.state_machine.state.state_type

    def got_hit(self, other):
        for i in range(6):
            speed = random.randrange(6, 8)
            angle = math.atan2(self.pos.y - other.pos.y, self.pos.x - other.pos.x) + random.uniform(-1.2, 1.2)
            spark = Spark(pos=vec2(self.pos.x, self.pos.y), angle=angle, speed=speed, color=RED)
            self.app.particles.add(spark)
        self.app.state_machine.state.flash()
        text_part = TextParticle(pos=vec2(self.pos.x + 16, self.pos.y), text='-' + str(other.damage), target_pos=vec2(self.pos.x, self.pos.y - 26), n=16, font=self.app.fonts['test'])
        self.app.particles.add(text_part)
        self.health -= other.damage

    def enemy_hit(self, angle, damage):
        for i in range(6):
            speed = random.randrange(6, 8)
            angle = angle + random.uniform(-ONEFORTH, ONEFORTH)
            spark = Spark(pos=vec2(self.pos.x, self.pos.y), angle=angle, speed=speed, color=RED)
            self.app.particles.add(spark)
        self.hurt = True
        text_part = TextParticle(pos=vec2(self.pos.x + 16, self.pos.y), text='-' + str(damage), target_pos=vec2(self.pos.x, self.pos.y - 26), n=16, font=self.app.fonts['test'])
        self.app.particles.add(text_part)
        self.health -= damage
    
    def hurt_timer(self):
        if self.hurt:
            self.hurt_time -= self.app.delta_time
            if self.hurt_time <= 0:
                self.hurt = False
                self.hurt_time = 1
        
    def attack_1(self):
        self.state_machine.change_state('attack')
        self.app.screenshake = 6
        pos = vec2(self.pos.x, self.pos.y + 8)
        vel = vec2(0,0)
        if not self.flip:
            pos.x += 30 
            vel.x = 1
        else:
            pos.x -= 12
            vel.x = -1
        flash = Flash(user=self)
        bullet = Bullet(app=self.app, pos=pos, vel=vel, dur=.5, speed=800, image=self.app.assets['bullet'][0])
        self.app.bullets.add(bullet)
        self.app.effects.add(flash)

    def jump(self):
        if self.is_on_floor() or self.is_on_wall() or (self.can_jump_time and self.jumps > 0) or self.state_type() == 'climb':
            #print('jumped', self.can_jump_time)
            if self.state_type() == 'climb':
                if self.movement[0]:  # not self.flip
                    self.x_left = 1.4 if self.movement[0] else 0
                    self.x_right = 0
                if self.movement[1]:  # self.flip
                    self.x_right = 1.4 if self.movement[1] else 0
                    self.x_left = 0
            self.state_machine.change_state("jump")
            self.jumps -= 1
            self.gravity = -1200
            self.jump_used = True
            jump_eff = Effect(pos = vec2(self.pos.x - 6, self.pos.y - 6), vel=vec2(0), size=[0], anim=self.app.assets['effects']['smoke'][1])
            self.app.effects.add(jump_eff)

    def squash_effect(self):
        if not self.is_on_floor() and not self.is_on_wall():
            self.jumped = True
            self.image_scale.x += (self.image_scale_stretched_vertical.x - self.image_scale.x) / 24
            self.image_scale.y += (40 - self.image_scale.y) / 24
        else:
            if self.jumped:
                self.image_scale.x += (40 - self.image_scale.x) / 3
                self.image_scale.y += (28 - self.image_scale.y) / 3

                self.image_offset.y += (18 - self.image_offset.y) / 4
                if abs(self.image_scale.x - 40) < 2 and abs(self.image_scale.y -28) < 2: 
                    self.jumped = False
            else:
                self.image_scale.x += (CELL_SIZE - self.image_scale.x) / 3
                self.image_scale.y += (CELL_SIZE - self.image_scale.y) / 3
                self.image_offset.y += (16 - self.image_offset.y) / 4

    def rotate_jump(self):
        if not self.is_on_floor() and self.state_type() == 'jump' and self.jumps == 0:
            if self.flip: self.rotation_angle += 38
            else: self.rotation_angle -= 38
        else: self.rotation_angle = 0
    
    def pos_copy(self): return self.pos.copy()
    def mask_and_pos(self): return self.mask, vec2(self.pos.x, self.pos.y)
    def middle_pos(self): return vec2(self.pos.x + 16, self.pos.y + 16)
    
    def check_health(self):
        if self.health <= 0:
            self.hurt = False
            self.dead = True
            self.state_machine.change_state('dead')
            self.health = 100
            
    def slow_mo_x(self): return self.vel.x * 0.5
    def slow_mo_y(self): return self.vel.y * 0.5
    
    def reset(self):
        self.weapon.magazine = self.weapon.clip_size
        self.knock_back_speed = 0
        self.knock_back_vel = vec2(0)
        self.movement = [0, 0, 0, 0]
        self.pos = vec2(HALF_WIDTH - 30, HALF_WIDTH - 100)
        self.dead = False
    