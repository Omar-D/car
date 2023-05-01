"""
CarSimPy

This a physics based car simulation ran on Python.
Attempts to model the physics of a car based on several factors.
The simulation runs on PyGame. (Current version 2.0.0dev6)

Written by David Joohoon Kim
joohoon.kim@outlook.com

TODO
- Add collision with map environment
- Choose a scaling method for screen and environment
"""
import os
from math import sin, cos, tan, radians, degrees, copysign, pi
from random import randint
import pygame
from pygame.math import Vector2
from pygame.locals import *

# local import
from constants import *
import car_model
import map_model
import obstacle_model

# Get image of car
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(current_dir, "assets/")
car_image = pygame.image.load(assets_path+"car.png")
background_image = pygame.image.load(assets_path+"background.png")
rock_image = pygame.image.load(assets_path+"rock.png")
sensor_image = pygame.image.load(assets_path+"sensor_beam.png")

# Sound Effects TODO::Get better sound effects
pygame.mixer.init()
car_crash_sound = pygame.mixer.Sound(assets_path+"sounds/crash.wav")
car_driving_sound = pygame.mixer.Sound(assets_path+"sounds/car_driving_3.wav")
car_snow_sound = pygame.mixer.Sound(assets_path+"sounds/car_snow.wav")
car_skid_sound = pygame.mixer.Sound(assets_path+"sounds/tire_skid.wav")

class Game:
    def __init__(self):
        """ initialize screen """
        pygame.init()
        pygame.display.set_caption("Drive-Simulation")

        # Starting Position
        car_pos_x = (SCREEN_WIDTH/2)-100
        car_pos_y = (SCREEN_HEIGHT/2)-100
        map_pos_x = car_pos_x
        map_pos_y = car_pos_y

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.ticks = GAME_TICKS
        self.exit = False
        self.terrain = 0    #0=road, 1=grass

        self.car = car_model.Car(car_pos_x, car_pos_y)
        self.map = map_model.Map(map_pos_x,map_pos_y)
        self.obstacles = []
        for i in range(NUM_OBSTACLES):
            x_pos = randint(100,800)
            y_pos = randint(100,800)
            rock = obstacle_model.Obstacle(map_pos_x+x_pos,map_pos_y+y_pos)
            self.obstacles.append(rock)

    def CheckBoundary(self,car_info,env,obstacles):
        # Get middle of the screen
        x = SCREEN_WIDTH//2
        y = SCREEN_HEIGHT//2

        # Check boundaries for object(s)
        pos_valid = [True,True]
        for ob in obstacles:
            pos_valid = ob.CheckBoundary(pos_valid,x,y,car_info)
        pos_valid = env.CheckBoundary(pos_valid,x,y,car_info)

        return pos_valid

    def CheckTerrain(self,car,env):
        # Get middle of the screen
        x = SCREEN_WIDTH//2
        y = SCREEN_HEIGHT//2

        self.terrain = env.CheckTerrain(x,y,car.getPosition())
        return self.terrain

    """ defines the controls of the car """
    """ TODO::Refine Controls for 2 wheel steering """
    """ TODO::Use something else for detecting keys, replace if else"""
    def controls(self, car, dt, pressed):
        if pressed[pygame.K_LEFT]:
            car.setSteerAngle(-10)
        elif pressed[pygame.K_RIGHT]:
            car.setSteerAngle(10)
        else:
            car.setSteerAngle(0)
        if pressed[pygame.K_UP]:
            car.setEngineForce(500000)
            car.setGear(1)
        elif pressed[pygame.K_DOWN]:
            car.setEngineForce(-200000)
            car.setGear(2)
        elif pressed[pygame.K_b]:
            car.setBraking(1)
        else:
            car.setEngineForce(0)
            car.setBraking(0)

    """ draws the screen and objects """
    def draw(self, car, env, obstacles):
        # Draw background
        map_width=(int)(env.getDim().x)
        map_height=(int)(env.getDim().y)
        background_scaled = pygame.transform.scale(background_image,(map_width,map_height))
        self.screen.blit(background_scaled, env.getPos())

        # Draw car
        car_scaled = pygame.transform.scale(car_image,(int(car.getLength()),int(car.getWidth()) ))
        car_rotated = pygame.transform.rotate(car_scaled, car.getOrientation())
        self.screen.blit(car_rotated, (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))

        # Draw obstacle(s)
        for ob in obstacles:
            rock_scaled = pygame.transform.scale(rock_image,(int(ob.getDim().x),int(ob.getDim().y)))
            self.screen.blit(rock_scaled, ob.getPosition())

        # Draw sensor(s)
        fs_obj = car.front_sensor
        fs_scaled = pygame.transform.scale(sensor_image,(int(fs_obj.get_length()),int(fs_obj.get_width())))
        fs_rotated = pygame.transform.rotate(fs_scaled, car.getOrientation())
        front_sensor_position = Vector2( (SCREEN_WIDTH//2)+car.getLength(), (SCREEN_HEIGHT//2)+(car.getWidth()//2) )
        self.screen.blit(fs_rotated, front_sensor_position)

        pygame.display.flip()

    """ processes the simulation """
    def run(self):
        while not self.exit:
            #Local save of parameters
            prev_terrain = self.terrain

            # Convert time from milliseconds to seconds
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                elif event.type == VIDEORESIZE:
                    screen = pygame.display.set_mode(event.dict['size'], HWSURFACE|DOUBLEBUF|RESIZABLE)

            # User input
            pressed = pygame.key.get_pressed()
            self.controls(self.car, dt, pressed)

            # Sensors
            self.car.front_sensor.update(self.car.getPosition(),self.car.getOrientation())
            detected = self.car.front_sensor.check_sensor(self.map,100,1)
            print(detected)

            # Logic
            self.terrain = self.CheckTerrain(self.car,self.map)
            self.car.setTerrain(self.terrain)
            car_info = self.car.calculate(dt)
            pos_valid = self.CheckBoundary(car_info,self.map,self.obstacles)
            self.car.update(dt,car_info,pos_valid)
            self.map.update(dt,self.car.getPosition())
            for ob in self.obstacles:
                ob.update(self.map.getPos())

            # Drawing
            self.screen.fill((0,0,0))
            self.draw(self.car,self.map,self.obstacles)

            # Sound Effects
            if(SOUND_ON):
                if(not(pos_valid[0]) or not(pos_valid[1])): #Car crashed
                    car_crash_sound.play()
                drive_sound = False
                if((abs(car_info["vel"].x) > 50 or abs(car_info["vel"].y) > 50)): #Car speed > 50
                    drive_sound = True
                if(not(pygame.mixer.Channel(0).get_busy())):    #Prevent sound overlap
                    if(drive_sound):
                        if(prev_terrain is not self.terrain):
                            car_snow_sound.stop()
                            car_driving_sound.stop()
                        if(self.terrain == 0):
                            car_driving_sound.play()
                        if(self.terrain == 1):
                            car_snow_sound.play()
                    else:
                        car_snow_sound.stop()
                        car_driving_sound.stop()
                else:
                    if(not(drive_sound)):
                        car_snow_sound.stop()
                        car_driving_sound.stop()
                if(abs(self.car.getAngVel()) > 3.0):
                    car_skid_sound.play()
                else:
                    car_skid_sound.stop()

            # Update the clock (Called once per frame)
            self.clock.tick(self.ticks)
        """ End of while not self.exit """

        pygame.quit()



if __name__ == '__main__':
    game = Game()
    game.run()
