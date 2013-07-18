#!/usr/bin/python

import yaml
import pygame
import re, glob, pygame, math, sys, time
from pygame.locals import *
import liblo, sys, time
import subprocess

heard = []
said = []
triggers = []

pitch_ratio = 400.0
flux_min = 76.0
flux_ratio = 124.0
centroid_min = 1300.0
centroid_ratio = 6189.0
#flux_min = 160.0
#flux_ratio = 220.0
#centroid_min = 1300
#centroid_ratio = 6189.0

try:
    osc = liblo.Server(6040)
except liblo.ServerError, err:
    print str(err)
    sys.exit()

def osc_hear(path, args):
    heard.append((time.time(), args))

osc.add_method("/hear", 'fff', osc_hear)

def osc_say(path, args):
    (sec, usec, pitch, flux, centroid) = args
    when = sec + (usec / 1000000.0)
    print("when: " + str(when - time.time() ))
    said.append((when, (pitch, flux, centroid)))

osc.add_method("/say", 'iifff', osc_say)

def osc_trigger(path, args):
    (sec, usec, what) = args
    when = sec + (usec / 1000000.0)
    triggers.append((when, what))

osc.add_method("/trigger", 'iii', osc_trigger)

pygame.init()

height = 800
width = 800
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("draw kriol")

clock = pygame.time.Clock()

try:
    dirtpid = int(subprocess.Popen("pidof dirt", shell=True, stdout=subprocess.PIPE).stdout.read())
    print("Dirtpid %d" % dirtpid)
except e:
    print "dirt isn't running"

n = 0.0;

positions = []

done = False

saved = None
try:
    stream = open('drawings.yaml', 'r') 
    saved = yaml.load(stream)
except yaml.YAMLError, exc:
    print "couldn't open drawings.yaml"
    saved = []
    for i in range(0, 10):
        saved.append(None)

drawing = None
drawing_points = []

bigfont = pygame.font.Font(None, 300)
smallfont = pygame.font.Font(None, 30)

target = None

try:
    target = liblo.Address(6010)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

numbers = []
for i in range (0, 10):
    numbers.append(smallfont.render(str(i), 1, (200,200,200)))

def playback(i):
    global target

    print("playback %d" % i)
    points = saved[i]
    if points == None or len(points) == 0:
        return

    start = points[0][0]
    now = time.time()

    print(str(points))
    for (t, (x,y)) in points:
        centroid = centroid_min + ((float(x)/float(width)) * centroid_ratio)
        pitch = (float(y)/float(height)) * pitch_ratio
        flux = flux_min + ((float(y)/float(height)) * flux_ratio)
        offset = (float(t - start) / 1000.0)
        when = now + offset
        when_sec = int(when)
        when_usec = int((when - when_sec) * 1000000.0)
        #iiiifff
        #sec, usec, , v_pitch, v_flux, v_centroid1 = args
        liblo.send(target, "/play",
                   int(dirtpid),
                   int(when_sec),
                   int(when_usec),
                   int(0), # lowchunk
                   float(pitch), #pitch
                   float(flux), # flux
                   float(centroid) # centroid
                  )

def addPoints(point1, point2):
    return ((int(point1[0] + point2[0]), int(point1[1] + point2[1])))

def scalePoint(point, amount):
    return ((int(point[0] * amount), int(point[1] * amount)))
    

def draw_saved():
    global saved, smallfont
    scaleBy = 0.1

    for (i, save) in enumerate(saved):
        if save != None:
            prev = None
            for point in save:
                if i == 0:
                    pos = 9
                else:
                    pos = i-1
                xoff = scaleBy * width * pos
                scaled = addPoints(scalePoint(point[1], 0.1), (xoff,int(height * (1 - scaleBy))))
                #pygame.draw.circle(screen, (0,0,0), scaled, int(10 * scaleBy))
                if prev != None:
                    pygame.draw.aaline(screen, (0,0,0), prev, scaled)
                prev = scaled

                text = numbers[i]
                textpos = text.get_rect()
                textpos.centerx = xoff + (width * scaleBy / 2)
                textpos.centery = height * (1 - (scaleBy / 2))
                screen.blit(text, textpos)            


def save_shape():
    global drawing, drawing_points
    if drawing != None:
        saved[int(drawing)] = drawing_points
        drawing = None
        drawing_points = []
        stream = open('drawings.yaml', 'w')
        yaml.dump(saved, stream)
        stream.close()

while not done:
    clock.tick(40)
    #print("fr: " + str(clock.get_fps()))
    for event in pygame.event.get():
        alt = pygame.key.get_mods() & KMOD_ALT
        if event.type == pygame.QUIT:
            done=True
        if (event.type == KEYDOWN):
            print "pressed something"
            if (event.unicode >= '0' and event.unicode <= '9'):
                if alt:
                    drawing = event.unicode
                    drawing_points = []
                else:
                    playback(int(event.unicode))
            elif event.key == K_ESCAPE:
                print "escape"
                drawing = None
                drawing_points = []
            elif event.key == K_RETURN:
                print "enter"
                save_shape()

    screen.fill((255,255,255))
    
    if drawing == None:
        if not pygame.mouse.get_pressed()[0]:
            drawing = None
    else:
	text = bigfont.render(drawing, 1, (200,200,200))
	textpos = text.get_rect()
	textpos.centerx = screen.get_rect().centerx
	textpos.centery = screen.get_rect().centery
	screen.blit(text, textpos)

        if pygame.mouse.get_pressed()[0]:
            drawing_points.append((pygame.time.get_ticks(), pygame.mouse.get_pos()))
    
    prev = None
    for point in drawing_points:
#        pygame.draw.circle(screen, (0,0,0), point[1], 10)
        if prev != None:
            pygame.draw.line(screen, (0,0,0), prev, point[1], 4)
        prev = point[1]

    for (t, (pitch, flux, centroid)) in heard:
        pygame.draw.circle(screen, (255,0,0), 
                           (int(((centroid - centroid_min) / centroid_ratio)*width),
                            int((pitch / pitch_ratio) * height)
                            #int(((flux - flux_min) / flux_ratio)*height)
                           ),
                           3
                          )
    now = time.time()
    for (i, (t, what)) in reversed(list(enumerate(triggers))):
        if t <= now:
            print("playback at " + str(now - t))
            playback(what)
            triggers.pop(i)
        
    draw_saved()        

    pygame.display.flip()
    osc.recv(0)
