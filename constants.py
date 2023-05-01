""" Global Parameters """
SCALE = 4

""" Screen Parameters """
SCREEN_WIDTH = 128*SCALE
SCREEN_HEIGHT = 128*SCALE
GAME_TICKS = 60

""" Game Parameters """
NUM_OBSTACLES = 0

""" Map Parameters """
MAP_WIDTH = 254*SCALE
MAP_HEIGHT = 254*SCALE
BORDER = 4*SCALE

""" Vehicle Parameters """
VEHICLE_LENGTH = 11*SCALE     #(0.1m)
VEHICLE_WIDTH  = 5.5*SCALE     #(0.1m)
MASS   = 650/SCALE   #(kg)
C_DRAG_ROAD = 50     #0.4257
C_DRAG_GRASS = 50
C_BRAKE = 1000000
POS_BUFFER_LENGTH = 60

""" Obstacle Parameters """
OBSTACLE_LENGTH = 20*SCALE
OBSTACLE_WIDTH = 10*SCALE

""" Sound Parameters """
SOUND_ON = False