import pygame
import random
import os

WIDTH = 800
HEIGHT = 650
FPS = 30

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
size = []
sizeup = []
score = 0
bestscore = int(open('bestscore.txt', 'r', encoding = 'utf8').read())
over = False

class Player(pygame.sprite.Sprite):
    def __init__(self, type, ssize):
        pygame.sprite.Sprite.__init__(self)
        self.type = type 
        if type == 0:
            self.image = player_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.center = (WIDTH / 2, HEIGHT / 2)
        elif type == 1:
            self.image = pygame.Surface( ( 50, random.randint(200,400) ) )
            self.image.fill(GREEN)
            self.rect = self.image.get_rect()
            if ssize != 0:
                self.rect.bottomleft = (size[-1].rect.right + ssize, HEIGHT)
            else:
                self.rect.bottomleft = (WIDTH, HEIGHT)
            size.append(self)
            all_sprites.add(Player(2, ssize))
        elif type == 2:
            self.image = pygame.Surface( (50, HEIGHT - size[-1].rect.bottom + size[-1].rect.top - 150))
            self.image.fill(GREEN)
            self.rect = self.image.get_rect()
            self.rect.bottomleft =  (size[-1].rect.left, HEIGHT - size[-1].rect.bottom + size[-1].rect.top - 150)
            sizeup.append(self)
    def update(self):
        global score, over 
        if self.type == 0:
            if pygame.time.get_ticks() % 1 == 0:
                self.rect.y += 6
            if self.rect.bottom < 0:
                over = True 
            if self.rect.top > HEIGHT:
                over = True
        else:
            if pygame.time.get_ticks() % 1 == 0:
                self.rect.x -= 6
            if self.rect.right < 0:
                if self.type == 1:
                    sizeup[ size.index(self) ].kill()
                    self.kill()
                    all_sprites.add(Player(1, 210))
                    sizeup.pop(size.index(self))
                    size.pop(size.index(self))
                    score += 1
    def fly(self):
        self.rect.y -= 80

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
font = pygame.font.Font(None, 40)
text = font.render("Game over!", True, [255, 255, 255])
text2 = font.render(f"Score: {score}", True, [255, 255, 255])
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game_folder = os.path.dirname(__file__)
player_img = pygame.image.load(os.path.join(game_folder, 'Bird.png')).convert()
back_img = pygame.image.load(os.path.join(game_folder, 'background.gif')).convert()
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock() 
all_sprites = pygame.sprite.Group()
player = Player(0, 0)
all_sprites.add(player)
all_sprites.add(Player(1,0))
for i in range(4):
    all_sprites.add(Player(1,210)) 
# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.fly()
    # Обновление
    all_sprites.update()
    # Рендеринг
    screen.blit(back_img, [0,0])
    all_sprites.draw(screen)
    screen.blit(font.render(f"Best Score: {bestscore}", True, [255, 255, 255]), [0, 0])
    screen.blit(font.render(f"Score: {score}", True, [255, 255, 255]), [WIDTH/2, 0])
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()
    if len(size) > 0:
        hits = pygame.sprite.spritecollide(player, size, False) 
        hits2 = pygame.sprite.spritecollide(player, sizeup, False)
        if hits or hits2:
            over = True 
        if over == True:
            if score > bestscore:
                bestscore = score
            open('bestscore.txt', 'w', encoding = 'utf8').write(str(bestscore))
            score = 0
            screen.blit(text, [WIDTH/2, HEIGHT/2] )
            pygame.display.flip()
            pygame.time.wait(500)
            for i in range(len(size)):
                size[-1].kill()
                size.pop(-1)
            for i in range(len(sizeup)):
                sizeup[-1].kill()
                sizeup.pop(-1)
            all_sprites.add(Player(1,0))
            for i in range(4):
                all_sprites.add(Player(1, 210))
            player.rect.center = [WIDTH/2, HEIGHT/2]
            screen.blit(back_img, [0,0])
            all_sprites.draw(screen)
            pygame.display.flip()
            over = False
pygame.quit()