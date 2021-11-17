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
players = []
machine = []
machineunwork = []
size = []
sizeup = []
score = 0
bestscore = int(open('bestscore.txt', 'r', encoding = 'utf8').read())
over = False
kop = 0

class machinne():
    def __init__(self, scales = [random.random(), random.random(), random.random()]):
        self.neurons = [ [ scales[0], scales[1], scales[2] ],[0] ]
        self.player = Player(self)
        all_players.add(self.player)
    def work(self):
        i = 1
        now = size[0]
        while now.rect.right - self.player.rect.left < 0:
            now = size[i]
            i += 1
        for i in size:
            if i.rect.right - self.player.rect.left <  now.rect.right - self.player.rect.left and i.rect.right - self.player.rect.left > -1:
                now = i 
        output = self.neurons[0][0] * (now.rect.right - self.player.rect.left) + self.neurons[0][1] * (self.player.rect.bottom - now.rect.top) + self.neurons[0][2] *   (sizeup[size.index(now)].rect.bottom - self.player.rect.top) 
        if output > 1:
            self.player.fly()
class Player(pygame.sprite.Sprite):
    def __init__(self, AI):
        pygame.sprite.Sprite.__init__(self)
        self.AI = AI
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        players.append(self)
    def update(self):
        if pygame.time.get_ticks() % 1 == 0:
            self.rect.y += 6
        self.AI.work()
        if self.rect.bottom < 0:
            self.died()
        if self.rect.top > HEIGHT:
            self.died()
        hits = pygame.sprite.spritecollide(self, size, False) 
        hits2 = pygame.sprite.spritecollide(self, sizeup, False)
        if hits or hits2:
            self.died()
    def fly(self):
        self.rect.y -= 80
    def died(self):
        global players, machine, machineunwork
        players.remove(self)
        machineunwork.append(self.AI)
        machine.remove(self.AI)
        self.kill()
        print(len(players))

def study():
    global machine, machineunwork
    open('весы.txt', 'w', encoding = 'utf8').write(str(machineunwork[-1].neurons))
    machine.append(cop(machineunwork[-1]))
    machine.append(cop(machineunwork[-2]))
    machine.append(cop(machineunwork[-3]))
    machine.append(cop(machineunwork[-4]))
    machine.append(cop(machineunwork[-5]))
    machine.append(gen(machineunwork[-1], machineunwork[-3]))
    machine.append(gen(machineunwork[-1], machineunwork[-4]))
    machine.append(gen(machineunwork[-1], machineunwork[-5]))
    machine.append(gen(machineunwork[-1], machineunwork[-2]))
    #machine.append(gen(machineunwork[-1], machineunwork[-3]))
    #machine.append(gen(machineunwork[-3], machineunwork[-2]))
    for i in range(3):
        for c in range(3):
            machine.append( ben( machineunwork[-1] , c ) )
    for i in range(3):
        for c in range(3):
            machine.append( ben( machineunwork[-2], c))
    for i in range(3):
        for c in range(3):
            machine.append( ben( machineunwork[-3] , c ) )
    for i in range(3):
        for c in range(3):
            machine.append( ben( machineunwork[-4], c))
    for i in range(3):
        for c in range(3):
            machine.append( ben( machineunwork[-5] , c ))
    machine.append(machinne(scales = read()))
    #machine.append(machinne(scales = ))
    #machine.append(cop(machineunwork[-1]))
    #machine.append(cop(machineunwork[-2]))
    #machine.append(cop(machineunwork[-3]))
    machineunwork.clear()
def gen(c, b):
    a = machinne()
    for i in range(3):
        a.neurons[0][i] = (c.neurons[0][i] + b.neurons[0][i]) / 2
    return a 

def ben(c, i):
    a = machinne()
    for b in range(3):
        a.neurons[0][b] = c.neurons[0][b]
    if random.randint(0,1) == 0:
        a.neurons[0][i] += random.uniform(0, 1)
    else:
        a.neurons[0][i] -= random.uniform(0, 1)
    return a
'''
if random.randint(0,1) == 0:
        a.neurons[0][i] += random.uniform(0, 0.01)
    else:
        a.neurons[0][i] -= random.uniform(0, 0.01)
'''
def cop(c):
    a = machinne()
    for b in range(3):
        a.neurons[0][b] = c.neurons[0][b]
    return a
def zap(kap):
    b = f'{kap.neurons[0][0]},{kap.neurons[0][1]},{kap.neurons[0][2]}'
    open('лучшиевесы.txt', 'w', encoding = 'utf8').write(b)

def read():
    b = open('лучшиевесы.txt', 'r', encoding = 'utf8').read()
    b = b.split(',')
    for i in b:
        b[b.index(i)] = float(i)
    return b

class barrier(pygame.sprite.Sprite):
    def __init__(self, type, ssize):
        pygame.sprite.Sprite.__init__(self)
        self.type = type 
        if type == 0:
            self.image = pygame.Surface( ( 50, random.randint(200, 400) ) )
            #200, 350
            self.image.fill(GREEN)
            self.rect = self.image.get_rect()
            if ssize != 0:
                self.rect.bottomleft = (size[-1].rect.right + ssize, HEIGHT)
            else:
                self.rect.bottomleft = (WIDTH, HEIGHT)
            size.append(self)
            all_sprites.add(barrier(1, ssize))
        elif type == 1:
            self.image = pygame.Surface( (50, HEIGHT - size[-1].rect.bottom + size[-1].rect.top - 155))
            self.image.fill(GREEN)
            self.rect = self.image.get_rect()
            self.rect.bottomleft =  (size[-1].rect.left, HEIGHT - size[-1].rect.bottom + size[-1].rect.top - 155)
            #160
            sizeup.append(self)
    def update(self):
        global score, bestscore
        if pygame.time.get_ticks() % 1 == 0:
            self.rect.x -= 6
        if self.rect.right < 0:
            if self.type == 0:
                sizeup[ size.index(self) ].kill()
                self.kill()
                all_sprites.add( barrier(0, 210) )
                sizeup.pop(size.index(self))
                size.remove(self)
                score += 1
                if score > bestscore:
                    bestscore = score
                    open('bestscore.txt', 'w', encoding = 'utf8').write(str(bestscore))
                    zap(machine[0])

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game_folder = os.path.dirname(__file__)
player_img = pygame.image.load(os.path.join(game_folder, 'Bird.png')).convert()
back_img = pygame.image.load(os.path.join(game_folder, 'background.gif')).convert()
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock() 
all_sprites = pygame.sprite.Group()
all_players = pygame.sprite.Group()
all_sprites.add(barrier(0,0))
for i in range(5):
    all_sprites.add(barrier(0,210)) 
#machine.append(machinne(scales = [random.random(), random.random(), random.random()]))
machine.append(machinne(scales = read()))
for i in range(54):
    machine.append(machinne(scales = [random.random(), random.random(), random.random()]))
# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(999)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
    # Обновление
    all_players.update()
    all_sprites.update()
    # Рендеринг
    screen.blit(back_img, [0,0])
    all_players.draw(screen)
    all_sprites.draw(screen)
    screen.blit(font.render(f"Best Score: {bestscore}", True, [255, 255, 255]), [0, 0])
    screen.blit(font.render(f"Score: {score}", True, [255, 255, 255]), [WIDTH/2, 0])
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()
    if len(players) == 0:
        over = True
    if over == True:
        if score > bestscore:
            bestscore = score
            open('bestscore.txt', 'w', encoding = 'utf8').write(str(bestscore))
            zap(machineunwork[-1])
        score = 0 
        pygame.time.wait(100)
        study()
        for i in range(len(size)):
            size[-1].kill()
            size.pop(-1)
        for i in range(len(sizeup)):
            sizeup[-1].kill()
            sizeup.pop(-1)
        all_sprites.add(barrier(0,0))
        for i in range(5):
            all_sprites.add(barrier(0,210)) 
        screen.blit(back_img, [0,0])
        all_players.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        over = False      
pygame.quit()