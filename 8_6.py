#encoding: utf-8
from __future__ import division
from nodebox.graphics import *
import pymunk
import pymunk.pyglet_util
import random, math
import numpy as np

space = pymunk.Space()

def createBody(x,y,shape,*shapeArgs):
    body = pymunk.Body()
    body.position = x, y
    s = shape(body, *shapeArgs)
    s.mass = 1
    s.friction = 1
    space.add(body, s)
    return s #shape!!!

s0=createBody(300, 300, pymunk.Poly, ((-20,-5),(-20,5),(20,15),(20,-15)))
s0.score=0
s3=createBody(200, 300, pymunk.Poly, ((-20,-5),(-20,5),(20,15),(20,-15)))
s3.color = (0, 255, 0, 255)
s3.score=0
s3.body.Q=[[0, 0], [0, 0], [0, 0]]
#s3.body.Q=[[0, 0], [1, -1], [-1, 1]]
#Q=[нічого[залишати, змінювати], об'єкт[залишати, змінювати], антиоб'єкт[залишати, змінювати]]
s3.body.action=0 # 0 - залишати, 1 - змінювати (випадковий кут)
s1=createBody(300, 200, pymunk.Circle, 10, (0,0))
S2=[]
for i in range(1):
    s2=createBody(350, 250, pymunk.Circle, 10, (0,0))
    s2.color = (255, 0, 0, 255)
    S2.append(s2)


def getAngle(x,y,x1,y1):
    return math.atan2(y1-y, x1-x)

def getDist(x,y,x1,y1):
    return ((x-x1)**2+(y-y1)**2)**0.5

def inCircle(x,y,cx,cy,R):
    if (x-cx)**2+(y-cy)**2 < R**2:
        return True
    return False

def inSector(x,y,cx,cy,R,a):
    angle=getAngle(cx,cy,x,y)
    a=a%(2*math.pi)
    angle=angle%(2*math.pi)
    if inCircle(x,y,cx,cy,R) and a-0.5<angle<a+0.5:
        return True
    return False

def strategy(b=s3.body):
    v=100
    a=b.angle
    b.velocity=v*cos(a), v*sin(a)
    x,y=b.position
    R=getDist(x,y,350,250)
    #print R, b.angle
    line(x,y,*s1.body.position,stroke=Color(0))
    if canvas.frame%100==0:
        if R>180:
            b.angle=getAngle(x,y,350,250)
        else:
            b.angle=getAngle(x,y,*s1.body.position) #2*math.pi*random.random()

def dynamicState(b=s3.body):
    # Розрахунок відстаней і кутів до цільових точок
    pos_x, pos_y = b.position
    distance_to_s1 = getDist(pos_x, pos_y, s1.body.position[0], s1.body.position[1])
    distance_to_s2 = getDist(pos_x, pos_y, S2[0].body.position[0], S2[0].body.position[1])
    angle_to_s1 = getAngle(pos_x, pos_y, s1.body.position[0], s1.body.position[1])
    angle_to_s2 = getAngle(pos_x, pos_y, S2[0].body.position[0], S2[0].body.position[1])
    return (distance_to_s1, distance_to_s2, angle_to_s1, angle_to_s2, b.angle)

def strategy2(b=s3.body):
    velocity = 100
    current_angle = b.angle
    b.velocity = velocity * cos(current_angle), velocity * sin(current_angle)
    position_x, position_y = b.position
    boundary_distance = getDist(position_x, position_y, 350, 250)
    
    ellipse(position_x, position_y, 200, 200, stroke=Color(0.5))

    if canvas.frame % 10 == 0:  # виконуємо кожні 10 кадрів
        is_in_s1_sector = inSector(s1.body.position[0], s1.body.position[1], position_x, position_y, 100, current_angle)
        is_in_s2_sector = inSector(S2[0].body.position[0], S2[0].body.position[1], position_x, position_y, 100, current_angle)

        # Встановлення стану робота на основі поточних даних
        current_state = dynamicState(b)
        reward_value = 0

        if is_in_s1_sector:
            reward_value = 1 if b.action == 0 else -1
        elif is_in_s2_sector:
            reward_value = -1 if b.action == 0 else 1

        learning_rate = 0.1  # швидкість навчання для алгоритму
        b.Q[current_state][b.action] += learning_rate * (reward_value + np.max(b.Q[current_state]) - b.Q[current_state][b.action])
        print(current_state, b.action, b.Q)

        # Вибір дії: випадкова дія або найкраща відповідно до Q-таблиці
        exploration_chance = 0.1  # ймовірність випадкової дії
        if random.random() < exploration_chance:
            b.action = random.choice([0, 1])
        else:
            b.action = np.argmax(b.Q[current_state])

        if b.action:  # При необхідності змінюємо напрямок
            b.angle += random.uniform(-math.pi/4, math.pi/4)  # Зміна на випадковий кут

        if boundary_distance > 180:  # Перевірка межі кола
            b.angle = getAngle(position_x, position_y, 350, 250)


def scr(s,s0,s3,p=1):
    bx,by=s.body.position
    s0x,s0y=s0.body.position
    s3x,s3y=s3.body.position
    if not inCircle(bx,by,350,250,180):
        if getDist(bx,by,s0x,s0y)<getDist(bx,by,s3x,s3y):
            s0.score=s0.score+p
        else:
            s3.score=s3.score+p
        s.body.position=random.randint(200,400),random.randint(200,300)

def score():
    u"""визначає переможця"""
    scr(s1,s0,s3)
    for s in S2:
        scr(s,s0,s3,p=-1)


def manualControl():
    u"""Керування роботом з мишки або клавіатури"""
    v=10 # швидкість
    b=s0.body
    a=b.angle
    x,y=b.position
    vx,vy=b.velocity
    if canvas.keys.char=="a":
        b.angle-=0.1
    if canvas.keys.char=="d":
        b.angle+=0.1
    if canvas.keys.char=="w":
        b.velocity=vx+v*cos(a), vy+v*sin(a)
    if canvas.mouse.button==LEFT:
        b.angle=getAngle(x,y,*canvas.mouse.xy)
        b.velocity=vx+v*cos(a), vy+v*sin(a)

def simFriction():
    for s in [s0,s1,s3]+S2:
        s.body.velocity=s.body.velocity[0]*0.9, s.body.velocity[1]*0.9
        s.body.angular_velocity=s.body.angular_velocity*0.9
        #s.body.update_velocity(s.body, (0.,0.), 0.9, 0.02)

draw_options = pymunk.pyglet_util.DrawOptions()

def draw(canvas):
    canvas.clear()
    fill(0,0,0,1)
    text("%i %i"%(s0.score,s3.score),20,20)
    nofill()
    ellipse(350, 250, 350, 350, stroke=Color(0))
    manualControl()
    strategy2()
    score()
    simFriction()
    space.step(0.02)
    space.debug_draw(draw_options)

canvas.size = 700, 500
canvas.run(draw)
