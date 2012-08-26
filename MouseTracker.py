# Mouse Tracking Square Demonstrating GameEngine2D
import numpy as np
import pygame
 
from GameEngine2D import NewtonWorld
from PhysicsEngine2D import NewtonianEntity
 
kp = 20
kv = 150
 
class MouseTracker(NewtonianEntity):
    def init(self):
        self.kp = kp
        self.kv = kv
       
    def set_k(self,kp,kv):
        self.kp = kp
        self.kv = kv
       
    def process(self,dt):
 
        # These values are in pixels or pixels/second
        positionDesired = pygame.mouse.get_pos()
        velocityDesired = np.array((0,0),float)
       
        # self.position and self.velocity are also stored in pixel units
        x = positionDesired - self.position
        dx = velocityDesired - self.velocity
       
        forceCommanded = (self.kp*x + self.kv*dx) / self.scale
        self.set_force(forceCommanded)
       
        NewtonianEntity.process(self,dt)
       
class MouseTracker1DOF(MouseTracker):
    def init(self):
        # Zero corresponds to x-axis
        self.degreeOfFreedom = 0
        self.kp = kp
        self.kv = kv
       
    def set_dof(self,dof):
        self.degreeOfFreedom = 0 if dof == 'x' else 1
       
    def process(self,dt):
        # These values are in pixels or pixels/second
        positionDesired = pygame.mouse.get_pos()[self.degreeOfFreedom]
        velocityDesired = 0
       
        # self.position and self.velocity are also stored in pixel units
        x = positionDesired - self.position[self.degreeOfFreedom]
        dx = velocityDesired - self.velocity[self.degreeOfFreedom]
       
        forceCommanded = np.array((0,0),float)
        forceCommanded[self.degreeOfFreedom] = (self.kp*x + self.kv*dx) / self.scale
       
        self.set_force(forceCommanded)
       
        NewtonianEntity.process(self,dt)       
       
       
def main():
    SCALE = 10 # pixels per meter
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    screenWidth,screenHeight = screen.get_size()
    worldSize = np.array(screen.get_size())/SCALE
    pygame.display.set_caption("Newton World")
    screen.fill((255,255,255))
    pygame.display.flip()
    
    world = NewtonWorld("NewtonWorld",screen,framesPerSecond=40,scale=SCALE)
    
    #square = MouseTracker(world,position=worldSize/2,mass=1)
    #world.add(square)
    
    paddleImage = pygame.Surface((30,120))
    paddleImage.fill(pygame.Color('red'))
    paddle1 = MouseTracker1DOF(world,position=worldSize/2-(38,0),mass=1,image=paddleImage)
    paddle1.set_dof('y')
    world.add(paddle1)
    #paddle2 = MouseTracker1DOF(world,position=worldSize/2+(38,0),mass=1,image=paddleImage)
    #paddle2.set_dof('x')
    #paddle2.set_k(10,100)
    #world.add(paddle2)
   
   
    world.unpause()
    world.run_main_loop()
    pygame.quit()
       
if __name__ == "__main__":
    main()
