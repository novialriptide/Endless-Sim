import pygame
import copy
from Sakuya.vector import *
from Sakuya.object import *
from Sakuya.math import *
from Sakuya.config import *

class entity(object):
    def __init__(self, position: vector, hitbox_radius: int, surface: pygame.Surface, has_rigidbody = True, has_box_collider = True):
        super().__init__(position, hitbox_radius, has_rigidbody=has_rigidbody, has_box_collider=has_box_collider)
        self.current_frame = 0
        self.current_animation = 0
        self.animations = []
        self.surface_offset = vector(0, 0)
        self._surface = surface

    @property
    def surface(self):
        """
        Returns a surface with the width and height in units
        """
        return pygame.transform.scale(self._surface, [self._surface.get_width(), self._surface.get_height()])
    
    def shoot(self, projectile, angle: float, speed: float):
        """
        :param entity projectile
        :param vector direction
        """
        projectile = copy.copy(projectile)
        projectile.velocity = vector(0, speed)
        projectile.velocity.rotate(angle)
        projectile.position = self.position
        return projectile

    def update(self, delta_time: float):
        super().update(delta_time)
        self.current_frame += 1