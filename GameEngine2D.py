import pygame
from pygame.locals import *
import numpy as np
from numpy import linalg as LA


class World(object):
    def __init__(self,name,surface,background=None,framesPerSecond=40):
        self.name = name
        self.surface = surface
        self.background = background
        self.entities = {}
        self.framesPerSecond = framesPerSecond
        self.clock = pygame.time.Clock()
        self.isPaused = True
        self.size = np.array(surface.get_size())

        if not self.background:
            self.background = pygame.Surface(self.size)
            self.background.fill(pygame.Color('white'))


    def add(self,entity):
        if entity.type in self.entities:
            self.entities[entity.type].append(entity)
        else:
            self.entities[entity.type] = [entity]

    def remove(self,entity):
        try:
            self.entities[entity.type].remove(entity)
        except ValueError:
            print "Entity does not exist in the world "+self.name
            print "Not removed."

    def get_group(self,identifier):
        """
        @param identifier:  string or entity representing the type of entity
                            you want to access

        returns:    list of entities matching the identifier; empty list if
                    the identifier is invalid or doesn't match any entities
        """
        if isinstance(identifier, str):
            return self.entities.get(identifier,[])
        if isinstance(identifier,Entity):
            return self.entities.get(identifier.type,[])
        return []

    def get_entities(self):
        entitiesList = []
        for group in self.entities.values():
            for entity in group:
                entitiesList.append(entity)

        return entitiesList

    def process(self,dt):
        for group in self.entities.values():
            for entity in group:
                entity.process(dt)

    def render(self,surface):
        for group in self.entities.values():
            for entity in group:
                entity.render(surface)

    def clean(self):
        for entity in self.get_entities():
            entity.erase()

    def get_rects(self):
        rects = []
        for entity in self.get_entities():
            rects.append(entity.get_rect())

        return rects

    def run_main_loop(self):
        while True:
            self.main_loop()
           
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                   
    def main_loop(self):
        dtInMilliseconds = self.clock.tick(self.framesPerSecond)
        dt = dtInMilliseconds/1000.
        # Store previous rects...
        dirtyRects = self.get_rects()
        self.clean()
        self.process(dt)
        self.render(self.surface)
        # ...and new rects for efficient updating display
        dirtyRects.extend(self.get_rects())

        pygame.display.update(dirtyRects)

    def display_message(self,message):
        # This function will eventually show the message in the GUI
        print message
       
    def get_height(self):
        return self.surface.get_height()

    def get_width(self):
        return self.surface.get_width()

    def pause(self):
        self.isPaused = True

    def unpause(self):
        self.isPaused = False
           
class Entity(object):
    def __init__(self,world):
        self.world = world
        self.type = "Entity"
        self.rect = None

    def render(self,surface):
        pass

    def erase(self):
        pass

    def process(self,dt):
        pass

    def get_rect(self):
        return None

class GraphicEntity(Entity):
    def __init__(self,world,position,image=None):
        self.world = world
        self.position = np.array(position)
        self.image = image
        if not image:
            self.image = pygame.Surface((1,1))

        self.size = np.array(self.image.get_size())
        self.type = "GraphicEntity"
       
        self.rect = pygame.Rect(self.position - size/2,size)
   
    def render(self,surface):
        surface.blit(self.image,self.rect)
       
    def erase(self):
        self.world.surface.blit(self.world.background,self.rect,self.rect)

    def get_rect(self):
        return self.rect.copy()

    def move_to(self,position):
        self.position = np.array(position)
        self.rect.center = self.position
       
class NewtonianEntity(GraphicEntity):
    """
    Arguments:
    ----------------------------------------------------------------
    mass            | mass of the entity (kg)
    centerOfMass    | relative to topleft of image (if None, use center of image)
    inertia         | moment of inertia wrt the z axis (kg * pixels^2)
    position        | position of center of mass in world (pixel,pixel)
    velocity        | in pixels per second (p/s)
    acceleration    | in pixels per second per second (p/s^2)
    force           | in kg * p / s^2
    image           | entity's image
    ----------------------------------------------------------------
    """
    def __init__(self,world,mass=1,centerOfMass=None,inertia=1,position=(0,0),velocity=(0,0),acceleration=(0,0),force=(0,0),image=None):
        self.world = world
        self.type = "NewtonianEntity"
       
        self.image = image
        if not image:
            self.image = pygame.Surface((10,10))
            self.image.fill(pygame.Color('red'))
        self.size = np.array(self.image.get_size())
               
        self.position = np.array(position,float)
        self.velocity = np.array(velocity,float)
        self.acceleration = np.array(acceleration,float)
        self.mass = mass
        if not centerOfMass: centerOfMass = self.size/2
        self.centerOfMass = np.array(centerOfMass,float)
        self.force = np.array(force,float)
       
        self.rect = pygame.Rect(self.position-self.centerOfMass,self.size)
       
    def process(self,dt):
        # TODO: Collision detection
        # Kinematics
        self.acceleration += self.force * dt / self.mass
        self.velocity += self.acceleration * dt
        self.position += self.velocity
       
        self.rect.topleft = self.position - self.centerOfMass
       
    def set_force(self,force):
        self.force = np.array(force)
       
    def add_force(self,force):
        self.force += np.array(force)
       

class NewtonWorld(World):
    def run_main_loop(self):
        while True:
            self.main_loop()
           
            soleEntity = self.get_entities()[0]
            soleEntity.set_force((0.,0.))
            keysPressed = pygame.key.get_pressed()
            if keysPressed[K_UP]:
                soleEntity.add_force((0.,-10.))
            if keysPressed[K_DOWN]:
                soleEntity.add_force((0.,10.))
            if keysPressed[K_RIGHT]:
                soleEntity.add_force((10.,0.))
            if keysPressed[K_LEFT]:
                soleEntity.add_force((-10.,0.))
           
           
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return

    def apply_friction(self):
        for entity in self.get_entities():
			if LA.norm(entity.velocity) <= 0.001:
				staticFriction = -max(0.2*self.mass*9.8/LA.norm(self.force),1)*self.force
				entity.add_force(staticFriction)
				return
			else:
				
def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    screenWidth,screenHeight = screen.get_size()
    screenSize = np.array(screen.get_size())
    pygame.display.set_caption("Newton World")
    screen.fill((255,255,255))
    pygame.display.flip()
   
    world = NewtonWorld("NewtonWorld",screen)
    square = NewtonianEntity(world,position=screenSize/2)
    world.add(square)
   
    world.unpause()
    world.run_main_loop()
    pygame.quit()

if __name__ == "__main__":
	main()
