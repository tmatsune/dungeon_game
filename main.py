from settings import * 
from tile_map import * 
from animation import *
from entity import * 
from enemy import * 
from transition import * 
from effects import * 
from app_state_machine import *
from weapon import * 
from ui import *
from particles import *
from utils import load_images_horiz, load_image, get_tile_images, load_images_from_folder, render_text_2, get_sound
#Menlo, Monaco, 'Courier New', monospace

class App():
    def __init__(self) -> None:
        pg.init()
        self.game_name = 'DUNGEON GAME'
        self.screen: pg.display = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill((0, 0, 0))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.delta_time: float = 0
        self.clock: pg.time = pg.time.Clock()
 
        self.cam_offset: vec2 = vec2(0)
        self.scroll_offset: vec2 = vec2(0)
        self.movement: list[int] = [0, 0, 0, 0]
        self.screenshake: int = 0
        self.mode = 'run_mode'

        self.assets: dict = {
            'player': {
                'idle': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/idle.png', 1, 4), dur=0.04),
                'hurt': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/idle.png', 1, 1), dur=0.04),
                'run': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/run.png', 1, 4), dur=0.04),
                'jump': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/fall.png', 1, 1), dur=0.04),
                'attack': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/attack.png', 1, 3), dur=0.04, loop=False),
                'fall': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/fall.png', 1, 1), dur=0.04),
                'dash': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/dash.png', 1, 1), dur=0.04),
                'climb': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/climb.png', 1, 4), dur=0.04),
                'dead': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/idle.png', 1, 4), dur=0.08, loop=False),
                'after': Animation(images=load_images_horiz(IMG_PATH + 'player/player_1/after.png', 1, 1), dur=0.04),
            },
            'bullet': {
                0: load_image(IMG_PATH + 'bullets/0.png', 1.4),
            },
            'weapon': {
                0: load_image(IMG_PATH + 'weapon/0.png', 1.4),
            },
            'ui': {
                'shell': load_image(IMG_PATH + 'ui/shell.png', .6),
                'bar': load_image(IMG_PATH + 'ui/bar.png', 1),
                'gem': load_image(IMG_PATH + 'ui/gem.png', 4),
                'empty': load_image(IMG_PATH + 'player/player_1/hurt.png',1)
            },
            'effects': {
                'slash' : {
                    'slash_1': Animation(images=load_images_from_folder(IMG_PATH + 'effects/slash', 4, 3), dur=0.05, loop=False, offset=vec2(14,12))
                },
                'stars':{
                    0: Animation(images=load_images_horiz(IMG_PATH + 'effects/star/0.png', .8, 5), dur=0.05, loop=True, offset=vec2(14, 12)),
                },
                'smoke': {
                    0: Animation(images=load_images_from_folder(IMG_PATH + 'effects/smoke', 1.4, 4), dur=0.03, loop=False),
                    1: Animation(images=load_images_from_folder(IMG_PATH + 'effects/smoke_1', 1.2, 4), dur=0.03, loop=False),
                },
            },
            'enemy': {
                0 : {
                    'idle': Animation(images=load_images_horiz(IMG_PATH + 'enemy/test/idle.png', 1, 1), dur=0.04),
                    'attack': Animation(images=load_images_horiz(IMG_PATH + 'enemy/test/idle.png', 1, 1), dur=0.04),
                    'chase': Animation(images=load_images_horiz(IMG_PATH + 'enemy/test/idle.png', 1, 1), dur=0.04),
                    'hurt': Animation(images=load_images_horiz(IMG_PATH + 'enemy/test/idle.png', 1, 1), dur=0.04),
                },
                1 : {
                    'idle': Animation(images=load_images_horiz(IMG_PATH + 'enemy/land_enemy/idle.png', 1, 1), dur=0.04),
                    'attack': Animation(images=load_images_horiz(IMG_PATH + 'enemy/land_enemy/idle.png', 1, 1), dur=0.04),
                    'chase': Animation(images=load_images_horiz(IMG_PATH + 'enemy/land_enemy/idle.png', 1, 1), dur=0.04),
                    'hurt': Animation(images=load_images_horiz(IMG_PATH + 'enemy/land_enemy/idle.png', 1.4, 1), dur=0.04),
                }
            },
            'door': {
                0: Animation(images=[load_image(TILE_PATH + 'objects/door/0.png', 1)], dur=1),
            },
            'objects': {
                'gem': Animation(images=load_images_horiz(IMG_PATH + 'objects/gem.png', 1, 8), dur=0.08),
                'gem_1': load_image(IMG_PATH + 'objects/gem.png', 1.8),
                'rocks': {
                    0: load_image(IMG_PATH + 'objects/rocks/0.png', .9),
                    1: load_image(IMG_PATH + 'objects/rocks/1.png', .9),
                    2: load_image(IMG_PATH + 'objects/rocks/2.png', .9),
                    3: load_image(IMG_PATH + 'objects/rocks/3.png', 1.4),
                }
            }
        }
        self.sound_assets = {
            'music': get_sound(SOUND_PATH + 'music.mp3'),
            'enemy_exp': get_sound(SOUND_PATH + 'enemy_exp.wav'),
            'gun_shot': get_sound(SOUND_PATH + 'gun_shot.mp3'),
        }
        self.tile_assets = get_tile_images()

        self.tile_map: TileMap = TileMap(self)
        self.player: Entity = Player(app = self, pos = vec2(CELL_SIZE * 4, CELL_SIZE * 4), size=(CELL_SIZE,CELL_SIZE), entity_type='player')
        self.start_weapon = Weapon(app=self, user=self.player, firerate=.08, magazine=10, clip_size=10, damage=20, recharge=.36)
        self.player.weapon = self.start_weapon
        self.ui = UI(app=self, user=self.player)

        self.enemies: set = set()
        self.doors: set = set()
        self.effects: set = set()
        self.bullets: set = set()
        self.particles: set = set()
        self.background_effects: set = set()

        self.curr_scene_num: int = 0

        self.state_machine: AppStateMachine = AppStateMachine(app=self)

        self.state = GAME_STATES['MENU']
        self.new_scene_to_process: int = -1
        self.pause_surf = pg.Surface((WIDTH , HEIGHT))

        self.pause_options: dict = {
            'resume': 0, 
            'menu': 1, 
            'settings': 2,
        }
        self.menu_options: dict = {
            'play': 0,
        }

        self.clicked: bool = False

        self.fonts = {
            'arcade': 'font/arcade.ttf',
            'drip': 'font/drip.ttf',
            'retro': 'font/retro.ttf',
            'test': 'font/test.ttf',
            'bold': 'font/bold.ttf',
        }
        self.can_shoot = False

    def _init(self):
        fade_out = FadeOut('default')
        self.effects.add(fade_out)
        pg.mixer.music.load('sounds/music.mp3')
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.6)

    def run(self):
        self._init_state(GAME_STATES['MENU'])
        self._init()

        while True:
            self.update()
            self.state_machine.render()
            self.check_inputs()
            
    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.delta_time = self.clock.tick(FPS)
        self.delta_time /= 1000
        
    def render(self):
        self.display.fill(BLACK)

        #TILES
        self.tile_map.render_tiles(self.display)

        #PLAYER
        self.player.update()
        self.player.render(self.display)

        #enemies
        for enemy in self.enemies.copy():
            enemy.render(self.display)
            done = enemy.update()
            if done:
                self.enemies.remove(enemy)

        for door in self.doors.copy():
            door.render(self.display)
            door.update()

        for eff in self.effects.copy():
            eff.render(self.display)
            done = eff.update(self.delta_time)
            if done:
                self.effects.remove(eff)

        display_offset = [0,0]
        if self.screenshake > 0:
            self.screenshake -= 1
            display_offset[0] = random.randrange(-6, 6)
            display_offset[1] = random.randrange(-6, 6)

        self.screen.blit(self.display, (0 + display_offset[0], 0 + display_offset[1]))
        pg.display.flip()
        pg.display.update()

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_d:
                    if self.player.state_machine.state.state_type != 'climb':
                        self.player.movement[0] = True
                        self.player.flip = False
                if e.key == pg.K_a:
                    if self.player.state_machine.state.state_type != 'climb':
                        self.player.movement[1] = True
                        self.player.flip = True
                if e.key == pg.K_w:
                    self.player.movement[2] = True
                if e.key == pg.K_s:
                    self.player.movement[3] = True

                if e.key == pg.K_p:
                    self.state_machine.pause()

                if e.key == pg.K_SPACE:
                    self.player.jump()
                if e.key == pg.K_m:
                    self.player.can_dash = True
                if e.key == pg.K_n:
                    #self.player.attack_1()
                    self.can_shoot = True
                
                if e.key == pg.K_t:
                    #self.test()
                    self.player.gravity = -900
                    eff = Explosion(app=self, pos = vec2(self.player.pos.x + 16, self.player.pos.y + 16))
                    self.effects.add(eff)

                if e.key == pg.K_0:
                    self.Capture(self.display, 'cap.png', (0, 96), (32, 32))

            if e.type == pg.KEYUP:
                if e.key == pg.K_d:
                    self.player.movement[0] = False
                if e.key == pg.K_a:
                    self.player.movement[1] = False
                if e.key == pg.K_w:
                    self.player.movement[2] = False
                if e.key == pg.K_s:
                    self.player.movement[3] = False
                if e.key == pg.K_n:
                    self.can_shoot = False
        
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.clicked = True
            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.clicked = False

    def transition_to_new_scene(self, next_scene: int):
        self.state_machine.change_state('transition')
        self.new_scene_to_process = next_scene
        transition = FadeOut('default')
        self.effects.add(transition)

    def reset(self):
        self.state_machine.change_state('transition')
        self.new_scene_to_process = 0
        transition = ResetTransition('reset', self.player)
        self.effects.add(transition)
        self.screenshake = 0

    def load_scene(self, scene_num):
        self.tile_map.reset_scene()
        self.enemies.clear()
        self.doors.clear()
        self.particles.clear()
        self.background_effects.clear()
        obj_items = self.tile_map.load_map(SCENE_PATH + str(scene_num)+'.json')
        for e in obj_items['enemies']: self.enemies.add(e)
        for d in obj_items['doors']: self.doors.add(d)
        for i in range(16):
            star_anim = self.assets['effects']['stars'][0].copy()
            star_anim.dur = random.uniform(.1, .2)
            star_eff = Effect(pos=vec2(random.randrange(50, WIDTH - 50), random.randrange(50, HEIGHT - 50)), vel=vec2(0), size=[0, 0], anim=star_anim)
            self.background_effects.add(star_eff)
        for i in range(10):
            f_particle = FloatParticle(app=self, vel=vec2(random.uniform(-1, 1), random.uniform(-1, 1)), pos=vec2(random.randrange(50, WIDTH - 50), random.randrange(50, HEIGHT - 50)), speed=.5, image=self.assets['objects']['rocks'][random.randrange(0, 3)])
            self.particles.add(f_particle)
        #floatparticle

    def change_state(self, state):
        if state in GAME_STATES and state != self.state:
            self.state = GAME_STATES[state]
            self._init_state(state)

    def play_sound(self, key, volume: float):
        sound1 = pg.mixer.Sound(self.sound_assets[key])
        channel = pg.mixer.find_channel(True)
        channel.set_volume(volume)
        channel.play(sound1)

    def menu_render(self):
        self.display.fill(BLACK)

        self.tile_map.render_tiles(self.display)

        mpos = pg.mouse.get_pos()
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)

        render_text_2( surf=self.display, text=self.game_name, pos=vec2( HALF_WIDTH - 280, HALF_HEIGHT - 122), offset=vec2(0,0), size=90, italic=False, rgb=PURPLE,  font=self.fonts['test'])
        render_text_2( surf=self.display, text=self.game_name, pos=vec2( HALF_WIDTH - 280, HALF_HEIGHT - 130), offset=vec2(0,0), size=90, italic=False, rgb=WHITE,  font=self.fonts['test'])

        for key, val in self.menu_options.items():
            click = self.button_box(
                surf=self.display,
                pos=vec2((WIDTH // 2) - (SELECT_BOX_SIZE[0] // 2) + 20, (HEIGHT // 2) - (SELECT_BOX_SIZE[1] // 2) + 20 + (val * 60)),
                size=[130,60],
                text=key,
                mpos_rect=mpos_rect,
                text_size=50,
                font=self.fonts['arcade']
            )
            if click:
                if key == 'play':
                    self.effects.clear()
                    self.change_state('PLAY')
                    self.load_scene(0)
        for eff in self.effects:
            eff.update(self.delta_time)
            eff.render(self.display)

        self.screen.blit(self.display, (0, 0))
        pg.display.flip()
        pg.display.update()

    def pause_render(self):
        self.display.fill(BG)

        mpos = pg.mouse.get_pos()

        self.tile_map.render_tiles(self.display)
        self.player.render(self.display)

        for enemy in self.enemies.copy(): enemy.render(self.display)
        for door in self.doors.copy(): door.render(self.display)
        for eff in self.effects.copy(): eff.render(self.display)

        self.pause_window(self.display, mpos)

        self.screen.blit( self.display, (0,0))
        pg.display.flip()
        pg.display.update()

    def pause_window(self, surf, mpos):
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)
        self.pause_surf.fill(BLACK)
        self.pause_surf.set_alpha(120)
        surf.blit(self.pause_surf, (0,0))
        pg.draw.rect(surf, ORANGE, ((WIDTH // 2) - (PAUSE_BOX_WIDTH // 2), (HEIGHT // 2) - (PAUSE_BOX_WIDTH // 2) + 20, PAUSE_BOX_WIDTH, PAUSE_BOX_HEIGHT), 6, 60, 0, 0, 0)
        for key, val in self.pause_options.items():
            click = self.button_box(
                surf=self.display, 
                pos=vec2((WIDTH // 2) - (SELECT_BOX_SIZE[0] // 2) - 100, (HEIGHT // 2) - (SELECT_BOX_SIZE[1] // 2) - 100 + (val * 100)),
                size=SELECT_BOX_SIZE,
                text=key,
                mpos_rect=mpos_rect,
                text_size=30,
                font=self.fonts['arcade']
                )
            if click:
                if val == self.pause_options['resume']:
                    self.change_state('PLAY')
                elif val == self.pause_options['menu']:
                    print('menu')
                elif val == self.pause_options['settings']:
                    print('settings')
                return 

    def button_box(self, surf, pos: vec2, size: list, text: str, mpos_rect, text_size: int, font: str):
        #pg.draw.rect(surf, ORANGE, (pos.x, pos.y, size[0], size[1]))
        tile_category_rect = pg.Rect(pos.x, pos.y, size[0], size[1])
        text_color = WHITE
        text_color_2 = LIGHT_RED
        if mpos_rect.colliderect(tile_category_rect): 
            text_color = LIGHT_RED
            text_color_2 = WHITE
            #pg.draw.rect(surf, WHITE, (pos.x - 1, pos.y - 1, size[0] + 2, size[1] + 2), 0, 10, 10, 0, 0)
        render_text_2(surf=surf, text=text, pos=vec2( pos.x + 12 ,pos.y + 8 ), offset=vec2(0,0), size=text_size,italic=False, rgb=text_color_2, font=font)
        render_text_2(surf=surf, text=text, pos=vec2( pos.x + 12 ,pos.y + 4 ), offset=vec2(0,0), size=text_size,italic=False, rgb=text_color, font=font)
        if mpos_rect.colliderect(tile_category_rect) and self.clicked: return True
        return False
    
    def test(self):
        self.state_machine.state.flash()

    def _init_state(self, state):
        if state == GAME_STATES['MENU']:
            self.effects.clear()
            for i in range(20):
                star_anim = self.assets['effects']['stars'][0].copy()
                star_anim.dur = random.uniform(.1, .2)
                star_eff = Effect(pos=vec2(random.randrange(10, WIDTH-10), random.randrange(0, HEIGHT - 200)), vel=vec2(0), size=[0,0], anim=star_anim)
                self.background_effects.add(star_eff)
            self.load_scene(-1)

    def Capture(self, display, name, pos, size): 
        image = pg.Surface(size) 
        image.blit(display, (0, 0), (pos, size))
        pg.image.save(image, 'images/saved/' + name)

if __name__ == '__main__':
    app: App = App()
    app.run()


'''
        self.cam_offset.x += (self.player.pos.x - WIDTH / 2 - self.cam_offset.x) / 20
        self.cam_offset.y += (self.player.pos.y - HEIGHT / 2 - self.cam_offset.y) / 20
        cam_offset = [self.cam_offset.x, self.cam_offset.y]
'''