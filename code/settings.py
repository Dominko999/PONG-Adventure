import pygame, random
from os.path import join

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BATTLE_AREA_LEFT, BATTLE_AREA_TOP, BATTLE_AREA_RIGHT, BATTLE_AREA_BOTTOM = WINDOW_WIDTH / 14, WINDOW_HEIGHT / 12, WINDOW_WIDTH / 14 * 13, WINDOW_HEIGHT / 12 * 10
SIZE = {'paddle' : (20,160), 'ball' : (20,20), 'player' : (64,64)}
POS = {
    'left_paddle' : (30,WINDOW_HEIGHT/2),
    'player_paddle' : (int(BATTLE_AREA_LEFT + (BATTLE_AREA_LEFT * 0.5)), (BATTLE_AREA_BOTTOM + BATTLE_AREA_TOP) / 2),
    'enemy_paddle' : (int(BATTLE_AREA_RIGHT - (BATTLE_AREA_LEFT * 0.5)), (BATTLE_AREA_BOTTOM + BATTLE_AREA_TOP) / 2),
    'right_paddle' : (WINDOW_WIDTH-30,WINDOW_HEIGHT/2),
    'ball' : (WINDOW_WIDTH/2,WINDOW_HEIGHT/2)
}
SPEED = {'paddle' : 700, 'ai_paddle' : 500, 'ball' : 700, 'player' : 300, 'fly' : 200, 'spider' : 150, 'beetle' : 40}
SPEED_LIMIT = {'ball' : pygame.Vector2(1600,600)}
ERROR_RATE = {'big' : 0}
COOLDOWN = {'paddle' : 1, 'ai_paddle_decision' : 0.5}
AI_ACTION_CHANCES = {'attack' : 3, 'slide' : 6, 'nothing' : 10} # 100% = 10
DURATIONS = {'paddle_attack' : 0.25, 'paddle_slide' : 0.2}
SPEED_BOOST = {'slide' : 1.5, 'attack' : 1.2}
COLORS = {
    'paddle_active' : [255,255,255],
    'paddle_cooldown' : [50,50,50],
    'paddle_slide' : [255, 251, 0],
    'ball' : [255,255,255],
    'bg' : [0,0,0],
    'bg_detail' : [200,200,200],
    'button' : [100,100,100],
    'button_hover' : [60,60,60],
    'button_pressed' : [30,30,30],
    'health' : [255,0,0],
    'exp' : [0,255,255],
    'progress_bar_background' : [80,80,80]
}

BATTLE_STATS = {
'Default' : {
    'speed' : 500,
    'paddle_size' : (20,150),
    'error_rate' : 0,
    'low_speed_multiplier' : 0.3,
    'medium_speed_multiplier' : 1.4,
    'high_speed_multiplier' : 2,
    'attack' : 3,
    'slide' : 6,
    'nothing' : 10  # 100% = 10
},
'Evil fly' : {
    'speed' : 600,
    'paddle_size' : (20,100),
    'error_rate' : 0,
    'low_speed_multiplier' : 0.4,
    'medium_speed_multiplier' : 1.6,
    'high_speed_multiplier' : 2.2,
    'attack' : 5,
    'slide' : 5,
    'nothing' : 10  # 100% = 10
    },
'Evil spiderlike creature' : {
    'speed' : 300,
    'paddle_size' : (20,160),
    'error_rate' : 0,
    'low_speed_multiplier' : 0.5,
    'medium_speed_multiplier' : 1,
    'high_speed_multiplier' : 1.3,
    'attack' : 0,
    'slide' : 7,
    'nothing' : 10  # 100% = 10
    },
'Evil very big beetle' : {
    'speed' : 200,
    'paddle_size' : (20,190),
    'error_rate' : 0.01,
    'low_speed_multiplier' : 0.5,
    'medium_speed_multiplier' : 0.9,
    'high_speed_multiplier' : 1.2,
    'attack' : 2,
    'slide' : 3,
    'nothing' : 10  # 100% = 10
    }
}

pygame.font.init()
FONTS = {
    'score' : pygame.font.SysFont('comicsans', 160),
    'menu_title' : pygame.font.SysFont('comicsans', 120),
    'menu_buttons' : pygame.font.SysFont('comicsans', 45),
    'instructions_player' : pygame.font.SysFont('comicsans', 80),
    'instructions_text' : pygame.font.SysFont('comicsans', 20),
    'dialogue' : pygame.font.SysFont('comicsans', 30)
}

