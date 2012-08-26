# Mouse Tracking Square Demonstrating GameEngine2D
import numpy as np
import numpy.linalg as LA
import pygame
from pygame.locals import *
import math
import random
 
from PhysicsEngine2D import PhysicsWorld, CollidingEntity
from GameEngine2D import GraphicEntity
 
kp = 2000
kv = 500
BALL_SPEED = 40. # meters per second
DIFFICULTY = "hard" #"medium" #"hard"

class Score(GraphicEntity):
	def __init__(self,world,side):
		if side == "left": position = (world.size[0]/4,50)
		elif side == "right": position = (3*world.size[0]/4,50)
		else: raise ValueError("Score side must be left or right")
		self.value = 0
		self.font = pygame.font.Font(None,30)
		
		GraphicEntity.__init__(self,world,position,image=self.font.render(str(self.value),True,pygame.Color("black")))
		self.type="Score"
		self.side=side
		
	def update_score(self,newScore):
		self.value = newScore
		self.image = self.font.render(str(self.value),True,pygame.Color("black"))
		self.size = np.array(self.image.get_size())
		self.rect = pygame.Rect(self.position - self.size/2,self.size)
		
	def increment(self):
		self.update_score(self.value+1)
		
		

class Ball(CollidingEntity):
	def init(self):
		self.type = "Ball"
		angle = 0.3*math.pi*random.random()+random.choice([0,math.pi])
		self.set_velocity(BALL_SPEED*np.array((math.cos(angle),math.sin(angle)))) 
		self.collisionPoints = [
								(np.array([0,15]),np.array([-1,0])),
								(np.array([30,15]),np.array([1,0])),
								(np.array([30,0]),np.array([0,-1])),
								(np.array([15,30]),np.array([0,1]))
							   ]
							   
	def process(self,dt):
		if self.position[0] < -15:
			self.set_position(self.world.size/2,units="PIX")
			angle = 0.3*math.pi*random.random()+random.choice([0,math.pi])
			self.set_velocity(BALL_SPEED*np.array((math.cos(angle),math.sin(angle))))
			for score in self.world.get_group("Score"):
				if score.side == "right":
					score.increment()
		if self.position[0] > self.world.size[0]-15:
			self.set_position(self.world.size/2,units="PIX")
			angle = 0.3*math.pi*random.random()+random.choice([0,math.pi])
			self.set_velocity(30*np.array((math.cos(angle),math.sin(angle))))
			for score in self.world.get_group("Score"):
				if score.side == "left":
					score.increment()
		if self.position[1] < 15:
			self.set_velocity((self.velocity[0],abs(self.velocity[1])),units="PIX")
		if self.position[1] > self.world.size[1]-15:
			self.set_velocity((self.velocity[0],-abs(self.velocity[1])),units="PIX")
		if self.velocity[0] == 0:
			self.velocity[0] = random.choice([.01,-.01])
		CollidingEntity.process(self,dt)

     
class Paddle(CollidingEntity):
    def init(self):
        # Zero corresponds to x-axis
        self.degreeOfFreedom = 0
        self.kp = kp
        self.kv = kv
        self.type = "Paddle"
       
    def set_dof(self,dof,fixedCoordinate):
        self.degreeOfFreedom = 0 if dof == 'x' else 1
        self.fixedCoordinate = fixedCoordinate
       
    def process(self,dt):
        # These values are in pixels or pixels/second
        positionDesired = np.array((0.,0.))
        positionDesired[self.degreeOfFreedom] = pygame.mouse.get_pos()[self.degreeOfFreedom]
        positionDesired[1-self.degreeOfFreedom] = self.fixedCoordinate
        velocityDesired = np.array((0.,0.))
       
        # self.position and self.velocity are also stored in pixel units
        x = positionDesired - self.position
        dx = velocityDesired - self.velocity
       
        forceCommanded = (self.kp*x + self.kv*dx) / self.scale
       
        self.set_force(forceCommanded)
       
        #print "velocity:", self.velocity
        if pygame.key.get_pressed()[K_SPACE]:
            self.add_force((-7000.,0.))
       
        CollidingEntity.process(self,dt)
        
    def collides_with(self,point):
		return self.rect.collidepoint(point)
		
class ComputerPaddle(Paddle):
	def process(self,dt):
		self.ball = self.world.get_group("Ball")[0]
		# These values are in pixels or pixels/second
		positionDesired = np.array((0.,0.))
		if DIFFICULTY in ("easy","medium"):
			positionDesired[self.degreeOfFreedom] = self.ball.position[self.degreeOfFreedom]
		elif DIFFICULTY == "hard":
			expectedYPos = (self.fixedCoordinate - self.ball.position[0])/self.ball.velocity[0]*self.ball.velocity[1]+self.ball.position[1]
			if expectedYPos < 0:
				expectedYPos = -expectedYPos
			elif expectedYPos > self.world.size[1]:
				expectedYPos = self.world.size[1] - (expectedYPos-self.world.size[1])
		positionDesired[self.degreeOfFreedom] = expectedYPos
		positionDesired[1-self.degreeOfFreedom] = self.fixedCoordinate
		velocityDesired = np.array((0.,0.))

		# self.position and self.velocity are also stored in pixel units
		x = positionDesired - self.position
		dx = velocityDesired - self.velocity

		forceCommanded = (self.kp*x + self.kv*dx) / self.scale

		self.set_force(forceCommanded)
		
		if DIFFICULTY in ("medium", "hard"):
			if self.ball.position[0] > self.fixedCoordinate - 300 and self.ball.position[0] < self.fixedCoordinate-150:
				self.add_force((7000.,0.))	

		CollidingEntity.process(self,dt)
		   
       
def main():
    SCALE = 10 # pixels per meter
    pygame.init()
    screen = pygame.display.set_mode((1000,700))
    screenWidth,screenHeight = screen.get_size()
    worldSize = np.array(screen.get_size())/SCALE
    pygame.display.set_caption("Newton World")
    screen.fill((255,255,255))
    pygame.display.flip()
   
    world = PhysicsWorld("Pong",screen,framesPerSecond=100,scale=SCALE)
   
    #square = MouseTracker(world,position=worldSize/2,mass=1)
    #world.add(square)
   
    paddleImage = pygame.Surface((20,120))
    paddleImage.fill(pygame.Color('red'))
    paddle1 = Paddle(world,position=(10,worldSize[1]/2),mass=1.,image=paddleImage)
    paddle1.set_dof('y',paddle1.position[0])
    world.add(paddle1)
    
    paddle2 = ComputerPaddle(world,position=(worldSize[0]-10,worldSize[1]/2),mass=1.,image=paddleImage)
    paddle2.set_dof('y',paddle2.position[0])
    world.add(paddle2)
    
    ballImage = pygame.Surface((31,31))
    pygame.draw.circle(ballImage,pygame.Color('blue'),(15,15),15)
    pygame.draw.circle(ballImage,pygame.Color('black'),(15,15),15,1)
    ballImage.set_colorkey(ballImage.get_at((0,0)))
    ball = Ball(world,position=worldSize/2,mass=.05,image=ballImage)
    world.add(ball)
    
    score1 = Score(world,"left")
    world.add(score1)
    score2 = Score(world,"right")
    world.add(score2)
   
    pygame.mouse.set_pos(paddle1.get_position(units="PIX"))
    world.unpause()
    world.run_main_loop()
    pygame.quit()
       
if __name__ == "__main__":
    main()
