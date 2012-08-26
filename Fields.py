# Standard Fields
import numpy as np
import math

class Field(object):
	""" All parameters or physical constants should be given in SI
	units unless there is no equivalent
	"""
	def __init__(self,name,world):
		self.name = name
		self.world = world
		
	def get_vector(self,entity):
		pass
		
	def apply(self,entity):
		force = self.get_vector(entity)
		entity.add_force(force)
		
	def apply_all(self):
		for entity in self.world.get_entities():
			if isinstance(entity,NewtonianEntity):
				self.apply(entity)
			
class Gravity(Field):
	def __init__(self,world,g):
		Field.__init__("Gravity",world)
		self.g = g * world.scale
		
	def get_vector(self,entity):
		return np.array((0,0,-self.g),float)
		
	def apply(self,entity):
		if len(entity.position) == 3:
			entity.add_force(self.get_vector(entity.position))
			
class PlanarGravity(Field):
	def __init__(self,world,sourcePosition,mass,G):
		Field.__init__("PlanarGravity",world)
		self.sourcePosition = np.array(sourcePosition)
		
		# Convert from m^3/(kg*s) to pixels^3/(kg*s)
		self.GM = G * mass * world.scale**3
		
	def get_vector(self,entity):
		d = self.sourcePosition - entity.position
		force = self.GM*entity.mass/p.dot(d,d)*d/LA.norm(d)
		return force
		
class ElectricField(Field):
	"""
	Arguments:
	--------------------------------------------------------------------    
	source		| entity with a charge creating this field
	E0			| permittivity of free space (8.85E-12 C^2/(N*m^2))		
	--------------------------------------------------------------------
	"""
	def __init__(self,world,source,E0=8.85e-12):
		Field.__init__("PlanarGravity",world)
		self.source = source
		
		# Convert from m^3/(kg*s) to pixels^3/(kg*s)
		self.FourPiE0 = 4*math.pi*E0 / world.scale**2
		
		assert(self.source.charge is not None)
		
	def get_vector(self,entity):
		if entity.charge:
			r = source.position - entity.position
			rSquared = np.dot(r,r)
			force = entity.charge*self.source.charge/(self.FourPiE0*rSquared) / LA.norm(r) * r 
			return force
		return np.array((0,0))
		
			
class Friction(Field):
	"""
	Not a 'field' in the physical sense, but we can exploit the Field
	class to implement friction
	"""
	def __init__(self,world,muS,muK):
		Field.__init__("Friction",world)
		self.muS = muS
		self.muK = muK
		
	def apply(self,entity):
		if LA.norm(entity.velocity) <= 0.01:
			if LA.norm(entity.force) > 0:
				staticFriction = -min(self.muS*entity.mass*self.gravity/LA.norm(entity.force),1)*entity.force
				#print "static friction:",staticFriction
				entity.add_force(staticFriction)
				return
			else:
				entity.velocity = np.array((0.,0.))
		else:
			kineticFriction = -self.muK*entity.mass*self.gravity*entity.velocity/LA.norm(entity.velocity)
			#print "kinitec friction:",kineticFriction, "velocity:",entity.velocity
			entity.add_force(kineticFriction)
			return
		
