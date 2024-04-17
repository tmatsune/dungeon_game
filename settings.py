import pygame as pg
from heapq import heapify, heappush, heappop
import math, sys, random, json, os

#DEFAULT
vec2 = pg.math.Vector2
WIDTH = 640
HEIGHT = 640
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60
CELL_SIZE = 32
HALF_CELL = CELL_SIZE // 2
IMG_PATH = 'images/'
TILE_PATH = 'images/tiles/'
SCENE_PATH = 'scenes/'
SOUND_PATH = 'sounds/'

#PAUSE
PAUSE_BOX_WIDTH = 500
PAUSE_BOX_HEIGHT = 440
SELECT_BOX_SIZE = [180,36]

#COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (40, 180, 250)
BG = (20, 20, 30)
GRAY = (30, 30, 50)
GREEN = (0, 255, 0)
RED = (255, 30, 30)
ORANGE = (255, 130, 30)
LIGHT_RED = (240, 0, 80)
RED_2 = (250, 10, 60)
PURPLE = (140, 0, 210)
LIGHT_GREEN = (0, 240, 0)
ORANGE = (250, 90, 0)

#WINDOW_COLORS
LIGHT_GRAY = (120, 120, 120)
MID_GRAY = (70, 70, 70)
DARK_GRAY = (30, 30, 30)

#CHARACTER DEFAULT
PLAYER_SPEED = 680
PLAYER_ATTACK_SPEED = 300
PLAYER_GRAVITY = 1200


# ENEMY TYPES 
ENEMY_HASH = {
    0 : 'enemy_test',
}

#GAME_STATES 
GAME_STATES = {
    'PLAY' : 1,
    'PAUSE': 2,
    'MENU': 3,
    'START': 4,
    'TRANSITION': 5,
}

ONEFORTH = math.pi / 2
PI = math.pi
THREEFORTH = 3 * (math.pi / 2)
PITIMES2 = math.pi * 2