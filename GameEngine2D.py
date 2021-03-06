import pygame
from pygame.locals import *
import numpy as np
from numpy import linalg as LA
 
DEBUG = True
 
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
        self.rect = pygame.Rect(self.position - self.size/2,self.size)
   
    def render(self,surface):
        surface.blit(self.image,self.rect)
       
    def erase(self):
        self.world.surface.blit(self.world.background,self.rect,self.rect)
 
    def get_rect(self):
        return self.rect.copy()
 
    def move_to(self,position):
        self.position = np.array(position)
        self.rect.center = self.position
             
 
class NewtonWorld(World):
    """
    Arguments:
    --------------------------------------------------------------------    
    scale           | pixels per meter (to set physical constants appropriately)
    --------------------------------------------------------------------
    """
    def __init__(self,name,surface,background=None,framesPerSecond=40,scale=10,muS=0.3,muK=0.2):
        World.__init__(self,name,surface,background,framesPerSecond)
        self.scale = scale
       
        # Define Physical Constants
        self.fields = []
        self.gravity = 9.8 * scale  # Gravitational force into the screen
       
    def run_main_loop(self):
        while True:
            if DEBUG:
			    soleEntity = self.get_entities()[0]
			    soleEntity.set_force((0.,0.))
			    keysPressed = pygame.key.get_pressed()
			    if keysPressed[K_UP]:
			        soleEntity.add_force((0.,-30.))
			    if keysPressed[K_DOWN]:
			        soleEntity.add_force((0.,30.))
			    if keysPressed[K_RIGHT]:
			        soleEntity.add_force((30.,0.))
			    if keysPressed[K_LEFT]:
			        soleEntity.add_force((-30.,0.))
								   
            self.apply_fields()
            self.main_loop()
           
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
 
    def apply_fields(self):
        for field in self.fields:
            field.apply_all()


def main():
    SCALE = 10 # pixels per meter
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    screenWidth,screenHeight = screen.get_size()
    worldSize = np.array(screen.get_size())/SCALE
    pygame.display.set_caption("Newton World")
    screen.fill((255,255,255))
    pygame.display.flip()
   
    world = StandardPhysicalWorld("NewtonWorld",screen,framesPerSecond=40,scale=SCALE)
    square = NewtonianEntity(world,position=worldSize/2,mass=1)
    world.add(square)
   
    world.unpause()
    world.run_main_loop()
    pygame.quit()
 
if __name__ == "__main__":
    main()
