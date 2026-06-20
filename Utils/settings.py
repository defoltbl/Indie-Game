from pygame.math import Vector2
import pygame
import os
import pickle

if os.path.exists('settings_data.txt'):
     with open('settings_data.txt', 'rb') as f:
            settings_data = pickle.load(f)
            SCREEN_WIDTH = settings_data['screen_width']
            SCREEN_HEIGHT = settings_data['screen_height']
            VOLUME = settings_data['volume']
else:
      screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
      SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
      VOLUME = 0.2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DEFAULT_FPS = 144
TILE_SIZE = 64

DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'
DIRECTION_LEFT = 'left'
DIRECTION_RIGHT = 'right'
ITEM_BOX_SIZE = 80
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
UI_BORDER_COLOR_ACTIVE = 'gold'


OVERLAY_POSITIONS = {

    'tool' : (40, SCREEN_HEIGHT - 15),
    'seed' : (90,SCREEN_HEIGHT - 10),
    'animal' : (1200, SCREEN_HEIGHT - 5)

    }

PLAYER_TOOL_OFFSET = {

    'left' : Vector2(-50, 40),
    'right' : Vector2(0, 10),
    'up' : Vector2(0, -10),
    'down' : Vector2(0, 50)

}

LAYERS = {

    'water' : 0,
    'ground' : 1,
    "soil" : 2,
    'soil water' : 3,
    'rain floor' : 4,
    'house bottom' : 5,
    'ground plant': 6,
    'main': 7,
    'player': 8,
    'house top': 9,
    'fruit': 10,
    'rain drops': 11,

}

APPLE_POS = {

    'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
    'Large': [(30,24), (60,65), (50,50), (16,40), (45,50), (42,70)]

}

GROW_SPEED = {

    'corn' : 1,
    'tomato' : 0.7
    
}

SALE_PRICES = {

    'wood' : 4,
    'apple': 2,
    'corn' : 3,
    'tomato' : 5, 
    'egg' : 5 
    
}

PURCHASEE_PRICES = {

    'corn' : 2,
    'tomato' : 3,
    'chicken': 20,
    'cow': 30
    
}

COAST = {
      'chickenhouse' : 15,
      'cowhouse': 25,
}

weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15,'graphic':'../graphics/weapons/sword/full.png'},
	'lance': {'cooldown': 400, 'damage': 30,'graphic':'../graphics/weapons/lance/full.png'},
	'axe': {'cooldown': 300, 'damage': 20, 'graphic':'../graphics/weapons/axe/full.png'},
	'rapier':{'cooldown': 50, 'damage': 8, 'graphic':'../graphics/weapons/rapier/full.png'},
	'sai':{'cooldown': 80, 'damage': 10, 'graphic':'../graphics/weapons/sai/full.png'}}

monster_data = {
	'squid': {'health': 100, 'damage':20,'attack_type': 'slash', 'attack_sound':'../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
	'spirit': {'health': 100,'damage':8,'attack_type': 'thunder', 'attack_sound':'../audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 350},
	'bamboo': {'health': 70,'damage':6,'attack_type': 'leaf_attack', 'attack_sound':'../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 100, 'notice_radius': 300}}

npc_data = {
	'wizzard': {'health': 99999, 'damage':99999, 'task_type': 1},
}

