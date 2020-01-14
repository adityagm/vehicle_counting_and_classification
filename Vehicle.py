# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:59:59 2017

@author: philanderz
"""

from random import randint
import time
from estimate_speed import estimateSpeed


class MyVehicle:
    tracks = []

    def __init__(self, i, xi, yi, max_age):
        self.i = i
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0,255)
        self.G = randint(0,255)
        self.B = randint(0,255)
        self.record = []
        self.done = False
        self.state = 0
        self.age = 0
        self.max_age = max_age
        self.dir = None
        self.direction = 0

    def getRGB(self):
        return self.R, self.G, self.B

    def getTracks(self):
        return self.tracks

    def getId(self):
        return self.i

    def getState(self):
        return self.state

    def getDir(self):
        return self.dir

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def updateCoords(self, xn, yn):
        self.tracks.append([self.x, self.y])
        self.x = xn
        self.y = yn

    def setDone(self):
        self.done = True

    def timedOut(self):
        return self.done
    
    def record_crossed(self, direction, rx, ry):
        self.record.append([direction,rx,ry])
        
    def crossed(self,mid_start, mid_end):
        if len(self.tracks) >= 2:
            if self.y < mid_end <= self.tracks[-2][1]: #cruzo la linea
                self.direction = -1
                return -1
            if self.y > mid_start >= self.tracks[-2][1]:
                self.direction = 1
                return 1
            
    def avgSpeed(self):
        if len(self.record) >= 2:
            if self.direction == -1:
                speed = estimateSpeed(self.record[-2][1:], self.record[-1][1:])
                return speed
            if self.direction == 1:
                speed = estimateSpeed(self.record[-1][1:], self.record[-2][1:])
                return speed
            
    def going_UP(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == 0:
                if self.tracks[-1][1] < mid_end and self.tracks[-2][1] >= mid_end: #cruzo la linea
                    self.state = 1
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False
        
    def going_DOWN(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == 0:
                if self.tracks[-1][1] > mid_start and self.tracks[-2][1] <= mid_start: #cruzo la linea
                    self.state = 1
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False
        
    def speed_down(self):
        if len(self.tracks) >= 2:
            speed = estimateSpeed(self.tracks[-1], self.tracks[-2])
            return speed
            
    def speed_up(self):
        if len(self.tracks) >= 2:
            speed = estimateSpeed(self.tracks[-2], self.tracks[-1])
            return speed
            
    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True
