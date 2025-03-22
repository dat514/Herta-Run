import pygame
from PIL import Image
import random
import sys
import os

pygame.init()

pygame.mixer.music.load("background_music.mp3")  
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

WIDTH = 700
HEIGHT = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run - Replay Button")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

high_score = 0

def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

def update_high_score(score):
    global high_score
    if score > high_score:
        high_score = score
        save_high_score(high_score)

FPS = 60
clock = pygame.time.Clock()

def load_gif_frames(gif_path, size):
    gif = Image.open(gif_path)
    frames = []
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.copy().convert("RGBA")
        frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
        frame_surface = pygame.transform.scale(frame_surface, size)
        frames.append(frame_surface)
    return frames

BACKGROUND_DAY_IMG = pygame.image.load("background_day.png")
BACKGROUND_DAY_IMG = pygame.transform.scale(BACKGROUND_DAY_IMG, (WIDTH, HEIGHT))
BACKGROUND_NIGHT_IMG = pygame.image.load("background_night.png")
BACKGROUND_NIGHT_IMG = pygame.transform.scale(BACKGROUND_NIGHT_IMG, (WIDTH, HEIGHT))

DINO_FRAMES = load_gif_frames("dino.gif", (40, 40))
CACTUS_IMG = pygame.image.load("cactus.png")
CACTUS_IMG = pygame.transform.scale(CACTUS_IMG, (30, 40))

CLOUD_IMG = pygame.image.load("cloud.png")
CLOUD_IMG = pygame.transform.scale(CLOUD_IMG, (100, 60)) 

SUN_IMG = pygame.image.load("sun.png")  
SUN_IMG = pygame.transform.scale(SUN_IMG, (100, 100))  

MOON_IMG = pygame.image.load("moon.png")  
MOON_IMG = pygame.transform.scale(MOON_IMG, (100, 100)) 

class Dino:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT - 40
        self.width = 40
        self.height = 40
        self.velocity = 0
        self.gravity = 0.8
        self.lift = -15
        self.frames = DINO_FRAMES
        self.frame_index = 0
        self.frame_delay = 5
        self.frame_counter = 0
        self.is_jumping = False

    def update(self):
        if self.is_jumping:
            self.velocity += self.gravity
            self.y += self.velocity
            if self.y >= HEIGHT - self.height:
                self.y = HEIGHT - self.height
                self.velocity = 0
                self.is_jumping = False
        
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.frame_counter = 0

    def jump(self):
        if not self.is_jumping:
            self.velocity = self.lift
            self.is_jumping = True

    def draw(self):
        screen.blit(self.frames[self.frame_index], (int(self.x), int(self.y)))

class Cactus:
    def __init__(self, base_speed):
        self.x = WIDTH
        self.y = HEIGHT - 40
        self.width = 30
        self.height = 40
        self.speed = base_speed
        self.image = CACTUS_IMG

    def update(self):
        self.x -= self.speed

    def draw(self):
        screen.blit(self.image, (int(self.x), int(self.y)))

    def collision(self, dino):
        dino_rect = pygame.Rect(dino.x, dino.y, dino.width, dino.height)
        cactus_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return dino_rect.colliderect(cactus_rect)

class Cloud:
    def __init__(self, speed):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(50, 150)  
        self.speed = speed

    def update(self):
        self.x -= self.speed
        if self.x + CLOUD_IMG.get_width() < 0:
            self.x = WIDTH  

    def draw(self):
        screen.blit(CLOUD_IMG, (self.x, self.y))

def draw_game_over(score):
    global high_score
    pygame.mixer.music.stop()
    update_high_score(score)
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("Game Over", True, BLACK)
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    
    screen.fill(WHITE)  
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 30))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2))
    
    replay_button = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 40, 100, 40)
    pygame.draw.rect(screen, GRAY, replay_button)
    replay_text = font.render("Replay", True, BLACK)
    screen.blit(replay_text, (WIDTH//2 - replay_text.get_width()//2, HEIGHT//2 + 45))
    
    pygame.display.flip()
    return replay_button

def main():
    global high_score, time_of_day
    high_score = load_high_score()  
    time_of_day = "day"  
    
    
    last_toggle_time = pygame.time.get_ticks()

    clouds = [Cloud(random.randint(1, 3)) for _ in range(3)]  

    while True:
        pygame.mixer.music.play(-1)
        dino = Dino()
        cacti = []
        score = 0
        
        font = pygame.font.Font(None, 36)  
        cactus_timer = 0
        CACTUS_GAP = 100
        base_speed = 5
        speed_increase_rate = 0.01

        running = True
        game_over = False
        
        while running:
            current_time = pygame.time.get_ticks()
            
           
            if current_time - last_toggle_time >= 15000: 
                time_of_day = "night" if time_of_day == "day" else "day"
                last_toggle_time = current_time  

            if not game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            dino.jump()
                
                
                dino.update()
                
                base_speed += speed_increase_rate
                if base_speed > 15:
                    base_speed = 15

                cactus_timer += 1
                if cactus_timer > CACTUS_GAP:
                    cacti.append(Cactus(base_speed))
                    cactus_timer = 0

                cacti_to_remove = []
                for cactus in cacti:
                    cactus.update()
                    if cactus.collision(dino):
                        game_over = True
                    if cactus.x + cactus.width < 0:
                        cacti_to_remove.append(cactus)
                        score += 1

                for cactus in cacti_to_remove:
                    cacti.remove(cactus)

                
                if time_of_day == "day":
                    screen.blit(BACKGROUND_DAY_IMG, (0, 0))
                    screen.blit(SUN_IMG, (WIDTH - 120, 20)) 
                else:
                    screen.blit(BACKGROUND_NIGHT_IMG, (0, 0))
                    screen.blit(MOON_IMG, (WIDTH - 120, 20))  

                for cloud in clouds:
                    cloud.update()
                    cloud.draw()

                pygame.draw.line(screen, BLACK, (0, HEIGHT-20), (WIDTH, HEIGHT-20), 2)
                dino.draw()
                for cactus in cacti:
                    cactus.draw()
                    
                score_text = font.render(f"Score: {score}", True, BLACK)
                high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
                screen.blit(score_text, (10, 10))  
                screen.blit(high_score_text, (10, 40))  
                
                pygame.display.flip()  
                clock.tick(FPS)

            if game_over:
                replay_button = draw_game_over(score)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if replay_button.collidepoint(event.pos):
                            running = False
                
                clock.tick(FPS)

        if not running and not game_over:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
