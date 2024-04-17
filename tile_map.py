from settings import * 
from enemy import *
from objects import * 
from particles import Spark, Particle, ImgParticle
from utils import render_text, mask_collision

WINDOW_STATES = {
    'NONE': 0,
    'TILE_CATEGORIES': 1,
    'TILE_TYPES': 2,
    'TILE_IDS': 3,
}
class TileMap():
    def __init__(self, app) -> None:
        self.app = app
        self.tiles: dict = {}
        self.objects: dict = {}
        self.enemy_attacks: set = set()
        self.cached_tiles: dict = {}

        self.tile_categories = [key for key in self.app.tile_assets]
        self.prev_actions: list = []
        self.curr_action: set = set()
        self.select_tile_options = {
            'window_state': WINDOW_STATES['NONE'],
            'show_tile_categories': False,
            'curr_tile_category': None,
            'curr_tile_type': None,
            'curr_tile_id': 0,
        }

        self.maps = os.listdir('scenes')

    def reset_scene(self):      
        self.tiles = {}
        self.objects = {}
        self.enemy_attacks.clear()

    def test_mode(self, surf):
        rows = WIDTH // CELL_SIZE
        cols = WIDTH // CELL_SIZE
        
        for r in range(rows):
            for c in range(cols):
                pg.draw.rect(self.app.display, 'white', (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                if f'{c},{r}' in self.tiles:
                    tile: Tile = self.tiles[f'{c},{r}']
                    tile.test_render(surf)

    def render_tiles(self, surf):
        for key, tile in self.tiles.copy().items():
            tile.render(surf)
            done = tile.update()
            if done: 
                del self.tiles[key]
            #pg.draw.rect(self.app.display, 'white', (tile.pos.x * CELL_SIZE, tile.pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        for key, obj in self.objects.copy().items():
            obj.render(surf)

        for att in self.enemy_attacks.copy():
            att.render(surf)
            done = att.update() if self.app.state_machine.state.state_type == 'play' else False
            if done: 
                self.enemy_attacks.remove(att)

    def load_map(self, path):
        fl = open(path, 'r')
        map_data = json.load(fl)
        fl.close()
        for key, data in map_data['tile_map'].items():
            pos, size, tile_category, type_id, num_id, hitable, breakable = data['pos'], data['size'], data['tile_category'], data['type_id'], data['num_id'], data['hitable'], data['breakable']
            if type_id == 'spikes' and self.app.mode != 'edit_mode':
                self.add_spike(num_id, pos[0], pos[1])
            else:
                nw_tile = Tile(self.app, vec2(pos[0], pos[1]), size, tile_category, type_id, num_id, hitable, breakable)
                self.tiles[key] = nw_tile
        objs = {
            'enemies': [],
            'doors': [],
        }
        for key, data in map_data['tile_objects'].items():
            pos, size, object_category, object_type, object_id = data['pos'], data['size'], data['object_category'], data['object_type'], data['object_id']
            if self.app.mode == 'run_mode':
                next_scene = -1
                vertical = False
                if object_type == 'door':
                    next_scene = data['scenes']
                    vertical = data['vertical']
                self.get_object_for_game(pos, size, object_category, object_type, object_id, objs, next_scene, vertical)
            else:
                test_obj = Object(self.app, vec2(pos[0], pos[1]), size, object_category, object_type, object_id)
                if object_type == 'door':test_obj.scene_lookup = data['scenes']
                self.objects[key] = test_obj
        return objs
    
    def get_object_for_game(self, pos, size, object_category, object_type, object_id, objs, next_scene=-1, vertical=False):
        if object_type == 'door':
            door = Door(app=self.app, pos=vec2(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE), size=[0,0],next_scene=next_scene, door_id=object_id, vertical=vertical, key=f'{int(pos[0])},{int(pos[1])}'  )
            self.tiles[f'{int(pos[0])},{int(pos[1])}'] = door
            objs['doors'].append(door)
        elif object_type == 'enemies':
            enemy = None
            if object_id == 0:
                enemy = Grunt(app=self.app, pos=vec2(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE), size=(CELL_SIZE,CELL_SIZE), entity_type=object_id)
            elif object_id == 1:
                enemy = LandEnemy(app=self.app, pos=vec2(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE), size=(CELL_SIZE, CELL_SIZE), entity_type=object_id)
            else:
                enemy = Grunt(app=self.app, pos=vec2(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE), size=(CELL_SIZE,CELL_SIZE), entity_type=object_id)
            objs['enemies'].append(enemy)

    def save_tile_map(self, path):
        json_tiles = self.convert_tile_map_to_json()
        for att in self.enemy_attacks:
            json_tiles[att.key] = att.json_data()
            print(att)
        json_objects = self.convert_objects_to_json()
        fl = open(path, 'w')
        json.dump({
            'tile_map': json_tiles,
            'tile_objects': json_objects,
        }, fl)
        fl.close()

    def convert_tile_map_to_json(self):
        json_tiles = {}
        for key, tile in self.tiles.items():
            json_tiles[key] = tile.json_data()
        return json_tiles

    def convert_objects_to_json(self):
        json_objects = {}
        for key, obj in self.objects.items():
            json_objects[key] = obj.json_data()
        return json_objects

    def tile_edit_mode(self, surf, mpos):
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)
        pg.draw.rect(surf, LIGHT_GRAY, (0,0,300,HEIGHT))

        print(self.curr_action)

        back_button_clicked = self.button_box(surf, vec2(8,10), [50, 30], 'back', mpos_rect)
        back_button_clicked = self.can_click(back_button_clicked, 'back_button')
        if back_button_clicked:
            if self.select_tile_options['window_state'] == WINDOW_STATES['TILE_TYPES']:
                self.select_tile_options['window_state'] = WINDOW_STATES['NONE']
            elif self.select_tile_options['window_state'] == WINDOW_STATES['TILE_IDS']:
                self.select_tile_options['window_state'] = WINDOW_STATES['TILE_TYPES']

        category_box_clicked = self.button_box(surf, vec2(170,10), [110, 30], 'tile categories', mpos_rect)
        category_box_clicked = self.can_click(category_box_clicked, 'show_category_box_clicked')

        if category_box_clicked:
            if not self.select_tile_options['show_tile_categories']:
                self.select_tile_options['show_tile_categories'] = True
            else:
                self.select_tile_options['show_tile_categories'] = False

        if self.select_tile_options['show_tile_categories']:
            pg.draw.rect(surf, DARK_GRAY, (170,40, 110, 60))
            for i in range(len(self.tile_categories)):
                tile_category_clicked = self.button_box(surf, vec2(170, 12 + (1 + i) * 30), [110, 30], self.tile_categories[i], mpos_rect)
                if tile_category_clicked:
                    self.select_tile_options['window_state'] = WINDOW_STATES['TILE_TYPES']
                    self.select_tile_options['curr_tile_category'] = self.tile_categories[i]

        #CUURENT STATE
        if self.select_tile_options['window_state'] == WINDOW_STATES['TILE_TYPES']:
            #tile_types = os.listdir('images/tiles/' + self.select_tile_options['curr_tile_category'])
            tile_types = [key for key in self.app.tile_assets[self.select_tile_options['curr_tile_category']]]
            for i in range(len(tile_types)):
                tile_type = tile_types[i]
                #exmaple_image_id = int(os.listdir('images/tiles/' + self.select_tile_options['curr_tile_category'] + '/' + tile_type)[-1][0])
                #example_image = self.app.tile_assets[self.select_tile_options['curr_tile_category']][tile_type][exmaple_image_id]
                example_image = self.app.tile_assets[self.select_tile_options['curr_tile_category']][tile_type][0]
                tile_type_clicked = self.tile_button_box(surf, vec2(20, 80 + (1 + i) * 20), example_image, mpos_rect)
                if tile_type_clicked:
                    self.select_tile_options['window_state'] = WINDOW_STATES['TILE_IDS']
                    self.select_tile_options['curr_tile_type'] = tile_type

        elif self.select_tile_options['window_state'] == WINDOW_STATES['TILE_IDS']:
            #tile_ids = os.listdir('images/tiles/' + self.select_tile_options['curr_tile_category'] + '/' + self.select_tile_options['curr_tile_type'])
            tile_ids = [ key for key in self.app.tile_assets[self.select_tile_options['curr_tile_category']][self.select_tile_options['curr_tile_type']] ]
            tiles = self.get_tile_images(tile_ids, self.select_tile_options['curr_tile_type'])
            for i in range(len(tiles)):
                tile_image, tile_category, tile_type, tile_id = tiles[i][0], tiles[i][1], tiles[i][2], tiles[i][3]
                tile_button = self.tile_button_box(surf, vec2(20, i * (CELL_SIZE + 10) + 80), tile_image, mpos_rect)
                if tile_button:
                    self.app.curr_tile = {
                        'image': tile_image,
                        'tile_category': tile_category,
                        'type_id': tile_type,
                        'num_id': tile_id,
                        'hitable': self.app.hitable,
                        'breakable': self.app.breakable,
                        'pos': [0,0]
                    }
    def button_box(self, surf, pos: vec2, size: list, text: str, mpos_rect):
        pg.draw.rect(surf, MID_GRAY, (pos.x, pos.y, size[0], size[1]))
        render_text(surf=surf, text=text, pos=vec2( pos.x + 6 ,pos.y + 6 ), offset=vec2(0,0), size=14, italic=False, rgb=WHITE)
        tile_category_rect = pg.Rect(pos.x, pos.y, size[0], size[1])
        if mpos_rect.colliderect(tile_category_rect):
            pg.draw.rect(surf, WHITE, (pos.x - 1, pos.y - 1, size[0] + 2, size[1] + 2) , 1)
        if mpos_rect.colliderect(tile_category_rect) and self.app.clicked:
            return True
        return False
      
    def tile_button_box(self, surf, pos: vec2, image, mpos_rect, size: list = [CELL_SIZE, CELL_SIZE]):
        surf.blit(image, (pos.x, pos.y))
        tile_rect = pg.Rect(pos.x, pos.y, size[0], size[1])
        if mpos_rect.colliderect(tile_rect): pg.draw.rect(surf, WHITE, (pos.x - 1, pos.y - 1, size[0] + 2, size[1] + 2) , 2)
        if mpos_rect.colliderect(tile_rect) and self.app.clicked: return True
        return False

    def can_click(self, pressed: bool, action: str):
        if pressed and action not in self.curr_action:
            self.curr_action.add(action)
            return True
        elif not pressed and action in self.curr_action:
            self.curr_action.remove(action)
            return False
        return False
    
    def get_tile_images(self, ids_list, tile_type) -> list:
        images = []
        ids_list.sort()
        for i in range(len(ids_list)):
            tile = self.app.tile_assets[self.select_tile_options['curr_tile_category']][tile_type][i]
            images.append( (tile, self.select_tile_options['curr_tile_category'], self.select_tile_options['curr_tile_type'], ids_list[i]) )
        return images
    
    def tile_save_mode(self, surf, mpos):
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)
        pg.draw.rect(surf, LIGHT_GRAY, (0, 0, 400, HEIGHT))

        clear_map_button = self.button_box(surf, vec2(20, 40), [50, 30], 'clear', mpos_rect)     
        if clear_map_button: 
            self.tiles = {}
            self.objects = {}
        for i in range(len(self.maps)):
            map_path = self.maps[i]
            map_clicked = self.button_box(surf, vec2(20, i * (CELL_SIZE + 10) + 80), [110, 30], map_path, mpos_rect)     
            if map_clicked: self.load_map(SCENE_PATH + map_path)
        save_map_button = self.button_box(surf, vec2(220, 40), [50, 30], 'save', mpos_rect)     
        if save_map_button:
            self.app.save_map()
        self.text_box(surf, vec2(220, 100), [100, 30])

    def object_attrs_mode(self, surf, mpos):
        box_width, box_height = 350, 300
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)
        pg.draw.rect(surf, LIGHT_GRAY, ((WIDTH // 2) - (box_width // 2), (HEIGHT // 2) - (box_height // 2), box_width, box_height))

        self.text_box(surf, vec2((WIDTH // 2) - 100, (HEIGHT // 2) - 30), [100, 30])

    def text_box(self, surf, pos: vec2, size: list):
        pg.draw.rect(surf, WHITE, (pos.x, pos.y, size[0], size[1]))
        text = ''
        for let in self.app.map_name: text += let
        render_text(surf=surf, text=text, pos=vec2( pos.x + 6 ,pos.y + 6 ), offset=vec2(0,0), size=14, italic=False, rgb=BLACK)

    def add_spike(self, num_id, pos_x, pos_y): # spikes
        real_pos = vec2(pos_x * CELL_SIZE, pos_y * CELL_SIZE)
        directions = {'vert': False, 'left': False, 'down': False}
        spike = None
        vel = vec2(0)
        if num_id == 4:
            directions['vert'] = True
            if real_pos.y < HALF_HEIGHT:
                directions['down'] = True
                vel.y = 1
            else:
                vel.y = -1
            spike = MovableSpike(app=self.app, pos=real_pos, vel=vel, num_id=num_id, image=self.app.tile_assets['objects']['spikes'][num_id], speed=4, directions=directions)
        elif num_id == 5:
            if real_pos.x > HALF_WIDTH:
                directions['left'] = True
                vel.x = -1
            else:
                vel.x = 1
            spike = MovableSpike(app=self.app, pos=real_pos, vel=vel, num_id=num_id, image=self.app.tile_assets['objects']['spikes'][num_id], speed=4, directions=directions)
        else:
            spike = Spike(app=self.app, pos=real_pos, vel=vec2(0), num_id=num_id, image=self.app.tile_assets['objects']['spikes'][num_id], speed=0)
        self.enemy_attacks.add(spike)


class Tile():
    def __init__(self, app, pos, size, tile_category, type_id, num_id, hitable, breakable=False) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.size: list = size
        self.tile_category: str = tile_category
        self.type_id: str = type_id
        self.num_id: int = num_id
        self.hitable: bool = hitable
        self.breakable: bool = breakable
        self.real_pos: vec2 = vec2(self.pos.x * CELL_SIZE, self.pos.y * CELL_SIZE)
        self.tile_image = self.app.tile_assets[self.tile_category][self.type_id][self.num_id]
        self.health = 100
        self.key = f'{int(pos.x)},{int(pos.y)}'
    
    def render(self, surf):
        surf.blit(self.tile_image, (self.real_pos.x, self.real_pos.y))

    def test_render(self, surf):
        surf.blit(self.tile_image, (self.real_pos.x, self.real_pos.y))

    def highlight(self, surf):
        pg.draw.rect(surf, GREEN, (self.real_pos.x, self.real_pos.y, CELL_SIZE, CELL_SIZE), 2)

    def update(self):
        done = False
        if self.health <= 0:
            done = True
        return done
    
    def tile_hit(self, vel):
        if vel.x > 0:
            for i in range(6):
                angle = random.uniform(2, 4.2)
                speed = random.randrange(6, 10)
                color = WHITE
                spark = Spark(vec2(self.real_pos.x + 8, self.real_pos.y + 8), angle, speed, color)
                self.app.particles.add(spark)
        elif vel.x < 0:
            for i in range(6):
                angle = random.uniform(0, 1) if random.random() > 0.5 else random.uniform(5, 6.2)
                speed = random.randrange(6, 10)
                color = WHITE
                spark = Spark(vec2(self.real_pos.x + 8, self.real_pos.y + 8), angle, speed, color)
                self.app.particles.add(spark)
    
    def tile_destroyed(self):
        for i in range(6):
            part = ImgParticle(app=self.app, pos=vec2(self.real_pos.x + 16 + random.randrange(-8, 8), self.real_pos.y + 16 + random.randrange(-8, 8)), vel=vec2(random.uniform(-1, 1), random.uniform(-1, 1)),
                               rad=2, speed=2, dec=-.2, image=pg.transform.scale(self.app.assets['objects']['rocks'][random.randrange(0, 3)], (10, 10)), rot=random.randrange(-6, 6), scale=10)
            self.app.particles.add(part)

    def json_data(self):
        return { 
            'pos': [self.pos.x, self.pos.y], 
            'size': self.size, 
            'tile_category': self.tile_category,
            'type_id': self.type_id,
            'num_id': self.num_id,
            'hitable': self.hitable,
            'breakable': self.breakable,
            }
    
    def rect(self):
        return pg.Rect(self.real_pos.x, self.real_pos.y, self.size[0], self.size[1])
    
class Spike():
    def __init__(self, app, pos, vel, num_id, image, speed) -> None:
        self.app = app
        self.pos = pos
        self.vel = vel
        self.num_id = num_id
        self.image = image
        self.speed = speed
        self.health = 100
        self.damage = 20
        self.mask = pg.mask.from_surface(image)

    def render(self, surf):
        surf.blit(self.image, (self.pos.x, self.pos.y))

    def update(self):
        done = False
        player_mask, player_pos = self.app.player.mask_and_pos()
        spike_mask, spike_pos = self.mask_and_pos()
        if mask_collision(player_mask, player_pos, spike_mask, spike_pos) and not self.app.player.hurt:
            self.app.player.hurt = True
            self.app.screenshake = 4
            self.app.player.got_hit(self)
            if self.vel != vec2(0):
                self.app.player.knock_back_vel = self.app.player.vel.copy().normalize() * -1 if self.app.player.vel != vec2(0) else vec2(0,-1)
                self.app.player.knock_back_speed = 34
            else:
                self.app.player.knock_back_vel = self.app.player.vel.copy().normalize() * -1 if self.app.player.vel != vec2(0) else vec2(0,-1)
                self.app.player.knock_back_speed = 44
        return done
    
    def rect(self):
        return pg.Rect(self.pos.x, self.pos.y, 32, 32)

    def test_mode(self, surf):
        surf.blit(self.image, (self.pos.x, self.pos.y))

    def mask_and_pos(self): return self.mask, self.pos.copy()

    def middle_pos(self):
        return vec2(self.pos.x + 16, self.pos.y + 16)

class MovableSpike(Spike):
    def __init__(self, app, pos, vel, num_id, image, speed, directions) -> None:
        super().__init__(app, pos, vel, num_id, image, speed)
        self.directions = directions
        self.part_timer = 0.3
        self.particles: set = set()
        if directions['vert']:
            if not directions['down']:
                self.image = pg.transform.flip(self.image, False, True)
        else:
            if directions['left']:
                self.image = pg.transform.flip(self.image, True, False)

    def middle_pos(self): return self.pos.copy()

    def render(self, surf):
        for part in self.particles.copy():
            part.render(surf)
            done = part.update(self.app.delta_time)
            if done:
                self.particles.remove(part)
        img_rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(self.image, img_rect)

    def update(self):
        done = False
        self.pos += self.vel * self.speed
        self.part_timer -= self.app.delta_time
        
        if self.part_timer < 0:
            if self.directions['vert']:
                if self.directions['down']: 
                    self.add_particle(x_offset=random.uniform(-5, 3), y_offset=-12, x_vel=random.uniform(-.2, .2), y_vel=random.uniform(-1, 1), radius=random.randrange(5, 7), speed=1)
                else: 
                    self.add_particle(x_offset=random.uniform(-5, 3), y_offset=10, x_vel=random.uniform(-.2, .2), y_vel=random.uniform(-1, 1), radius=random.randrange(5, 7), speed=1)
            else:
                if self.directions['left']: 
                    self.add_particle(x_offset=12, y_offset=random.uniform(-3, 3), x_vel=random.uniform(-1, 1), y_vel=random.uniform(-.2, .2), radius=random.randrange(5, 7), speed=1)
                else: 
                    self.add_particle(x_offset=-10, y_offset=random.uniform(-3, 3), x_vel=random.uniform(-1, 1), y_vel=random.uniform(-.2, .2), radius=random.randrange(5, 7), speed=1)
            self.part_timer = 0.03

        player_mask, player_pos = self.app.player.mask_and_pos()
        spike_mask, spike_pos = self.mask_and_pos()
        if mask_collision(player_mask, player_pos, spike_mask, spike_pos) and not self.app.player.hurt:
            self.app.player.hurt = True
            self.app.screenshake = 4
            self.app.player.got_hit(self)
            if self.vel != vec2(0):
                #self.app.player.knock_back_vel = self.app.player.vel.copy().normalize() * -1 if self.app.player.vel != vec2(0) else vec2(0,-1)
                vel = (self.middle_pos() - self.app.player.middle_pos()).normalize()
                self.app.player.knock_back_vel = vel * -1
                self.app.player.knock_back_speed = 34
            else:
                #self.app.player.knock_back_vel = self.app.player.vel.copy().normalize() * -1 if self.app.player.vel != vec2(0) else vec2(0,-1)
                vel = (self.middle_pos() - self.app.player.middle_pos()).normalize()
                self.app.player.knock_back_vel = vel * -1
                self.app.player.knock_back_speed = 34

        self.check_borders()

        return done
    
    def add_particle(self, x_offset, y_offset, x_vel, y_vel, radius, speed, dec=-.4):
        for i in range(2):
            pos = vec2(self.pos.x + x_offset, self.pos.y + y_offset)
            part = Particle(app=self.app, pos=pos, vel=vec2(x_vel, y_vel), rad=radius, speed=speed, dec=dec)
            self.particles.add(part)

    def mask_and_pos(self): return self.mask, vec2(self.pos.x - HALF_CELL, self.pos.y - HALF_CELL)

    def check_borders(self):
        if self.directions['vert']:
            if self.directions['down']:
                if self.pos.y > HEIGHT + 40: self.pos.y = -40
            else:
                if self.pos.y < -4: self.pos.y = HEIGHT + 40
        else:
            if not self.directions['left']:
                if self.pos.x > WIDTH: self.pos.x = -40
            else:
                if self.pos.x < -40: self.pos.x = WIDTH + 40

class Object():
    def __init__(self, app, pos, size, object_category, object_type, object_id) -> None:
        self.app = app
        self.pos: vec2 = pos
        self.size: list = size
        self.object_category: str = object_category
        self.object_type: str = object_type
        self.object_id: int = object_id
        self.real_pos: vec2 = vec2(self.pos.x * CELL_SIZE, self.pos.y * CELL_SIZE)
        self.object_image = self.app.tile_assets[self.object_category][self.object_type][self.object_id]
        self.scene_lookup: int = 0

    def render(self, surf):
        surf.blit(self.object_image, (self.real_pos.x, self.real_pos.y))

    def json_data(self):
        data = {
            'pos': [self.pos.x, self.pos.y],
            'size': self.size,
            'object_category': self.object_category,
            'object_type': self.object_type,
            'object_id': self.object_id,
        }
        if self.object_type == 'door': 
            data['scenes'] = self.scene_lookup
            data['vertical'] = False
        return data

    def rect(self): return pg.Rect(self.real_pos.x, self.real_pos.y, self.size[0], self.size[1])

class ListNode:
    def __init__(self, tile_val, tile, tile_type) -> None:
        self.next = None
        self.prev = None
        self.tile_val = (tile_val, tile, tile_type)

class TileHistory():
    def __init__(self) -> None:
        self.curr = ListNode('none', None, 'none')

    def new_tile(self, key, tile, tile_type):
        nw_node = ListNode(key, tile, tile_type)
        nw_node.prev = self.curr
        self.curr.next = nw_node
        self.curr = self.curr.next

    def back(self):
        if not self.curr.prev:
            return self.curr.tile_val
        val_to_ret = self.curr.tile_val
        self.curr = self.curr.prev
        return val_to_ret

    def forward(self):
        if not self.curr.next:
            return self.curr.tile_val
        val_to_ret = self.curr.tile_val
        self.curr = self.curr.next
        return val_to_ret


