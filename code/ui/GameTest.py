import pygame
import serial
import random
import sys
import glob

# Constants
WIDTH = 400
HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 80
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
OBSTACLE_GAP = 200
OBSTACLE_SPEED = 5
OBSTACLE_MOVEMENT_SPEED = 2

# Initialize serial port
serial_port = '/dev/cu.usbmodem1103'
ser = serial.Serial(port=serial_port, baudrate=115200)
print(f"Using serial port: {serial_port}")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Background class
class Background(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__() 
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = 0,0

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self, tilt_angle):
        self.speedx = 0
        if tilt_angle < -10:
            self.speedx = -5
        if tilt_angle > 10:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = OBSTACLE_MOVEMENT_SPEED * random.choice([-1, 1])

    def update(self, tilt_angle):
        self.rect.y += OBSTACLE_SPEED
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
            self.speedx = OBSTACLE_MOVEMENT_SPEED * random.choice([-1, 1])
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx
            
class Game():
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Driving Game")
        self.clock = pygame.time.Clock()

        # Load images
        self.load_images()
        # Create sprites
        self.create_sprites()

        self.running = True

    def load_images(self):
        # Load and transform images
        self.player_img = pygame.image.load('ui/redcar.png').convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.obstacle_img = pygame.image.load('ui/cone.png').convert_alpha()
        self.obstacle_img = pygame.transform.scale(self.obstacle_img, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.road_img = pygame.image.load('ui/road.png').convert_alpha()
        self.road_img = pygame.transform.scale(self.road_img, (WIDTH, HEIGHT))

    def create_sprites(self):
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        # Create player and background
        self.player = Player(img=self.player_img)
        self.all_sprites.add(self.player)
        self.background = Background(img=self.road_img)
        # Create initial obstacles
        self.create_initial_obstacles()
        
    def create_initial_obstacles(self):
        for i in range(2):
            obstacle = Obstacle(random.randint(0, WIDTH - OBSTACLE_WIDTH), i * (HEIGHT // 2), self.obstacle_img)
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)
    
    def reset_game(self):
        # Clear obstacles
        for i, obstacle in enumerate(self.obstacles):
            obstacle.rect.x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
            obstacle.rect.y = i * (HEIGHT // 4)
            obstacle.speedx = OBSTACLE_MOVEMENT_SPEED * random.choice([-1, 1])
            
        # Reset player position
        self.player.rect.centerx = WIDTH // 2  
        self.player.rect.bottom = HEIGHT - 10
    
    def pause(self, over):
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                if event.type == pygame.KEYDOWN: # Restart game
                    if over:
                        self.reset_game()
                    paused = False
      
    def play(self):
        # Game loop

        self.screen.fill(WHITE)
        self.screen.blit(self.background.image, self.background.rect)
        font = pygame.font.SysFont(None, 36)
        text = font.render("Don't Crash!", 1, RED)
        subfont = pygame.font.SysFont(None, 25)
        subtext = subfont.render("Press any key to start.", 1, (10, 10, 10))
        textpos = text.get_rect()
        subtextpos = subtext.get_rect()
        textpos.centerx = self.screen.get_rect().centerx
        textpos.centery = self.screen.get_rect().centery
        subtextpos.centerx = self.screen.get_rect().centerx
        subtextpos.centery = textpos.centery + 30
        self.screen.blit(text, textpos)
        self.screen.blit(subtext, subtextpos)
        pygame.display.flip()
        self.pause(False)
        
        while self.running:
            # Keep loop running at the right speed
            self.clock.tick(FPS)
            # Update
            serial_data = ser.readline().decode()
            angle_str = serial_data[-13:-3].replace(" ", "").lstrip(':')
            # Convert the string to a float
            try:
                angle = float(angle_str)
            except ValueError:
                angle = 0
            print(angle)

            self.all_sprites.update(angle)

            # Process input (events)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.screen.fill(WHITE)
            self.screen.blit(self.background.image, self.background.rect)

            # Check for collision between player and obstacles
            hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
            if hits:
                self.screen.fill('red')
                text = font.render("GAME OVER!", 1, (10, 10, 10))
                subtext = subfont.render("Press any key to play again.", 1, (10, 10, 10))
                textpos.centerx = self.screen.get_rect().centerx
                subtextpos.centerx = self.screen.get_rect().centerx
                self.screen.blit(text, textpos)
                self.screen.blit(subtext, subtextpos)
                pygame.display.flip()
                tx_string = "GAME_OVER\n"
                bytes_written = ser.write(tx_string.encode())
                print(f"Bytes written: {bytes_written}")
                self.pause(True)
                continue
                
            # Add new obstacles
            while len(self.obstacles) < 3:
                obstacle = Obstacle(x=random.randint(0, WIDTH - OBSTACLE_WIDTH), y=-OBSTACLE_HEIGHT, img=self.obstacle_img)
                self.all_sprites.add(obstacle)
                self.obstacles.add(obstacle)

            # Draw / render
            self.all_sprites.draw(self.screen)
            # *after* drawing everything, flip the display
            pygame.display.flip()

if __name__=='__main__':
    game = Game()
    game.play()
    pygame.quit()
    sys.exit()
