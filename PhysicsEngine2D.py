# Physics Engine
import numpy as np
import pygame

from GameEngine2D import NewtonWorld,NewtonianEntity
from Fields import Gravity,PlanarGravity, ElectricField,Friction

class PhysicsWorld(NewtonWorld):
