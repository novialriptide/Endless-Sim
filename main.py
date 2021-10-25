from pygame import mouse
import Sakuya
import pygame
import sys
from Sakuya.math import get_angle

from Sakuya.vector import vector

WINDOW_SIZE = vector(640, 480)
TICKS_PER_SEC = 16

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE.x, WINDOW_SIZE.y))
pygame.display.set_caption("Endless Sim (PRE-ALPHA)")
clock = pygame.time.Clock()
delta_time = 0
ticks_past = 0

# ENTITIES
CHUNAMI = Sakuya.entity(
    vector(10, 20),
    Sakuya.unit(2),
    pygame.Surface([10, 10]) # add surface size adjust to units 
)

DRONE = Sakuya.entity(
    vector(15, 20),
    Sakuya.unit(1),
    pygame.Surface([10, 10])
)

PROJECTILE = Sakuya.entity(
    vector(0, 0),
    Sakuya.unit(0.5),
    pygame.Surface([2, 2])
)

# MAIN WORLD SETUP
world = Sakuya.world()
world.gravity = vector(0, 0)
world.objects.append(CHUNAMI)
world.objects.append(DRONE)

if __name__ == "__main__":
    while(True):
        mouse_pos = vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                angle = Sakuya.get_angle(CHUNAMI.position, Sakuya.to_units(mouse_pos))
                p = CHUNAMI.shoot(PROJECTILE, angle, 5)
                print(CHUNAMI.position, Sakuya.to_units(mouse_pos), angle, p.velocity)
                world.objects.append(p)

        screen.fill((0,0,0))
        for o in world.objects:
            pygame.draw.rect(screen, (255,255,255), o.hitbox)

        pygame.draw.line(
            screen, (0,255,0), 
            Sakuya.to_pixels(CHUNAMI.position).to_list(), 
            pygame.mouse.get_pos()
        )

        pygame.display.update()
        world.advance_frame(delta_time)
        delta_time = 1 / clock.tick(60)