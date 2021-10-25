import typing
import pygame
from Sakuya.object import *
from Sakuya.vector import *
from Sakuya.config import *

class world:
    def __init__(self):
        self.objects = []
        self.gravity = vector(0, 10)
        self.current_tick = 1

        #pixels per unit
        self.ppu = 10

    def advance_frame(self, delta_time: float):
        """
        Updates the entities inside the world, such as physics & animation
        Should be added to the end of the main loop
        """
        if self.current_tick <= TICKS_PER_SECOND:
            self.current_tick = int(pygame.time.get_ticks() / 1000 * TICKS_PER_SECOND) % TICKS_PER_SECOND + 1
        if self.current_tick > TICKS_PER_SECOND:
            self.current_tick = 1

        for object in self.objects[:]:
            object._gravity = self.gravity
            object.update(delta_time)

            if object._is_destroyed:
                self.objects.remove(object)