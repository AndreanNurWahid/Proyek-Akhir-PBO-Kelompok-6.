SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAP_WIDTH = 1200   
MAP_HEIGHT = 900
FPS = 60

RADAR_VIEW_DISTANCE = 250

PLAYER_SIZE = 64
NPC_SIZE = 64
MONSTER_SIZE = 64

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34) 
DARK_GREEN = (10, 150, 50)    
BLUE = (0, 120, 255)         
RED = (220, 20, 60)        
GOLD = (255, 215, 0)         
GREY = (50, 50, 60)       
LIGHT_GREY = (180, 180, 180)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128) 
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
LIGHT_BLUE = (150, 150, 255)

ELEMENT_CHART = {
    "Wind":   {"Water": 2.0, "Earth": 0.5, "Wind": 1.0, "Fire": 1.0, "Normal": 1.0},
    "Water":  {"Fire": 2.0, "Wind": 0.5, "Water": 1.0, "Earth": 1.0, "Normal": 1.0},
    "Fire":   {"Earth": 2.0, "Water": 0.5, "Fire": 1.0, "Wind": 1.0, "Normal": 1.0},
    "Earth":  {"Wind": 2.0, "Fire": 0.5, "Earth": 1.0, "Water": 1.0, "Normal": 1.0},
    "Normal": {"Wind": 1.0, "Water": 1.0, "Fire": 1.0, "Earth": 1.0, "Normal": 1.0}
}