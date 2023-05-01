"""
car_model.py

The Car Class represents the physical nature of the car.
Physics model is based on equations from the following link:
https://asawicki.info/Mirror/Car%20Physics%20for%20Games/Car%20Physics%20for%20Games.html

Written by David Joohoon Kim
joohoon.kim@outlook.com
"""
import pygame
from pygame.math import Vector2
from math import sin, cos, tan, radians, degrees, copysign, pi, sqrt
from random import randint

from constants import *
import sensor

class Car:
    def __init__(self,x,y,orient=180,max_steer=0,max_speed=5,max_accel=5.0):
        self.pos = Vector2(x,y)
        self.vel = Vector2(0.0,0.0)
        self.accel = Vector2(0.0,0.0)
        self.engine_force = 0.0
        self.steer_angle = 0.0
        self.orient = orient
        self.brake_b = 0
        self.gear = 1               #0:park, 1:drive, 2:reverse
        self.prev_pos = Vector2(0,0)
        self.pos_buf = Vector2(0,0)
        self.terrain = 0
        self.drag = C_DRAG_ROAD
        self.RR = 30*self.drag
        self.ang_vel = 0

        # Sensors
        self.front_sensor = sensor.Sensor(x,y)

        # Threshold Constants
        self.max_steer = max_steer
        self.max_speed = max_speed
    ''' Calculate vehicle position '''
    def calculate(self, dt):
        pos_local  = Vector2(0.0,0.0)
        vel_local = Vector2(0.0,0.0)
        speed=sqrt(self.vel.x*self.vel.x + self.vel.y*self.vel.y)

        if(self.terrain == 1):
            self.steer_angle += randint(-2,2)

        self.ang_vel = 0

        if(self.steer_angle):
            circ_radius = VEHICLE_LENGTH / (sin(self.steer_angle))
            ang_vel = speed / circ_radius
            self.ang_vel = ang_vel
            # print("angular velocity = ", ang_vel)
            self.orient = (self.orient + ang_vel)%360

        heading = Vector2(cos(self.orient*pi/180.0),sin(-self.orient*pi/180.0))

        F_tract = self.engine_force*heading

        if( ((self.vel.x>=0 and heading.x>=0)or(self.vel.x<=0 and heading.x<=0)) and\
            ((self.vel.y>=0 and heading.y>=0)or(self.vel.y<=0 and heading.y<=0)) and\
             self.brake_b and (self.gear == 1) ):
            F_tract = -heading*C_BRAKE
        if( ((self.vel.x<=0 and heading.x>=0)or(self.vel.x>=0 and heading.x<=0)) and\
            ((self.vel.y<=0 and heading.y>=0)or(self.vel.y>=0 and heading.y<=0)) and\
             self.brake_b and (self.gear == 2) ):
            F_tract = heading*C_BRAKE
        # print("C_DRAG = ",self.drag)
        F_drag = -self.drag*self.vel
        self.RR = 30*self.drag
        F_rr = -self.RR*self.vel                   #Rolling Resistance C_rr ~= 30*C_drag
        F_long = F_tract + F_drag + F_rr

        accel = F_long / MASS
        vel_local.x = self.vel.x + (accel.x*dt)
        vel_local.y = self.vel.y + (accel.y*dt)
        pos_local.x = self.pos.x + (vel_local.x*dt)
        pos_local.y = self.pos.y + (vel_local.y*dt)
        length = self.getLength()
        width = self.getWidth()

        info = { "pos": pos_local, "vel": vel_local,
                 "length": length, "width": width }
#        print("car_model.info: ", info)

        return info


    ''' Update the vehicle information '''
    def update(self, dt, car_info, pos_valid):
        if(pos_valid[0]):
            self.pos.x = car_info["pos"].x
            self.vel.x = car_info["vel"].x
        else:
            self.vel.x = 0
        if(pos_valid[1]):
            self.pos.y = car_info["pos"].y
            self.vel.y = car_info["vel"].y
        else:
            self.vel.y = 0

        # print("Car position=",self.pos)
        # print("Car velocity=",self.vel)


    def setGear(self,gear):
        self.gear=gear

    def setEngineForce(self,f):
        self.engine_force = f

    def setSteerAngle(self,a):
        self.steer_angle = a

    def setBraking(self,b):
        self.brake_b = b

    def getLength(self):
        return VEHICLE_LENGTH

    def getWidth(self):
        return VEHICLE_WIDTH

    def getPosition(self):
        return self.pos

    def getVel(self):
        return self.vel

    def getPrevPos(self):
        return self.prev_pos

    def getAccel(self):
        return self.accel

    def getOrientation(self):
        return self.orient

    def getAngVel(self):
        return self.ang_vel

    def setTerrain(self,terrain):
        self.terrain = terrain
        if(terrain == 0):
            self.drag = C_DRAG_ROAD
        if(terrain == 1):
            self.drag = C_DRAG_GRASS
        # print("terrain = ",terrain," and C_DRAG=",self.drag)
