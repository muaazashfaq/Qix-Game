import pygame
import sys
from pygame.locals import *
import time
import math
import random
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LinearRing


TOPLEFT = (50,50)
TOPRIGHT = (450,50)
BOTTOMLEFT = (50,450)
BOTTOMRIGHT = (450,450)
PLAYER_LIVES = 3
Coords = [TOPLEFT, TOPRIGHT, BOTTOMRIGHT, BOTTOMLEFT]
inside = []
MAINBORDER = [TOPLEFT, TOPRIGHT, BOTTOMRIGHT, BOTTOMLEFT]
points = []
follow = []
followSlow = []
state = 0
currDir = None
startDir = None
claimed = 0
speed = 10

def area(points):
    #Code for finding area of polygon from coordinates.
    #Sourced from:
    #https://www.mathopenref.com/coordpolygonarea2.html
    j = len(points) -1
    area = 0
    for i in range(len(points)):
        area += (points[i][0]+points[j][0])*(points[i][1]-points[j][1])
        j = i
    return area/2

totalA = area(Coords)

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
        self.speed = 4

    def temp(self):
        global Coords


    def move(self):
        #TODO: Movement for changing list of coords
        x = self.rect.centerx
        y = self.rect.centery
        if y == 50:
            if x < 450:
                self.rect.move_ip(self.speed,0)
            else:
                self.rect.move_ip(0,self.speed)
        if x == 450:
            if y < 450:
                self.rect.move_ip(0,self.speed)
            else:
                self.rect.move_ip(-self.speed,0)
        if y == 450:
            if x > 50:
                self.rect.move_ip(-self.speed,0)
            else:
                self.rect.move_ip(0,-self.speed)
        if x == 50:
            if y > 50:
                self.rect.move_ip(0,-self.speed)
            else:
                self.rect.move_ip(self.speed,0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Qix(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Qix.png")
        self.surf = pygame.Surface((20,20))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.surf.get_rect(center=(250, 250))
        self.poly = Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])

    def update(self):
        global Coords
        polygon = Polygon(Coords)
        found = False
        arr = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
        tl = self.rect.topleft
        tr = self.rect.topright
        br = self.rect.bottomright
        bl = self.rect.bottomleft
        while not found:
            key = random.choice(arr)
            if key == K_UP:
                qix = Polygon([(tl[0], tl[1]-10), (tr[0], tr[1]-10), (br[0], br[1]-10), ([bl[0], bl[1]-10])])
                if polygon.contains(qix):
                    found = True
                    self.rect.y -= 10
                else:
                    arr.remove(K_UP)
            if key == K_DOWN:
                qix = Polygon([(tl[0], tl[1] + 10), (tr[0], tr[1] + 10), (br[0], br[1] + 10), ([bl[0], bl[1] + 10])])
                if polygon.contains(qix):
                    found = True
                    self.rect.y += 10
                else:
                    arr.remove(K_DOWN)
            if key == K_LEFT:
                qix = Polygon([(tl[0]-10, tl[1]), (tr[0]-10, tr[1]), (br[0]-10, br[1]), ([bl[0]-10, bl[1]])])
                if polygon.contains(qix):
                    found = True
                    self.rect.x -= 10
                else:
                    arr.remove(K_LEFT)
            if key == K_RIGHT:
                qix = Polygon([(tl[0] + 10, tl[1]), (tr[0] + 10, tr[1]), (br[0] + 10, br[1]), ([bl[0] + 10, bl[1]])])
                if polygon.contains(qix):
                    found = True
                    self.rect.x += 10
                else:
                    arr.remove(K_RIGHT)
        self.poly = Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def move(self, coord1, coord2, key, speed):
        left = lambda: coord1[0]-5 if coord1[0] < coord2[0] else coord2[0]-5
        top = lambda: coord1[1]-5 if coord1[1] < coord2[1] else coord2[1]-5
        #Clamp uses center of rect, so adjustments made based on sprite size.
        bound = Rect((left(),top()),(abs((coord1[0]-coord2[0]))+10,abs(coord1[1]-coord2[1])+10))
        if key[K_LEFT]:
            self.rect.move_ip(-speed,0)
            self.rect.clamp_ip(bound)
        if key[K_RIGHT]:
            self.rect.move_ip(speed,0)
            self.rect.clamp_ip(bound)
        if key[K_UP]:
            self.rect.move_ip(0, -speed)
            self.rect.clamp_ip(bound)
        if key[K_DOWN]:
            self.rect.move_ip(0, speed)
            self.rect.clamp_ip(bound)

    def isValid(self, point, coord1, coord2):
        #Checks if point is between the coords
        #x and y bounds [low, high]
        x = lambda: [coord1[0],coord2[0]] if coord1[0] < coord2[0] else [coord2[0],coord1[0]]
        y = lambda: [coord1[1], coord2[1]] if coord1[1] < coord2[1] else [coord2[1], coord1[1]]
        x = x()
        y = y()
        if point[0] <= x[1] and point[0] >= x[0]:
            return (point[1] <= y[1] and point[1] >= y[0])
        return False

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

    def onBorder(self):
        global Coords
        for p1, p2 in offset(Coords):
            if p1 and p2:
                if self.isValid(self.rect.center, p1, p2):
                    return True
        if self.isValid(self.rect.center, Coords[0], Coords[-1]):
            return True
        return False

    def theory(self, qix, display):
        global claimed
        global inside
        global Coords
        global currDir
        global startDir
        global points
        global state
        global speed
        global follow
        global followSlow
        key = pygame.key.get_pressed()
        if key[K_1]:
            print(Coords)
            print(self.rect.center)
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
                            if self.isValid(spot, prev, next):
                                break
                        else:
                            prev = Coords[m]
                            next = Coords[(m+1)%(len(Coords))]
                            if self.isValid(spot, prev, next):
                                break
            if key[K_2]:
                print(prev, current, next)

            if state == 0:
                speed = 10
                if key[K_SPACE]:
                    state = 1
                    speed = 5
                    followSlow.append(self.rect.center)
                if key[K_v]:
                    state = 1
                    speed = 10
                    follow.append(self.rect.center)
                elif current:  # Is on a node, enable x and y movement
                    if self.is_x_y(prev, current):  # if prev-current is the horizontal line
                        if key[K_LEFT] or key[K_RIGHT]:
                            self.move(prev, current, key, speed)
                        elif key[K_UP] or key[K_DOWN]:
                            self.move(current, next, key, speed)
                    else:
                        if key[K_LEFT] or key[K_RIGHT]:
                            self.move(current, next, key, speed)
                        elif key[K_UP] or key[K_DOWN]:
                            self.move(prev, current, key, speed)
                else:
                    self.move(prev, next, key, speed)

        if state == 1:
            if key[K_v]:
                speed = 10
                follow.append(self.rect.center)
            if key[K_LEFT]:
                if not startDir:
                    startDir = K_LEFT
                if currDir != K_LEFT: #e.g. if currDir = right, can't move left.
                    points.append(self.rect.center)
                if self.rect.centerx > 50:
                    self.rect.move_ip(-speed, 0)
                if not Polygon(Polygon(Coords).buffer(6).exterior).contains\
                            (Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                    self.rect.move_ip(speed, 0)
                    self.rect.move_ip(-5, 0)
                    if not Polygon(Polygon(Coords).buffer(6).exterior).contains \
                                (Polygon(
                                [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                        self.rect.move_ip(speed, 0)
                if not currDir:
                    if self.onBorder():
                        state = 0
                        points = []
                        startDir = None
                        currDir = None
                currDir = K_LEFT
            elif key[K_RIGHT]:
                if not startDir:
                    startDir = K_RIGHT
                if currDir != K_RIGHT:
                    points.append(self.rect.center)
                if self.rect.centerx < 450:
                    self.rect.move_ip(speed, 0)
                if not Polygon(Polygon(Coords).buffer(6).exterior).contains\
                            (Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                    self.rect.move_ip(-speed, 0)
                    self.rect.move_ip(5, 0)
                    if not Polygon(Polygon(Coords).buffer(6).exterior).contains \
                                (Polygon(
                                [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                        self.rect.move_ip(-speed, 0)
                if not currDir:
                    if self.onBorder():
                        state = 0
                        points = []
                        startDir = None
                        currDir = None
                currDir = K_RIGHT
            elif key[K_UP]:
                if not startDir:
                    startDir = K_UP
                if currDir != K_UP:
                    points.append(self.rect.center)
                if self.rect.centery > 50:
                    self.rect.move_ip(0, -speed)
                if not Polygon(Polygon(Coords).buffer(6).exterior).contains\
                            (Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                    self.rect.move_ip(0, speed)
                    self.rect.move_ip(0, -5)
                    if not Polygon(Polygon(Coords).buffer(6).exterior).contains \
                                (Polygon(
                                [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                        self.rect.move_ip(0, speed)
                if not currDir:
                    if self.onBorder():
                        state = 0
                        points = []
                        startDir = None
                        currDir = None
                currDir = K_UP
            elif key[K_DOWN]:
                if not startDir:
                    startDir = K_DOWN
                if currDir != K_DOWN:
                    points.append(self.rect.center)
                if self.rect.centery < 450:
                    self.rect.move_ip(0, speed)
                if not Polygon(Polygon(Coords).buffer(6).exterior).contains\
                            (Polygon([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                    self.rect.move_ip(0 , -speed)
                    self.rect.move_ip(0, 5)
                    if not Polygon(Polygon(Coords).buffer(6).exterior).contains \
                                (Polygon(
                                [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])):
                        self.rect.move_ip(0, -speed)
                if not currDir:
                    if self.onBorder():
                        state = 0
                        points = []
                        startDir = None
                        currDir = None
                currDir = K_DOWN
            if speed == 10:
                follow.append(self.rect.center)
            else:
                followSlow.append(self.rect.center)
            self.trail(follow, display, (209, 59, 194))
            self.trail(followSlow, display, (222, 110, 24))

            for p1, p2 in offset(Coords): #Exit area collection on success
                if p1 and p2:
                    if self.isValid(self.rect.center, p1, p2) and startDir and currDir:
                        state = 2
            if self.isValid(self.rect.center, Coords[0], Coords[-1]) and startDir and currDir:
                state = 2

            for p1, p2 in offset(points): #Die/reset on collision with created line
                if p1 and p2:
                    if self.isValid(self.rect.center, p1, p2):
                        print('reset')
                        state = 0
                        self.rect.center = points[0]
                        points = []
                        startDir = None
                        currDir = None
                        follow = []
                        followSlow = []

        if state == 2:
            points.append(self.rect.center) #May not be needed, unknown how points are implemented in area capture
            #Delete points between start and end exclusive
            start = None
            end = None
            self.clockwise(points)

            for o in range(len(Coords)):
                if start == None:
                    #First point to contain dup axis
                    if self.isValid(points[0], Coords[o], Coords[(o + 1) % (len(Coords))]):
                            start = o
                if end == None:
                    if self.isValid(points[-1], Coords[o], Coords[(o + 1) % (len(Coords))]):
                        if Coords[(o + 1) % (len(Coords))] == points[-1]:
                            end = (o +2) % (len(Coords))
                        else:
                            end = (o + 1) % (len(Coords))
            print(start, end)

            if start != None and end != None:
                if start == end and False:
                    #Corner case when incasing 50, 50
                    inside.append(points)
                    for n in points:
                        Coords.insert(start+1, n)
                else:
                    inside.append(points)
                    temp = Coords.copy()
                    temp1 = self.crossSection(start, end, Coords, points, qix)
                    if Polygon(temp1[0]).contains(qix.poly):
                        Coords = temp1[0].copy()
                    else:
                        Coords = temp1[1].copy()
                    print(Coords)
            points = []
            state = 0
            startDir = None
            currDir = None
            follow = []
            followSlow = []
            i = 0
            while i < len(Coords):
                if Coords[i] == Coords[(i+1)%(len(Coords))]:
                    Coords.pop((i+1)% len(Coords))
                i += 1
            claimed = totalA - Polygon(Coords).area

    def trail(self, points, display, colour):
        for p1, p2 in offset(points):
            if p1 and p2:
                pygame.draw.line(display, colour, p1, p2)

    def closer(self, p1, p2, testp):
        d1 = math.sqrt(math.pow(p1[0]-testp[0], 2)+ math.pow(p1[1]-testp[1], 2)) #Distance formula
        d2 = math.sqrt(math.pow(p2[0] - testp[0], 2) + math.pow(p2[1] - testp[1], 2))
        if d1 <= d2:
            return True
        return None #last item is closer

    def clockwise(self, points):
        global currDir
        global startDir
        ccw = [[K_DOWN, K_LEFT], [K_LEFT, K_UP], [K_UP, K_RIGHT], [K_RIGHT, K_DOWN]]
        directions = [K_DOWN, K_UP, K_LEFT, K_RIGHT]
        opDir = [K_UP, K_DOWN, K_RIGHT, K_LEFT]
        sI = directions.index(startDir)
        cI = opDir.index(currDir)
        #orders points in closewise direction
        if [startDir, currDir] in ccw:
            points.reverse()
        if sI == cI:
            if startDir == K_UP:
                if points[0][0] < points[-1][0]:
                    points.reverse()
            if startDir == K_DOWN:
                if points[0][0] > points[-1][0]:
                    points.reverse()
            if startDir == K_LEFT:
                if points[0][1] < points[-1][1]:
                    points.reverse()
            if startDir == K_RIGHT:
                if points[0][1] > points[-1][1]:
                    points.reverse()

    def axis(self, p1, p2):
        if p1[0] == p2[0] or p1[1] == p2[1]:
            return True
        return False

    def axis3(self, p1, p2, p3):
        if (p1[0] == p2[0] and p1 [0] == p3[0]) or (p1[1] == p2[1] and p1[1] == p3[1]):
            return True
        return False

    def crossSection(self, start, end, input, points, qix):
        #Function to provide 2 output lists for a cross-section area
        out1 = input.copy()
        out2 = input.copy()
        if start > end:
            start, end = end, start

        for i in range(abs(start-end)-1):#(Start - end) non inclusive
            out1.pop(start+1)
        if out1:
            for j in range(len(out1)):
                if out1[j] == input[start]:
                    newStart = j
                if out1[j] == input[end]:
                    newEnd = j
            if self.axis(out1[newStart], points[0]) and self.axis(out1[newEnd], points[-1]):
                if self.axis(out1[newStart], points[-1]) and self.axis(out1[newEnd], points[0]):
                    if not self.closer(points[0], points[-1], out1[newStart]):
                        points.reverse()
            else:
                points.reverse()
            for p in range(len(points)):
                out1.insert(newStart + p + 1, points[p])

        comp = input.copy()
        # Inclusive start-end
        for i in range(abs(end - start) + 1):
            comp.pop(start)
        if comp:
            for j in range(len(comp)):
                if comp[j] == input[start - 1]:
                    newStart = j
                if comp[j] == input[(end + 1) % (len(input))]:
                    newEnd = j
            if self.axis(comp[newStart], points[0]) and self.axis(comp[newEnd], points[-1]):
                if self.axis(comp[newStart], points[-1]) and self.axis(comp[newEnd], points[0]):
                    if not self.closer(points[0], points[-1], comp[newStart]):
                        points.reverse()
            else:
                points.reverse()
            for p in range(len(points)):
                comp.insert(newStart + 1 + p, points[p])
        if validBounds(out1):
            if validBounds(comp):
                if Polygon(comp).contains(qix.poly):
                    out1 = comp.copy()
        else:
            out1 = comp.copy()

        i = (end+1)%(len(out2))
        toDel = []
        while i != start: #Non inclusive end-start
            toDel.append(out2[i])
            i = (i+1)%(len(out2))
        for d in toDel:
            out2.remove(d)
        if out2:
            for j in range(len(out2)):
                if out2[j] == input[end]:
                    newStart = j
                if out2[j] == input[start]:
                    newEnd = j
            if self.axis(out2[newStart], points[0]) and self.axis(out2[newEnd], points[-1]):
                if self.axis(out2[newStart], points[-1]) and self.axis(out2[newEnd], points[0]):
                    if not self.closer(points[0], points[-1], out2[newStart]):
                        points.reverse()
            else:
                points.reverse()
            for p in range(len(points)):
                out2.insert(newStart + p + 1, points[p])

        comp = input.copy()
        if comp[start] not in toDel:
            toDel.append(comp[start])
        if comp[end] not in toDel:
            toDel.append(comp[end])
        for d in toDel:
            comp.remove(d)
        if comp:
            for j in range(len(comp)):
                if comp[j] == input[end - 1]:
                    newStart = j
                if comp[j] == input[(start + 1) % (len(input))]:
                    newEnd = j
            if self.axis(comp[newStart], points[0]) and self.axis(comp[newEnd], points[-1]):
                if self.axis(comp[newStart], points[-1]) and self.axis(comp[newEnd], points[0]):
                    if not self.closer(points[0], points[-1], comp[newStart]):
                        points.reverse()
            else:
                points.reverse()

            for p in range(len(points)):
                comp.insert(newStart + p + 1, points[p])
        if validBounds(out2):
            if validBounds(comp):
                if Polygon(comp).contains(qix.poly):
                        out2 = comp.copy()
        else:
            if validBounds(comp):
                if Polygon(comp).contains(qix.poly):
                    out2 = comp.copy()

        rem = []
        for p in range(len(out1)):
            if self.axis3(out1[p], out1[(p+1)%(len(out1))], out1[(p+2)%(len(out1))]):
                rem.append(out1[(p+1)%(len(out1))])
        for p in rem:
            out1.remove(p)
        rem = []
        for p in range(len(out2)):
            if self.axis3(out2[p], out2[(p + 1) % (len(out2))], out2[(p + 2) % (len(out2))]):
                rem.append(out2[(p + 1) % (len(out2))])
        for p in rem:
            out2.remove(p)
        return [out1, out2]

def drawBorder(Cord, dis): #Draws all the lines for borders based on list of coordinates.
    for p1, p2 in offset(Cord):
        if p1 and p2:
            pygame.draw.line(dis, WHITE, p1, p2)
    pygame.draw.line(dis, WHITE, Cord[-1], Cord[0])

def drawBoard(Cords, display):
    pygame.draw.polygon(display, BLACK, Cords)

def drawBound(Cord, dis):
    for i in Cord:
        for p1, p2 in offset(i):
            if p1 and p2:
                pygame.draw.line(dis, GREEN, p1, p2)

def offset(iter):
    last = None
    for curr in iter:
        yield last, curr
        last = curr

def validBounds(points):
    #given a list of points/coords, ensure a proper boundary can be made
    if not points:
        return False
    for p1, p2 in offset(points):
        if p1 and p2:
            if p1[0] != p2[0] and p1[1] != p2[1]:
                return False
    if points[0][0] != points[-1][0] and points[0][1] != points[-1][1]:
        return False
    if area(points) != 0:
        return True

P1 = Player()
E1 = Sparx()
Qix = Qix()
Timer = Timer()
big = pygame.sprite.Group()
big.add(Qix)
enemies = pygame.sprite.Group()
enemies.add(E1)
sprites = pygame.sprite.Group()
#sprites.add(B)
#sprites.add(P1)
#sprites.add(E1)
font = pygame.font.SysFont("Times New Roman",16)
bg = (105, 66, 245)

while True:
    #P1.moveTest() #Movement w/ no bounds (TESTING USE ONLY)
    display.fill(bg)
    if MAINBORDER != Coords:
        pygame.draw.polygon(display, (73, 126, 201), MAINBORDER)
        if len(Coords) > 2:
            pygame.draw.polygon(display, (BLACK), Coords)
    else:
        pygame.draw.polygon(display, (BLACK), MAINBORDER)
    E1.move()
    Qix.update()
    P1.theory(Qix, display)
    drawBound(inside, display)
    drawBorder(MAINBORDER, display)
    P1.draw(display)
    E1.draw(display)
    Qix.draw(display)
    percent = font.render(("Claimed:" + str(claimed / totalA * 100) + "%"), True, RED)
    percentRect = percent.get_rect()
    percentRect.topleft = (0, 0)
    win = font.render(("Win: " + str(claimed / totalA * 100)), True, BLUE, BLACK)
    winRect = win.get_rect()
    winRect.center = (250, 250)
    lose = font.render('You lost!', True, RED, BLACK)
    loseRect = lose.get_rect()
    loseRect.center = (250, 250)
    lives = font.render(("Lives: "+str(PLAYER_LIVES)), True, RED)
    livesRect = lives.get_rect()
    livesRect.topright = (500, 0)
    display.blit(percent, percentRect)
    display.blit(lives,livesRect)
    pygame.display.flip()
    FPS.tick(60)
    """if claimed/totalA*100 >= 60:
        #Win the level, do whatever.
        display.blit(win, winRect)
        pygame.display.update()
        time.sleep(3)
        pygame.quit() #TEMP! Should implement more levels
        sys.exit()"""

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
        # TODO:Make player flash to signify dmg,
        #  adjust timer to make larger i-frame period
    if pygame.sprite.spritecollide(P1, big, False):
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
                if state == 1:
                    state = 0
                    P1.rect.center = points[0]
                    points = []
                    startDir = None
                    currDir = None
                    follow = []
                    followSlow = []