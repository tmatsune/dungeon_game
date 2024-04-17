from settings import * 

def load_image(path: str, scale: float) -> pg.image:
    image: pg.image = pg.image.load(path)
    image = pg.transform.scale( image, (image.get_width() * scale, image.get_height() * scale))
    return image

def load_images_horiz(path: str, scale: float, frames: int) -> list:
    images = []
    sprite_sheet: pg.image = load_image(path, 1)
    sprite_sheet_width = sprite_sheet.get_width() 
    sprite_width = sprite_sheet_width // frames
    sprite_height = sprite_sheet.get_height()
    for i in range(frames):
        x = i * sprite_width
        sprite = sprite_sheet.subsurface((x, 0, sprite_width, sprite_height))
        image = pg.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
        images.append(image)
    return images   

def load_images_from_folder(path: str, scale: float, frames: int) -> list:
    images: list = []
    for i in range(frames):
        img_frame = load_image(path + '/' + str(i) + '.png', scale)
        images.append(img_frame)
    return images

def get_sound(path): return pg.mixer.Sound(path)

def render_text(surf, text, pos, offset, size, italic, rgb, font='arial', bold=True):
    font = pg.font.SysFont(font, size, bold, italic)
    text_surface = font.render(text, False, rgb)
    surf.blit(text_surface, (pos.x + offset.x, pos.y + offset.y))

def render_text_2(surf, text, pos, offset, size, italic, rgb, font='arial'):
    font = pg.font.Font(font, size)
    text_surface = font.render(text, False, rgb)
    surf.blit(text_surface, (pos.x + offset.x, pos.y + offset.y))

def mask_collision(mask1, pos1, mask2, pos2): return mask2.overlap(mask1, (pos1.x - pos2.x, pos1.y - pos2.y))
def distance(pos1, pos2): return math.sqrt( pow(pos1.x - pos2.x, 2) + pow(pos1.y - pos2.y, 2) )

def get_tile_images():
    tile_images = {
        'main': {
            'tile': {
                0: load_image(TILE_PATH + 'main/tile/0.png', 1),
                1: load_image(TILE_PATH + 'main/tile/1.png', 1),
                2: load_image(TILE_PATH + 'main/tile/2.png', 1),
                3: load_image(TILE_PATH + 'main/tile/3.png', 1),
                4: load_image(TILE_PATH + 'main/tile/4.png', 1),
                5: load_image(TILE_PATH + 'main/tile/5.png', 1),
                6: load_image(TILE_PATH + 'main/tile/6.png', 1),
                7: load_image(TILE_PATH + 'main/tile/7.png', 1),
                8: load_image(TILE_PATH + 'main/tile/8.png', 1),
            }
        },
        'objects': {
            'door': {
                0: load_image(TILE_PATH + 'objects/door/0.png', 1),
            },
            'enemies': {
                0: load_image(TILE_PATH + 'objects/enemies/0.png', 1),
                1: load_image(TILE_PATH + 'objects/enemies/1.png', 1.6),
            },
            'spikes': {
                0: load_image(TILE_PATH + 'objects/spikes/0.png', 1),
                1: load_image(TILE_PATH + 'objects/spikes/1.png', 1),
                2: load_image(TILE_PATH + 'objects/spikes/2.png', 1),
                3: load_image(TILE_PATH + 'objects/spikes/3.png', 1),
                4: load_image(TILE_PATH + 'objects/spikes/4.png', 1),
                5: load_image(TILE_PATH + 'objects/spikes/5.png', 1),
            }
        }
    }
    return tile_images

    

