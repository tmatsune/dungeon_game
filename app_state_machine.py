from settings import * 
from utils import * 
from transition import * 
from effects import Effect, Background

class AppStateMachine():
    def __init__(self, app) -> None:
        self.app = app
        self.state: AppState = MenuState(app=app, state_machine=self)
        self.states: dict = {
            'play': PlayState(app=app, state_machine=self),
            'pause': PauseState(app=app, state_machine=self),
            'menu': MenuState(app=app, state_machine=self),
            'transition': TransitionState(app=app, state_machine=self),
        }
        self.state_names: set = {'play', 'pause', 'menu', 'transition'}

    def update(self):
        self.state.update()

    def render(self):
        self.state.render()

    def change_state(self, state: str):
        if state in self.states and self.state.state_type != state:
            self.app.effects.clear()
            self.state = self.states[state]
    
    def pause(self):
        if self.state.state_type == 'pause':
            self.state = self.states['play']
        else:
            self.state = self.states['pause']

    def _init_state(self, state: str):
        if state == 'menu':
            self.app.effects.clear()
            self.app.load_scene(-1)
            for i in range(20):
                star_anim = self.assets['effects']['stars'][0].copy()
                star_anim.dur = random.uniform(.1, .2)
                star_eff = Effect(pos=vec2(random.randrange(10, WIDTH-10), random.randrange(0, HEIGHT - 200)), vel=vec2(0), size=[0, 0], anim=star_anim)
                self.app.background_effects.add(star_eff)
        elif state == 'play':
            pass
        elif state == 'pause':
            pass
        elif state == 'transition':
            pass

class AppState():
    def __init__(self, app, state_machine) -> None:
        self.app = app
        self.state_machine: AppStateMachine = state_machine
        self.state_type = 'app'
    def update(self): pass
    def render(self): pass

class PlayState(AppState):
    def __init__(self, app, state_machine) -> None:
        super().__init__(app, state_machine)
        self.state_type = 'play'
        self.background = Background(app)
        self.w = WIDTH
        self.h = HEIGHT
        self.target_x = self.app.player.pos.x
        self.target_y = self.app.player.pos.y
        self.screen_offset = [0, 0]

    def render(self):
        self.app.display.fill(BLACK)

        #BACKGROUND
        self.background.render(self.app.display)
        self.background.update()

        for be in self.app.background_effects.copy():
            be.render(self.app.display)
            be.update(self.app.delta_time)

        # TILES
        self.app.tile_map.render_tiles(self.app.display)

        # PLAYER
        self.app.player.update()
        self.app.player.render(self.app.display)

        if self.app.player.weapon:
            self.app.player.weapon.can_shoot = self.app.can_shoot
        # enemies
        for enemy in self.app.enemies.copy():
            enemy.render(self.app.display)
            done = enemy.update()
            if done:
                self.app.enemies.remove(enemy)

        for door in self.app.doors.copy():
            door.render(self.app.display)
            door.update()

        for eff in self.app.effects.copy():
            eff.render(self.app.display)
            done = eff.update(self.app.delta_time)
            if done:
                self.app.effects.remove(eff)
        
        for bullet in self.app.bullets.copy():
            bullet.render(self.app.display)
            done = bullet.update()
            if done:
                self.app.bullets.remove(bullet)
            for e in self.app.enemies.copy():
                bullet.check_collision(e)
        
        for p in self.app.particles.copy():
            p.render(self.app.display)
            done = p.update()
            if done:
                self.app.particles.remove(p)

        self.app.ui.render(self.app.display)
        self.app.ui.update()

        display_offset = [0, 0]
        if self.app.screenshake > 0:
            self.app.screenshake -= 1
            display_offset[0] = random.randrange(-7,7)
            display_offset[1] = random.randrange(-7,7)

        self.screen_offset[0] = (WIDTH - self.w) / 2
        self.screen_offset[1] = (HEIGHT - self.h) / 2
        #self.w-=1
        #self.h-=1
        self.app.screen.blit(pg.transform.scale(self.app.display, (self.w, self.h)), (0 + display_offset[0] + self.screen_offset[0], 0 + display_offset[1] + self.screen_offset[1]))
        pg.display.flip()
        pg.display.update()

    def flash(self):
        self.background.flash()

class PauseState(AppState):
    def __init__(self, app, state_machine) -> None:
        super().__init__(app, state_machine)
        self.state_type = 'pause'
        self.background = Background(app)
        
    def render(self):
        self.app.display.fill(BLACK)
        self.background.render(self.app.display)
        for be in self.app.background_effects.copy():
            be.render(self.app.display)
        self.app.tile_map.render_tiles(self.app.display)
        self.app.player.render(self.app.display)

        if self.app.player.weapon:
            self.app.player.weapon.can_shoot = self.app.can_shoot
        for enemy in self.app.enemies.copy():
            enemy.render(self.app.display)
        for door in self.app.doors.copy():
            door.render(self.app.display)
        for eff in self.app.effects.copy():
            eff.render(self.app.display)
        for bullet in self.app.bullets.copy():
            bullet.render(self.app.display)
        for p in self.app.particles.copy():
            p.render(self.app.display)
        self.app.ui.render(self.app.display)
        self.app.ui.update()

        self.app.screen.blit(self.app.display, (0 , 0))
        pg.display.flip()
        pg.display.update()

class MenuState(AppState):
    def __init__(self, app, state_machine) -> None:
        super().__init__(app, state_machine)
        self.state_type = 'menu'
        self.menu_options: dict = {
            'play': 0,
        }
        self.background = Background(app)

    def flash(self):
        self.background.flash()

    def render(self): 

        mpos = pg.mouse.get_pos()
        mpos_rect = pg.Rect(mpos[0], mpos[1], 6, 6)

        self.app.display.fill(BLACK)

        self.background.render(self.app.display)
        self.background.update()

        for be in self.app.background_effects.copy():
            be.render(self.app.display)
            be.update(self.app.delta_time)

        self.app.tile_map.render_tiles(self.app.display)

        render_text_2( surf=self.app.display, text=self.app.game_name, pos=vec2( HALF_WIDTH - 280, HALF_HEIGHT - 122), offset=vec2(0,0), size=90, italic=False, rgb=LIGHT_RED,  font=self.app.fonts['test'])
        render_text_2( surf=self.app.display, text=self.app.game_name, pos=vec2( HALF_WIDTH - 280, HALF_HEIGHT - 130), offset=vec2(0,0), size=90, italic=False, rgb=WHITE,  font=self.app.fonts['test'])

        for key, val in self.menu_options.items():
            click = self.app.button_box(
                surf=self.app.display,
                pos=vec2((WIDTH // 2) - (SELECT_BOX_SIZE[0] // 2) + 20, (HEIGHT // 2) - (SELECT_BOX_SIZE[1] // 2) + 20 + (val * 60)),
                size=[130,60],
                text=key,
                mpos_rect=mpos_rect,
                text_size=50,
                font=self.app.fonts['arcade']
            )
            if click:
                if key == 'play':
                    self.app.effects.clear()
                    self.app.transition_to_new_scene(0)

        for eff in self.app.effects:
            eff.update(self.app.delta_time)
            eff.render(self.app.display)

        self.app.screen.blit(self.app.display, (0, 0))
        
        pg.display.flip()
        pg.display.update()

    def intro_to_game(self):
        pass


class TransitionState(AppState):
    def __init__(self, app, state_machine) -> None:
        super().__init__(app, state_machine)
        self.state_type = 'transition'

    def render(self):
        self.app.display.fill(BLACK)
        self.app.tile_map.render_tiles(self.app.display)
        self.app.player.render(self.app.display)
        for enemy in self.app.enemies.copy():
            enemy.render(self.app.display)
        for door in self.app.doors.copy():
            door.render(self.app.display)
        for eff in self.app.effects.copy():
            eff.render(self.app.display)
            if isinstance(eff, Transition):
                done = eff.update(self.app.delta_time)
                self.app.load_scene(self.app.new_scene_to_process)
                if done:
                    self.state_machine.change_state('play')
        self.app.screen.blit(self.app.display, (0, 0))
        pg.display.flip()
        pg.display.update()
