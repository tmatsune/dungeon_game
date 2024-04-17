from settings import * 
from tile_map import * 
from utils import * 

editor_states: dict = {'add_tile': 0, 'select_tile': 1, 'save_tile_map': 2, 'enter_object_attrs': 3}
top_left = 0
top_center = 1
top_right = 2
mid_left = 3
mid_center = 4
mid_right = 5
bottom_left = 6
bottom_center = 7
bottom_right = 8

class TileEditor():
    def __init__(self) -> None:
        pg.init()
        self.tile_assets = get_tile_images()
    
        self.auto_tile_map: dict = {
            ((0,1), (1, 0)): top_left,
            ((-1,0),(0,1),(1,0)): top_center,
            ((-1,0),(0,1)): top_right,
            ((0,-1),(0,1),(1,0)): mid_left,
            ((-1,0),(0,-1),(0,1),(1,0)): mid_center,
            ((-1,0),(0,-1),(0,1)): mid_right,
            ((0,-1),(1,0)): bottom_left,
            ((-1,0),(0,-1),(1,0)): bottom_center,
            ((-1,0),(0,-1)): bottom_right,
        }

        self.states: list = ['add_tile', 'select_tile', 'save_tile_map']
        self.state: str = editor_states['add_tile']
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock: pg.time = pg.time.Clock()

        self.clicked: bool = False
        self.state_index: int = 0
        self.mouse_button_down: bool = False
        self.right_clicked: bool = False
        self.shift_clicked: bool = False
        self.selected_position: vec2 = vec2(0)
        self.curr_action: set = set()
        self.scene_name = 0

        self.tile_map: TileMap = TileMap(self)

        self.curr_tile: dict = {}
        self.hitable: bool = True
        self.breakable: bool = False
        self.last_tile_added = None

        self.actions_stack: list = []
        self.map_name: list = []

        self.mode = 'edit_mode'
        self.tile_history = TileHistory()

    def update(self):
        self.state_index = self.state_index % len(self.states)
        if self.state != editor_states['enter_object_attrs']: self.state = editor_states[self.states[self.state_index]]

    def render(self):
        self.screen.fill(BG)

        mpos = pg.mouse.get_pos()

        self.tile_map.render_tiles(self.screen)

        render_text(surf=self.screen, text='Current Scene: ' + str(self.scene_name), pos=vec2(420,40), offset=vec2(0,0), size=20, italic=False, rgb=WHITE)
        if self.state == editor_states['enter_object_attrs']:
            render_text(surf=self.screen, text='object attrs', pos=vec2(460,10), offset=vec2(0,0), size=20, italic=False, rgb=WHITE)
        else:
            render_text(surf=self.screen, text=self.states[self.state_index], pos=vec2(460,10), offset=vec2(0,0), size=20, italic=False, rgb=WHITE)

        if self.state == editor_states['add_tile']:
            self.map_name = []
            if self.curr_tile:
                self.screen.blit(self.curr_tile['image'], ( int(mpos[0]), int(mpos[1])) )
            if self.clicked and self.curr_tile:
                self.curr_tile['pos'] = mpos
                self.add_tile() 
            if self.right_clicked:
                self.remove_tile(mpos)
            if self.can_click(self.shift_clicked, 'shift_click'):
                self.get_tiles_chunk(mpos)
        elif self.state == editor_states['select_tile']:
            self.map_name = []
            self.tile_map.tile_edit_mode(self.screen, mpos)
        elif self.state == editor_states['save_tile_map']:
            self.tile_map.tile_save_mode(self.screen, mpos)
        elif self.state == editor_states['enter_object_attrs']:
            self.tile_map.object_attrs_mode(self.screen, mpos)

        if self.hitable: pg.draw.rect(self.screen, GREEN, (WIDTH - 60, HEIGHT - 60, 30, 30))
        else: pg.draw.rect(self.screen, RED, (WIDTH - 60, HEIGHT - 60, 30, 30))
        render_text(surf=self.screen, text='hitable', pos=vec2(490,HEIGHT - 60), offset=vec2(0,0), size=20, italic=False, rgb=WHITE)
    
        if self.breakable: pg.draw.rect(self.screen, GREEN, (WIDTH - 60, HEIGHT - 120, 30, 30))
        else: pg.draw.rect(self.screen, RED, (WIDTH - 60, HEIGHT - 120, 30, 30))
        render_text(surf=self.screen, text='breakable', pos=vec2(470,HEIGHT - 120), offset=vec2(0,0), size=20, italic=False, rgb=WHITE)

        pg.display.flip()
        pg.display.update()

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
 
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RIGHT:
                    self.state_index += 1
                if e.key == pg.K_LEFT:
                    self.state_index -= 1
                if e.key == pg.K_UP:
                    self.hitable = not self.hitable
                if e.key == pg.K_DOWN:
                    self.breakable = not self.breakable
                if self.state == editor_states['save_tile_map'] or self.state == editor_states['enter_object_attrs']:
                    if e.key == pg.K_BACKSPACE:
                        if len(self.map_name) > 0: self.map_name.pop()
                    elif e.key == pg.K_RSHIFT:
                        new_scene_name = self.convert_to_str()
                        self.scene_name = int(new_scene_name)
                    elif e.key == pg.K_RETURN:
                        name = self.convert_to_str()
                        if self.state == editor_states['save_tile_map']: self.save_map(map=name)
                        else: self.save_object_attrs(new_scene=name)
                    else:
                        let = e.unicode
                        self.map_name.append(let)   

                if self.state == editor_states['add_tile']:
                    if e.key == pg.K_a:
                        tile_key, tile, tile_type = self.tile_history.back()
                        if tile_type == 'tile':
                            if tile_key in self.tile_map.tiles:
                                del self.tile_map.tiles[tile_key]
                        elif tile_type == 'object':
                            if tile_key in self.tile_map.objects:
                                del self.tile_map.objects[tile_key]
                    if e.key == pg.K_d:
                        tile_key, tile, tile_type = self.tile_history.forward()
                        if tile_type == 'tile':
                            self.tile_map.tiles[tile_key] = tile
                        elif tile_type == 'object':
                            self.tile_map.objects[tile_key] = tile
                        
                if self.state == editor_states['add_tile']:
                    if e.key == pg.K_LSHIFT:
                        self.shift_clicked = True     
            if e.type == pg.KEYUP:
                if self.state == editor_states['add_tile']:
                    if e.key == pg.K_LSHIFT:
                        self.shift_clicked = False

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.state == editor_states['select_tile']:
                        self.clicked = True
                        self.mouse_button_down = True
                    elif self.state == editor_states['add_tile']:
                        self.clicked = True
                    elif self.state == editor_states['save_tile_map']:
                        self.clicked = True

                if e.button == 3:
                    if self.state == editor_states['add_tile']:
                        self.right_clicked = True

            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    if self.state == editor_states['select_tile']:
                        self.mouse_button_down = False
                        self.clicked = False
                    elif self.state == editor_states['add_tile']:
                        self.clicked = False
                        if len(self.curr_tile) > 4 and self.curr_tile['type_id'] == 'door':
                            self.state = editor_states['enter_object_attrs']
                    elif self.state == editor_states['save_tile_map']:
                        self.clicked = False

                if e.button == 3:
                    if self.state == editor_states['add_tile']:
                        self.right_clicked = False
    
    def init_scene(self):
        pass
    
    def add_tile(self):
        if len(self.curr_tile) > 3:
            tile_image = self.curr_tile['image']
            pos = vec2(int(self.curr_tile['pos'][0] // CELL_SIZE), int(self.curr_tile['pos'][1] // CELL_SIZE))
            tile_category = self.curr_tile['tile_category']
            tile_type = self.curr_tile['type_id']
            tile_id = int(self.curr_tile['num_id'])
            size = [tile_image.get_width(), tile_image.get_height()]
            key = f'{int(pos[0])},{int(pos[1])}'
            if key not in self.tile_map.tiles and key not in self.tile_map.objects:
                if self.hitable:
                    new_tile = Tile(app=self, pos=pos, size=size, tile_category=tile_category, type_id=tile_type, num_id=tile_id, hitable=self.hitable, breakable=self.breakable)
                    self.tile_map.tiles[key] = new_tile
                    self.last_tile_added = new_tile
                    self.tile_history.new_tile(key, new_tile, 'tile')
                else:
                    new_object = Object(app=self, pos=pos, size=size, object_category=tile_category, object_type=tile_type, object_id=tile_id)
                    self.tile_map.objects[key] = new_object
                    self.last_tile_added = new_object
                    self.tile_history.new_tile(key, new_object, 'object')

    def remove_tile(self, mpos):
        key = f'{int(mpos[0] // CELL_SIZE)},{int(mpos[1] // CELL_SIZE)}'
        if self.hitable:
            if key in self.tile_map.tiles:
                del self.tile_map.tiles[key]
            for att in self.tile_map.enemy_attacks:
                if att.key == key:
                    self.tile_map.enemy_attacks.remove(att)
                    break
        else:
            if key in self.tile_map.objects:
                del self.tile_map.objects[key]

    def save_map(self, map):
        save_path_name = SCENE_PATH + map
        self.tile_map.save_tile_map(save_path_name)

    def save_object_attrs(self, new_scene):
        if self.last_tile_added != None:
            key = f'{int(self.last_tile_added.pos.x)},{int(self.last_tile_added.pos.y)}'
            if key in self.tile_map.objects:
                self.tile_map.objects[key].scene_lookup = int(new_scene)
        self.map_name = []
        self.last_tile_added = None
        self.state = editor_states['add_tile']

    def can_click(self, pressed: bool, action: str):
        if pressed and action not in self.curr_action:
            self.curr_action.add(action)
            return True
        elif not pressed and action in self.curr_action:
            self.curr_action.remove(action)
            return False
        return False
    
    def get_tiles_chunk(self, mpos):
        key = f'{int(mpos[0] // CELL_SIZE)},{int(mpos[1] // CELL_SIZE)}'
        tiles = []
        visit = set()
        if key in self.tile_map.tiles:
            self.get_tiles(int(mpos[0]//CELL_SIZE), int(mpos[1]//CELL_SIZE), tiles, visit)
        for tile in tiles:
            neighbors = self.get_neighbors(int(tile.pos.x), int(tile.pos.y), tiles)
            if neighbors in self.auto_tile_map:
                tile.num_id = self.auto_tile_map[neighbors]
                tile.tile_image = self.tile_assets[tile.tile_category][tile.type_id][tile.num_id]

    def get_tiles(self, c: int, r: int, curr_tiles: list, visit: set):
        key = f'{c},{r}'
        if key in visit or key not in self.tile_map.tiles: return
        visit.add(key)
        curr_tiles.append(self.tile_map.tiles[key])
        up_key = f'{c},{r - 1}'
        down_key = f'{c},{r + 1}'
        left_key = f'{c - 1},{r}'
        right_key = f'{c + 1},{r}'
        if up_key in self.tile_map.tiles:
            self.get_tiles(c, r - 1, curr_tiles, visit)
        if down_key in self.tile_map.tiles:
            self.get_tiles(c, r + 1, curr_tiles, visit)
        if left_key in self.tile_map.tiles:
            self.get_tiles(c - 1, r, curr_tiles, visit)
        if right_key in self.tile_map.tiles:
            self.get_tiles(c + 1, r, curr_tiles, visit)

    def get_neighbors(self, c, r, tiles):
        neighbors = []
        up_key = f'{c},{r - 1}'
        down_key = f'{c},{r + 1}'
        left_key = f'{c - 1},{r}'
        right_key = f'{c + 1},{r}'
        if up_key in self.tile_map.tiles: neighbors.append((0,-1))
        if down_key in self.tile_map.tiles: neighbors.append((0,1))
        if left_key in self.tile_map.tiles: neighbors.append((-1,0))
        if right_key in self.tile_map.tiles: neighbors.append((1,0))
        return tuple(sorted(neighbors))
    
    def get_tile_images(self):
        tile_images: dict = {}
        tile_categories = os.listdir('images/tiles')
        for i in range(len(tile_categories)):
            tile_images[tile_categories[i]] = {}
            tiles_types = os.listdir('images/tiles/' + tile_categories[i])
            for j in range(len(tiles_types)):
                tile_images[tile_categories[i]][tiles_types[j]] = {}
                tile_ids = os.listdir('images/tiles/' + tile_categories[i] + '/' + tiles_types[j])
                tile_ids.reverse()
                for k in range(len(tile_ids)):
                    tile_images[tile_categories[i]][tiles_types[j]][k] = load_image(TILE_PATH + f'main/tile/{tile_ids[k]}', 1)
        return tile_images
    
    def convert_to_str(self) -> str:
        res = ''
        for let in self.map_name: res += let
        self.map_name = []
        return res

    def run(self):
        while True:
            self.render()
            self.check_inputs()
            self.update()

if __name__ == '__main__':
    tile_editor = TileEditor()
    tile_editor.run()