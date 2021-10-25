from pygame import mouse
import Sakuya
import pygame
import sys
from Sakuya.math import get_angle, to_units

from Sakuya.vector import vector

WINDOW_SIZE = vector(480, 640)
TICKS_PER_SEC = 16

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE.x, WINDOW_SIZE.y))
pygame.display.set_caption("Endless Sim (PRE-ALPHA)")
clock = pygame.time.Clock()
delta_time = 0
ticks_past = 0

# MAIN WORLD SETUP
world = Sakuya.world()
world.gravity = vector(0, 0)

# ENTITIES
CHUNAMI = Sakuya.entity(
    vector(to_units(WINDOW_SIZE.x/2), 10),
    Sakuya.unit(5),
    pygame.Surface([10, 10])
)

PROJECTILE = Sakuya.entity(
    vector(0, 0),
    Sakuya.unit(1),
    pygame.Surface([2, 2])
)

CHUNAMI.ATTACKS = [
    [[
        [vector(1, 1), 5],
        [vector(0.5, 1), 5],
        [vector(0.25, 1), 5],
        [vector(0.1, 1), 5],
        [vector(-1, 1), 5],
        [vector(-0.5, 1), 5],
        [vector(-0.25, 1), 5],
        [vector(-0.1, 1), 5],
    ], 100]
]

def attack(entity: Sakuya.entity, atk_id):
    atk_list = CHUNAMI.ATTACKS[atk_id]
    for atk in atk_list:
        p = entity.shoot(PROJECTILE, get_angle(entity.position, entity.position + atk[0][0]), atk[0][1])
        world.objects.append(p)
        print(atk_list[1])
        pygame.time.delay(atk_list[1])

world.objects.append(CHUNAMI)

if __name__ == "__main__":
    while(True):
        mouse_pos = vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                attack(CHUNAMI, 0)

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