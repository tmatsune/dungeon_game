from settings import * 

class Animation():
    def __init__(self, images, dur, loop=True, offset: vec2=vec2(0)) -> None:
        self.images = images
        self.timer = dur
        self.dur = dur
        self.loop = loop
        self.frame = 0
        self.max_frames = len(images)
        self.image_offset: vec2 = offset
        self.done = False
    
    def copy(self):
        return Animation(images=self.images, dur=self.dur, loop=self.loop, offset=self.image_offset)

    def update(self, delta_time):
        self.timer -= delta_time
        if self.timer <= 0:
            self.timer = self.dur
            self.frame += 1
            if self.frame >= self.max_frames:
                self.frame = 0
                if not self.loop: 
                    self.done = True
                    return True
        return False

    def offset(self):
        return self.image_offset.copy()
        
    def image(self):
        return self.images[self.frame]
    