import pygame
import sys
from pygame.locals import *
import time

TOPLEFT = (50,50)
TOPRIGHT = (450,50)
BOTTOMLEFT = (50,450)
BOTTOMRIGHT = (450,450)
PLAYER_LIVES = 3
Coords = [TOPLEFT, TOPRIGHT, BOTTOMRIGHT, BOTTOMLEFT]
MAINBORDER = [TOPLEFT, TOPRIGHT, BOTTOMRIGHT, BOTTOMLEFT]
points = []
state = 0
currDir = None
pygame.init()
RED = pygame.Color(255,0,0)
BLUE = pygame.Color(0,0,255)
GREEN = pygame.Color(0,255,0)
WHITE = pygame.Color(255,255,255)
BLACK = pygame.Color(0,0,0)

#Display window
display = pygame.display.set_mode((500,500))
pygame.display.set_caption("Qix")

#FPS
FPS = pygame.time.Clock()
FPS.tick(60)

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        if self.start_time:
            return time.perf_counter() - self.start_time
        else:
            return 1

#First enemy
class Sparx(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("spark.png")
        self.surf = pygame.Surface((9,9))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.surf.get_rect(center=(50,50))

    def move(self):
        #TODO: Movement for changing list of coords
        x = self.rect.centerx
        y = self.rect.centery
        if y == 50:
            if x < 450:
                self.rect.move_ip(5,0)
            else:
                self.rect.move_ip(0,5)
        if x == 450:
            if y < 450:
                self.rect.move_ip(0,5)
            else:
                self.rect.move_ip(-5,0)
        if y == 450:
            if x > 50:
                self.rect.move_ip(-5,0)
            else:
                self.rect.move_ip(0,-5)
        if x == 50:
            if y > 50:
                self.rect.move_ip(0,-5)
            else:
                self.rect.move_ip(5,0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png")
        self.surf = pygame.Surface((10,10))
        self.rect = self.surf.get_rect(center=(BOTTOMRIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.coords = (Coords[2], Coords[3])
        self.next = (Coords[1], Coords[0])

    def update(self):
        key = pygame.key.get_pressed()
        if self.rect.centerx < 450:
            if key[K_RIGHT] and (self.rect.centery == 50 or self.rect.centery == 450):
                self.rect.move_ip(5,0)
        if self.rect.centerx > 50:
            if key[K_LEFT] and (self.rect.centery == 50 or self.rect.centery == 450) :
                self.rect.move_ip(-5,0)
        if self.rect.centerx == 50 or self.rect.centerx == 450:
            if self.rect.centery > 50:
                if key[K_UP]:
                    self.rect.move_ip(0, -5)
            if self.rect.centery < 450:
                if key[K_DOWN]:
                    self.rect.move_ip(0,5)
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def move(self, coord1, coord2, key):
        left = lambda: coord1[0]-5 if coord1[0] < coord2[0] else coord2[0]-5
        top = lambda: coord1[1]-5 if coord1[1] < coord2[1] else coord2[1]-5
        #Clamp uses center of rect, so adjustments made based on sprite size.
        bound = Rect((left(),top()),(abs((coord1[0]-coord2[0]))+10,abs(coord1[1]-coord2[1])+10))
        if key[K_LEFT]:
            self.rect.move_ip(-5,0)
            self.rect.clamp_ip(bound)
        if key[K_RIGHT]:
            self.rect.move_ip(5,0)
            self.rect.clamp_ip(bound)
        if key[K_UP]:
            self.rect.move_ip(0, -5)
            self.rect.clamp_ip(bound)
        if key[K_DOWN]:
            self.rect.move_ip(0, 5)
            self.rect.clamp_ip(bound)

    # Movement without bounds
    def moveTest(self):
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            self.rect.move_ip(-5,0)
        if key[K_RIGHT]:
            self.rect.move_ip(5,0)
        if key[K_UP]:
            self.rect.move_ip(0,-5)
        if key[K_DOWN]:
            self.rect.move_ip(0,5)

    def is_x_y(self, coord1, coord2):
        if coord1[0] == coord2[0]:
            return None #line seg is vertical (y)
        return 1 #line segment is horizontal (x)

    def theory(self):
        global Coords
        global currDir
        global points
        global state
        toDel = []
        key = pygame.key.get_pressed()
        if state == 0:
            spot = self.rect.center
            prev = None
            next = None
            current = None
            for l in range(len(Coords)):
                if Coords[l] == spot:
                    prev = Coords[l-1]
                    current = Coords[l]
                    next = Coords[(l+1)%(len(Coords))]

            if not prev: #Spot isn't in coords (no dup for x AND y vals)
                for m in range(len(Coords)):
                    if Coords[m][0] == spot[0] or Coords[m][1] == spot[1]: #Same x/y val
                        #Found a match, now find the other coord of the line seg.
                        if Coords[m-1][0] == spot[0] or Coords[m-1][1] == spot[1]:
                            prev = Coords[m-1]
                            next = Coords[m]
                        else:
                            prev = Coords[m]
                            next = Coords[(m+1)%(len(Coords)-1)]

            #Consider implementing below as a method somehow
            if state == 0:
                if key[K_SPACE]:
                    state = 1
                elif current:  # Is on a node, enable x and y movement
                    if self.is_x_y(prev, current):  # if prev-current is the horizontal line
                        if key[K_LEFT] or key[K_RIGHT]:
                            self.move(prev, current, key)
                        elif key[K_UP] or key[K_DOWN]:
                            self.move(current, next, key)
                    else:
                        if key[K_LEFT] or key[K_RIGHT]:
                            self.move(current, next, key)
                        elif key[K_UP] or key[K_DOWN]:
                            self.move(prev, current, key)
                else:
                    self.move(prev, next, key)

        if state == 1:
            #Simple code for area capture. Lets you go ANYWHERE, placeholder/example only.
            if key[K_0]:
                state = 2
            elif key[K_LEFT]:
                if currDir != K_LEFT:
                    points.append(self.rect.center)
                self.rect.move_ip(-5, 0)
                currDir = K_LEFT
            elif key[K_RIGHT]:
                if currDir != K_RIGHT:
                    points.append(self.rect.center)
                self.rect.move_ip(5, 0)
                currDir = K_RIGHT
            elif key[K_UP]:
                if currDir != K_UP:
                    points.append(self.rect.center)
                self.rect.move_ip(0, -5)
                currDir = K_UP
            elif key[K_DOWN]:
                if currDir != K_DOWN:
                    points.append(self.rect.center)
                self.rect.move_ip(0, 5)
                currDir = K_DOWN
        if state == 2: #Should activates once player successfully finishes area
            #Old code, needs to be updated to more recent algorithm
            #Doesn't actually work properly
            points.append(self.rect.center)
            if len(points) >= 3:
                for i in points:
                    temp = Coords.copy()
                    temp.append(temp[0])
                    found = False
                    for j in range(len(Coords)):
                        x = (temp[j][0], temp[j + 1][0]) #X bounds
                        y = (temp[j][1], temp[j + 1][1]) #Y bounds
                        if i[0] >= x[0] and i[0] <= x[1]:
                            if i[1] >= y[0] and i[1] <= y[1]:
                                found = True
                                Coords.insert(j + 1, i)
                    if not found:
                        smallest = sys.maxsize
                        smallestIn = 0
                        for k in range(len(temp) - 1):
                            current = abs(temp[k][0] - i[0]) + abs(temp[k][1] - i[1])
                            if smallest < current:
                                smallest = current
                                smallestIn = k
                        Coords.pop(smallestIn)
                        Coords.insert(smallestIn, i)
                state = 0


class Border(pygame.sprite.Sprite):
    #Code for using sprites for borders. Unknown if this will be used yet.
    def __init__(self, rect):
        super().__init__()
        self.surf = pygame.Surface((rect))
        self.rect = self.surf.get_rect()

    def draw(self, surface, colour):
        pygame.draw.rect(surface, colour, self.rect)

def drawBorder(Cord, dis): #Draws all the lines for borders based on list of coordinates.
    for p1, p2 in offset(Cord):
        if p1 and p2:
            pygame.draw.line(dis, WHITE, p1, p2)
    pygame.draw.line(dis, WHITE, Cord[-1], Cord[0])

def offset(iter):
    last = None
    for curr in iter:
        yield last, curr
        last = curr
#B = Border() #TODO: adapt for the conquest rectangle sprites
P1 = Player()
E1 = Sparx()
Timer = Timer()
enemies = pygame.sprite.Group()
enemies.add(E1)
sprites = pygame.sprite.Group()
#sprites.add(B)
#sprites.add(P1)
#sprites.add(E1)
font = pygame.font.SysFont("Times New Roman",16)
temp = "Lives:",str(PLAYER_LIVES)
lives = font.render(("Lives: "+str(PLAYER_LIVES)),True,RED)
livesRect = lives.get_rect()
livesRect.topright = (500,0)
lose = font.render('You lost!',True,RED,BLACK)
loseRect = lose.get_rect()
loseRect.center = (250,250)

while True:
    E1.move()
    P1.theory()
    #P1.moveTest() #Movement w/ no bounds (TESTING USE ONLY)
    display.fill(BLACK)
    drawBorder(MAINBORDER, display)
    drawBorder(Coords, display)
    P1.draw(display)
    E1.draw(display)
    lives = font.render(("Lives: "+str(PLAYER_LIVES)), True, RED)
    display.blit(lives,livesRect)
    pygame.display.flip()
    FPS.tick(60)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.sprite.spritecollideany(P1, enemies):
        if Timer.stop() > 0.1:
            if PLAYER_LIVES <= -100:
                #display.fill(BLACK)
                display.blit(lose, loseRect)
                pygame.display.update()
                time.sleep(4)
                pygame.quit()
                sys.exit()
            else:
                PLAYER_LIVES -= 1
        Timer.start()
        # TODO:Move sparx, keep player in initial spot.
