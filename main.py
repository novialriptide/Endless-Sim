from pygame import mouse
import Sakuya
import pygame
import sys
import random
import math
from Sakuya.math import get_angle, to_units
from Sakuya.vector import *

WINDOW_SIZE = Vector(480, 640)
TICKS_PER_SEC = 16

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE.x, WINDOW_SIZE.y))
pygame.display.set_caption("Endless Sim (PRE-ALPHA)")
clock = pygame.time.Clock()
sak_time = Sakuya.Time()
delta_time = 0
ticks_past = 0

# MAIN WORLD SETUP
world = Sakuya.World()
world.gravity = Vector(0, 0)

def spread_attack(mid, min, max, speed: float, projectile_count: int, repeat: int, delay_per_bullet: int, delay_per_shot, rng_range: float):
    projectiles = []
    dist = (max - min) / projectile_count
    for p in range(projectile_count):
        projectiles.append(dist*p + mid + min)

    return {"projectiles": projectiles, "speed": speed, "repeat": repeat, "dpb": delay_per_bullet, "dps": delay_per_shot, "rng_range": rng_range}

# ENTITIES
CHUNAMI = Sakuya.Entity(
    Vector(to_units(WINDOW_SIZE.x/2), 10),
    Sakuya.Unit(5),
    pygame.Surface([10, 10])
)

PROJECTILE = Sakuya.Entity(
    Vector(0, 0),
    Sakuya.Unit(1),
    pygame.Surface([2, 2])
)

CHUNAMI.ATTACKS = [
    spread_attack(90, -50, 50, 10, 20, 1, 50, 500, 0.008)
]

def attack(entity: Sakuya.Entity, atk_id):
    atk_list = CHUNAMI.ATTACKS[atk_id]
    bullet_time_offset = 0
    for atk in atk_list["projectiles"]:
        def time_stuff(o, p, a, s):
            p = entity.shoot(o, p, a, s)
            p.on_destroy(10000)
            world.objects.append(p)

        t = Sakuya.Event(
            bullet_time_offset, time_stuff, 
            [Vector(0, 0), PROJECTILE, math.radians(atk) + random.uniform(-atk_list["rng_range"], atk_list["rng_range"]), atk_list["speed"]]
        )
        sak_time.wait(t)
        bullet_time_offset += atk_list["dpb"]

world.objects.append(CHUNAMI)

if __name__ == "__main__":
    while(True):
        mouse_pos = Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                attack(CHUNAMI, 0)

        screen.fill((0,0,0))
        for o in world.objects:
            pygame.draw.circle(screen, (255,255,255), o.hitbox.position.to_list(), o.hitbox.radius)

        pygame.draw.line(
            screen, (0,255,0), 
            Sakuya.to_pixels(CHUNAMI.position).to_list(), 
            pygame.mouse.get_pos()
        )
        
        fps = Sakuya.text(f"fps: {int(clock.get_fps())}", 20, "Arial", (0, 255, 0))
        objects_loaded = Sakuya.text(f"loaded objects: {len(world.objects)}", 20, "Arial", (0, 255, 0))
        screen.blit(fps, (0,0))
        screen.blit(objects_loaded, (0,20))

        pygame.display.update()
        world.advance_frame(delta_time)
        sak_time.update()
        delta_time = 1 / clock.tick(60)