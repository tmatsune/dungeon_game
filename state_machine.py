from settings import * 
from animation import * 
from particles import DustParticle

class StateMachine():
    def __init__(self, app, entity) -> None:
        self.app = app
        self.entity = entity
        self.state: State = Idle(app=app, user=entity, state_machine=self, e_type='player')
        self.states: dict = {
            'idle': Idle(app=app, user=entity, state_machine=self, e_type='player'),
            'run': Run(app=app, user=entity, state_machine=self, e_type='player'),
            'attack': Attack(app=app, user=entity, state_machine=self, e_type='player'),
            'fall': Fall(app=app, user=entity, state_machine=self, e_type='player'),
            'jump': Jump(app=app, user=entity, state_machine=self, e_type='player'),
            'dash': Dash(app=app, user=entity, state_machine=self, e_type='player'),
            'climb': Climb(app=app, user=entity, state_machine=self, e_type='player'),
            'dead': Dead(app=app, user=entity, state_machine=self, e_type='player'),
        }

    def update(self):
        return self.state.update(self.app.delta_time)
    
    def render(self):
        return self.state.render()
    
    def change_state(self, state: str):
        if state in self.states and self.state.state_type != state:
            self.state = self.states[state]
            sprite_image = self.state.anim.image()
            self.entity.image_scale.x = sprite_image.get_width()
            self.entity.image_scale.y = sprite_image.get_height()
            
class State():
    def __init__(self, app, user, state_machine, e_type) -> None:
        self.app = app
        self.user = user
        self.state_machine = state_machine
        self.e_type: str = e_type
        self.state_type: str
        self.anim: Animation

    def update(self):
        pass
    def render(self):
        pass

class Idle(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['idle']
        self.state_type = 'idle'

    def update(self, delta_time):
        self.anim.update(delta_time)
        if not self.user.is_on_floor():
            self.state_machine.change_state("fall")
        #if user.jump_used:
        #    state_machine.change_state("jump")
        if self.user.is_on_floor() and (self.user.movement[0] != 0 or self.user.movement[1] != 0):
            self.state_machine.change_state("run")
        return False

    def render(self):
        return self.anim.image()

class Run(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['run']
        self.state_type = 'run'
        self.add_dust_timer: float = 0
        
    def update(self, delta):
        self.anim.update(delta)

        if self.user.movement[0] == 0 and self.user.movement[1] == 0:
            self.state_machine.change_state('idle')
        if not self.user.is_on_floor():
            self.state_machine.change_state("fall")
        
        self.add_dust_timer -= delta
        if self.add_dust_timer <= 0:
            self.add_dust_timer = .06
            pos = vec2(self.user.pos.x, self.user.pos.y + 28)
            x_v = 0
            if self.user.flip:
                pos.x += 36
                x_v = 3
            else:
                pos.x -= 4
                x_v = -3
            dust = DustParticle(app=self.app, pos=pos, vel= vec2(x_v, -4))
            self.app.particles.add(dust)
        return False

    def render(self):
        return self.anim.image()
    

class Jump(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['jump']
        self.state_type = 'jump'

    def update(self, delta_time):
        self.anim.update(delta_time)

        if self.user.is_on_wall() and (self.user.movement[0] or self.user.movement[1]):
            self.state_machine.change_state('climb')
        if self.user.is_on_floor():
            self.state_machine.change_state('idle')
        return False

    def render(self):
        return self.anim.image()

class Dash(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['dash']
        self.state_type = 'dash'

    def update(self, delta_time):
        self.anim.update(delta_time)
        if self.user.acceleration < 2:
            self.user.acceleration = 2
            if self.user.is_on_floor():
                self.state_machine.change_state("idle")
            elif self.user.jump_used:
                self.user.gravity = 600
                self.state_machine.change_state("fall")
            else:
                self.user.gravity = 600
                self.state_machine.change_state("fall")
        return False

    def render(self):
        return self.anim.image()

class Fall(State): 
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['fall']
        self.state_type = 'fall'
    
    def update(self, delta_time):
        self.anim.update(delta_time)

        if self.user.is_on_floor():
            self.state_machine.change_state('idle')

        if self.user.is_on_wall() and (self.user.movement[0] or self.user.movement[1]):
            self.state_machine.change_state('climb')
        return False

    def render(self):
        return self.anim.image()


class Hurt(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['hurt']
        self.state_type = 'hurt'
        self.hurt_timer = 1

    def update(self, delta_time):
        self.anim.update(delta_time)
        self.hurt_timer -= self.app.delta_time
        if self.hurt_timer <= 0:
            self.state_machine.change_state('idle')
        return False

    def render(self):
        return self.anim.image()

class Dead(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['dead']
        self.state_type = 'dead'

    def update(self, delta_time):
        done = self.anim.update(delta_time) if not self.anim.done else True
        if done:
            self.app.reset()
            return True
        return done

    def render(self):
        return self.anim.image()

class Climb(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['climb']
        self.state_type = 'climb'
    
    def update(self, delta_time):
        self.anim.update(delta_time)

        if not self.user.movement[0] and not self.user.movement[1]:
            self.state_machine.change_state('fall')
        
        if self.user.jump_used:  # self.user.gravity < -1000
            self.state_machine.change_state('jump')
        
        if not self.user.is_on_wall() and (self.user.x_left == 0 and self.user.x_right == 0):
            self.state_machine.change_state('fall')
        return False
    
    def render(self):
        return self.anim.image()
    
class Attack(State):
    def __init__(self, app, user, state_machine, e_type) -> None:
        super().__init__(app, user, state_machine, e_type)
        self.anim = app.assets[self.e_type]['attack']
        self.state_type = 'attack'

    def update(self, delta_time):
        self.anim.update(delta_time)
        if self.user.hover_timer <= 0:
            self.state_machine.change_state('idle')
        return False

    def render(self):
        return self.anim.image()
    
class EnemyStateMachine():
    def __init__(self, app, enemy) -> None:
        self.app = app
        self.enemy = enemy
        self.state: EnemyState = EnemyIdle(app=app, user=enemy, state_machine=self, e_type='enemy', enemy_type=enemy.enemy_id)
        self.states: dict = {
            'idle': EnemyIdle(app=app, user=enemy, state_machine=self, e_type='enemy', enemy_type=enemy.enemy_id),
            'attack': EnemyAttack(app=app, user=enemy, state_machine=self, e_type='enemy', enemy_type=enemy.enemy_id),
            'chase': EnemyChase(app=app, user=enemy, state_machine=self, e_type='enemy', enemy_type=enemy.enemy_id),
        }

    def update(self):
        self.state.update(self.app.delta_time)

    def render(self):
        return self.state.render()

    def change_state(self, state: str):
        if state in self.states and self.state.state_type != state:
            self.state = self.states[state]

class EnemyState():
    def __init__(self, app, user, state_machine, e_type, enemy_type) -> None:
        self.app = app
        self.user = user
        self.state_machine = state_machine
        self.e_type: str = e_type
        self.enemy_type: int = enemy_type
        self.state_type: str
        self.anim: Animation

    def update(self): pass
    def render(self): pass

class EnemyIdle(EnemyState):
    def __init__(self, app, user, state_machine, e_type, enemy_type) -> None:
        super().__init__(app, user, state_machine, e_type, enemy_type)
        self.anim = app.assets[self.e_type][self.enemy_type]['idle']
        self.state_type = 'idle'
    
    def update(self, delta_time):
        self.anim.update(delta_time)

    def render(self):
        return self.anim.image()

class EnemyAttack(EnemyState):
    def __init__(self, app, user, state_machine, e_type, enemy_type) -> None:
        super().__init__(app, user, state_machine, e_type, enemy_type)
        self.anim = app.assets[self.e_type][self.enemy_type]['attack']
        self.state_type = 'attack'

    def update(self, delta_time):
        self.anim.update(delta_time)

    def render(self):
        return self.anim.image()

class EnemyChase(EnemyState):
    def __init__(self, app, user, state_machine, e_type, enemy_type) -> None:
        super().__init__(app, user, state_machine, e_type, enemy_type)
        self.anim = app.assets[self.e_type][self.enemy_type]['chase']
        self.state_type = 'chase'

    def update(self, delta_time):
        self.anim.update(delta_time)

    def render(self):
        return self.anim.image()
