#############################
# Game properties
#############################
WIDTH, HEIGHT = 800, 600
FPS = 30

#############################
# Menu properties
#############################
MENU_WINDOW_WIDTH = 800
MENU_WINDOW_HEIGHT = 600
FONT_SIZE = 20

#############################
# Colors
#############################
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)


#############################
# Paddle
#############################
PADDLE_WIDTH, PADDLE_HEIGHT = 11, 100
PADDLE_SPEED = 5

#############################
# Ball
#############################
BALL_SIZE = 20
BALL_SPEED_X = 5
BALL_SPEED_Y = 6

#############################
# Middleware 
#############################

#Logging
LOGS_DIR = "logs"
LOG_RATE = 10 # Log every 10 seconds

#Peer
POLL_RATE = 1000 

#Discovery
PRESENCE_BROADCAST_INTERVAL = 1
UDP_BROADCAST_PORT = 9999
KEY = b'abcd'

#Leader selection
ELECTION_TIMEOUT = 5  
HEARTBEAT_INTERVAL = 1 
ELECTION_TIMEOUT_CHECK = 3 