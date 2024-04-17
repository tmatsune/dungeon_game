from settings import * 
from particles import Shell

class Weapon():
    def __init__(self, app, user, firerate, magazine, clip_size, damage, recharge) -> None:
        self.app = app
        self.user = user
        self.firerate = firerate
        self.magazine = magazine
        self.clip_size = clip_size
        self.damage = damage
        self.recharge = recharge
        self.can_shoot = False
        self.shoot_timer = 0
        self.recharge_timer = recharge
        self.fired = True

    def update(self):
        self.shoot_timer -= self.app.delta_time
        if self.can_shoot and self.shoot_timer <= 0 and self.magazine > 0:
            self.shoot_timer = self.firerate    
            self.user.hover_timer = 0.1
            self.user.attack_1()
            self.shoot()
            self.magazine -= 1
            self.app.play_sound('gun_shot', .6)
            shell = Shell(app=self.app, pos=self.user.pos.copy(), vel=vec2(random.randrange(-4, 4), random.randrange(-5, -4)), image=self.app.assets['ui']['shell'])
            self.app.particles.add(shell)

        self.recharge_bullets()
    
    def recharge_bullets(self):
        self.recharge_timer -= self.app.delta_time
        if self.recharge_timer <= 0:
            if self.magazine < self.clip_size and not self.can_shoot: self.magazine += 1
            self.recharge_timer = self.recharge

    def shoot(self):
        self.fired = True
