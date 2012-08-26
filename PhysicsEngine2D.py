# Physics Engine
import numpy as np
import pygame
from pygame.locals import *
 
from GameEngine2D import NewtonWorld,GraphicEntity
 
def elastic_collision(entity1,entity2,normalVector):
    #print "ELASTIC COLLISION"
    normalVector = np.array(normalVector)
    m1,m2 = entity1.mass,entity2.mass
    u1 = np.dot(entity1.get_velocity(units="PIX"),normalVector)
    u2 = np.dot(entity2.get_velocity(units="PIX"),normalVector)
    v1 = (u1*(m1-m2)+2*m2*u2)/(m1+m2)
    v2 = (u2*(m2-m1)+2*m1*u1)/(m1+m2)
   
    entity1.add_velocity((v1-u1)*normalVector,units="PIX")
    entity2.add_velocity((v2-u2)*normalVector,units="PIX")
   
class NewtonianEntity(GraphicEntity):
    """
    Arguments:
    ----------------------------------------------------------------
    mass            | mass of the entity (kg)
    centerOfMass    | relative to topleft of image (if None, use center of image) IN PIXELS
    inertia         | moment of inertia wrt the z axis (kg * m^2)
    position        | position of center of mass in world (meters,meters)
    velocity        | in meters per second (m/s)
    acceleration    | in meters per second per second (m/s^2)
    force           | in Newtons (kg * m/s^2)
    image           | entity's image
   
    *Note that 'force' and 'inertia' values need to be scaled appropriately
    ----------------------------------------------------------------
    """
    def __init__(self,world,mass=1,centerOfMass=None,inertia=1,position=(0,0),velocity=(0,0),acceleration=(0,0),force=(0,0),image=None,charge=None):
        self.world = world
        self.type = "NewtonianEntity"
        self.scale = self.world.scale
 
        self.image = image
        if not image:
            self.image = pygame.Surface((20,20))
            self.image.fill(pygame.Color('red'))
        self.size = np.array(self.image.get_size())
               
        self.position = np.array(position,float)*self.world.scale
        self.velocity = np.array(velocity,float)*self.world.scale
        self.acceleration = np.array(acceleration,float)*self.world.scale
        self.mass = mass
        if not centerOfMass: centerOfMass = self.size/2
        self.centerOfMass = np.array(centerOfMass,float)
        self.force = np.array(force,float) * self.scale
        self.charge = charge
       
        self.rect = pygame.Rect(self.position-self.centerOfMass,self.size)
        self.init()
       
    def init(self):
        # Initialize any non-standard parameters here
        pass
   
    def process(self,dt):
        # TODO: Collision detection
        # Kinematics
        self.acceleration = self.force * dt / self.mass
        self.velocity += self.acceleration * dt
        self.position += self.velocity
       
        self.rect.topleft = self.position - self.centerOfMass
       
    def set_force(self,force):
        # Force argument is in N, force attribute is in kg * pixels/s^2
        self.force = np.array(force,float) * self.scale
       
    def add_force(self,force):
        self.force += np.array(force) * self.scale
       
    def set_velocity(self,velocity,units="SI"):
        # Velocity argument in m/s
        self.velocity = np.array(velocity,float) * (self.scale if units=="SI" else 1.)
        #print "Set velocity at",self.velocity
   
    def add_velocity(self,velocity,units="SI"):
        self.velocity += np.array(velocity) * (self.scale if units=="SI" else 1.)
        
    def set_position(self,position,units="SI"):
		self.position = np.array(position) * (self.scale if units=="SI" else 1.)
       
    def get_position(self,units='SI'):
        if units == 'SI':
            return self.position/self.scale
        else:
            return self.position
           
    def get_velocity(self,units="SI"):
        if units == "SI":
            return self.velocity/self.scale
        else:
            return self.velocity
           
    def get_acceleration(self,units="SI"):
        if units == "SI":
            return self.acceleration/self.scale
        else:
            return self.acceleration
   
class CollidingEntity(NewtonianEntity):
    def __init__(self,world,mass=1,centerOfMass=None,inertia=1,position=(0,0),
                 velocity=(0,0),acceleration=(0,0),force=(0,0),image=None,charge=None,
                 collisionPoints=[]):
        """
        Arguments
        ----------------------------------------------------------------
        collisionPoints     | a list of tuples of the form
                            | (collisionPoint,normalVector @ that point)
        ----------------------------------------------------------------
        """
        self.collisionPoints = collisionPoints
        NewtonianEntity.__init__(self,world,mass=mass,centerOfMass=centerOfMass,
                                 inertia=inertia,position=position,velocity=velocity,
                                 acceleration=acceleration,force=force,image=image,charge=charge)
        
       
    def process(self,dt):
        # Collision detection
        self.check_collisions()
       
        # Kinematics
        self.acceleration = self.force * dt / self.mass
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
       
        self.rect.topleft = self.position - self.centerOfMass
        
        self.stabilize()
       
    def check_collisions(self):
        #print "Checking...",self.world.get_entities()
        for entity in self.world.get_entities():
            if isinstance(entity,CollidingEntity) and entity != self:
                for point,normalVector in self.collisionPoints:
                    if np.dot(normalVector,self.velocity) >= 0:
						#print "Point:",point, "in",entity.type,"?"
						if entity.collides_with(point+self.rect.topleft):
							elastic_collision(self,entity,normalVector)
                        
    def collides_with(self,point):
		# Implement for each custom game object
		return False
                        
    def stabilize(self):
		for i in range(2):
			if abs(self.velocity[i]) < 0.0001:
				self.velocity[i] = 0.
       
class PhysicsWorld(NewtonWorld):
    """
    Arguments:
    --------------------------------------------------------------------    
    scale           | pixels per meter (to set physical constants appropriately)
    --------------------------------------------------------------------
    """
    def __init__(self,name,surface,background=None,framesPerSecond=40,scale=10,muS=0.3,muK=0.2):
        NewtonWorld.__init__(self,name,surface,background,framesPerSecond)
        self.scale = scale
       
        # Define Physical Constants
        self.fields = []
        self.gravity = 9.8 * scale  # Gravitational force into the screen
   
    def run_main_loop(self):
        while True:            
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
 
    def add_field(self,field):
        assert(isinstance(field,Field))
        self.fields.append(Field)
