from numpy.lib.function_base import angle
from pygame import mouse
import Sakuya
import pygame
import sys
import random
import math
from Sakuya.math import *

WINDOW_SIZE = Vector(480, 640)
TICKS_PER_SEC = 16
BUTTONS = {"up": pygame.K_UP, "left": pygame.K_LEFT, "down": pygame.K_DOWN, "right": pygame.K_RIGHT, "shoot": pygame.K_z}
MAX_PROJECTILES = 1000
BOSSBAR_UPDATE_SPEED = to_pixels(5)
PLAYER_SHOOTING_COOLDOWN = 100

pygame.init()
pg_flags = pygame.SCALED
screen = pygame.display.set_mode(size=(WINDOW_SIZE.x, WINDOW_SIZE.y), flags = pg_flags)
pygame.display.set_caption("Endless Sim (PRE-ALPHA)")
clock = pygame.time.Clock()
sak_time = Sakuya.Time()
delta_time = 0
ticks_past = 0
current_scene = None
mouse_pos = Vector(0, 0)
angle_attack = 0

# Main world setup
world = Sakuya.World()
world.gravity = Vector(0, 0)

def spread_attack(speed: float, projectile_count: int, delay_per_bullet: int, rng_range: float, damage: float, mid, min, max):
    projectiles = []
    dist = (max - min) / projectile_count
    for p in range(projectile_count):
        projectiles.append(dist*p + mid + min)

    return {"projectiles": projectiles, "speed": speed, "dpb": delay_per_bullet, "rng_range": rng_range, "damage": damage}

def spiral_attack(speed: float, projectile_count: int, delay_per_bullet: int, rng_range: float, damage: float):
    projectiles = []
    dist = 1 / projectile_count
    for p in range(projectile_count):
        projectiles.append(dist * 360 * p)
        
    return {"projectiles": projectiles, "speed": speed, "dpb": delay_per_bullet, "rng_range": rng_range, "damage": damage}

def target_attack(speed: float, projectile_count: int, delay_per_bullet: int, rng_range: float, damage: float, mid):
    projectiles = []
    dist = 1 / projectile_count
    for p in range(projectile_count):
        projectiles.append(mid + angle_attack)
    
    return {"projectiles": projectiles, "speed": speed, "dpb": delay_per_bullet, "rng_range": rng_range, "damage": damage}

# Player Setup
PLAYER = Sakuya.Entity(
    Vector(to_units(WINDOW_SIZE.x/2), 40),
    Sakuya.Unit(0.5),
    pygame.Surface([10, 10])
)
PLAYER.speed = 0.03
is_moving_left = False
is_moving_right = False
is_moving_down = False
is_moving_up = False
is_shooting = False
can_shoot = True
player_damage = 1

# Projectile Setup
CHUNAMI_PROJECTILE = Sakuya.Entity(
    Vector(0, 0),
    Sakuya.Unit(1),
    pygame.Surface([2, 2]),
    name = "CHUNAMI PROJECTILE"
)

PLAYER_PROJECTILE = Sakuya.Entity(
    Vector(0, 0),
    Sakuya.Unit(1),
    pygame.Surface([2, 2]),
    name = "PLAYER PROJECTILE"
)

# Chunami setup
CHUNAMI = Sakuya.Entity(
    Vector(to_units(WINDOW_SIZE.x/2), 10),
    Sakuya.Unit(5),
    pygame.Surface([10, 10])
)
CHUNAMI.MAX_HEALTH = 3000
CHUNAMI.current_health = CHUNAMI.MAX_HEALTH

chunami_moveset1 = Sakuya.Replay()
chunami_moveset2 = Sakuya.Replay()
chunami_moveset3 = Sakuya.Replay()
chunami_bossbar = Sakuya.BossBar(CHUNAMI.MAX_HEALTH, BOSSBAR_UPDATE_SPEED)

def chu_atk1(): return target_attack(10, 5, 50, 0, 10, 180)
def chu_atk2(): return spread_attack(10, 15, 50, 0.008, 10, 90, -50, 50)
def chu_atk3(): return spiral_attack(10, 15, 0, 0, 10)

CHUNAMI.ATTACKS = [chu_atk1, chu_atk2, chu_atk3]
for m in CHUNAMI.ATTACKS:
    chunami_moveset1.methods.append(m)

def attack(shooter: Sakuya.Entity, atk_id, start_angle: float):
    atk_list = CHUNAMI.ATTACKS[atk_id]()
    bullet_time_offset = 0
    for atk in atk_list["projectiles"]:
        def time_stuff(o, p, a, s):
            p = shooter.shoot(o, p, a+start_angle, s)
            p.on_destroy(3000)
            world.objects.append(p)

        t = Sakuya.Event(
            bullet_time_offset, time_stuff, 
            [Vector(0, 0), CHUNAMI_PROJECTILE, math.radians(atk) + random.uniform(-atk_list["rng_range"], atk_list["rng_range"]), atk_list["speed"]]
        )
        sak_time.wait(t)
        bullet_time_offset += atk_list["dpb"]

world.objects.append(PLAYER)
world.objects.append(CHUNAMI)

def game_scene():
    global is_moving_up
    global is_moving_down
    global is_moving_left
    global is_moving_right
    global is_shooting
    global delta_time
    global current_scene
    global mouse_pos
    global angle_attack
    global shooting_cooldown
    global can_shoot

    mouse_pos = to_vector(pygame.mouse.get_pos())
    angle_attack = math.degrees(get_angle(PLAYER.position, CHUNAMI.position))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                attack(CHUNAMI, 0, 0)
            if event.key == pygame.K_2:
                attack(CHUNAMI, 1, 0)
            if event.key == pygame.K_3:
                attack(CHUNAMI, 2, 0)
            if event.key == BUTTONS["up"]:
                is_moving_up = True
            if event.key == BUTTONS["down"]:
                is_moving_down = True
            if event.key == BUTTONS["left"]:
                is_moving_left = True
            if event.key == BUTTONS["right"]:
                is_moving_right = True
            if event.key == BUTTONS["shoot"]:
                is_shooting = True
        if event.type == pygame.KEYUP:
            if event.key == BUTTONS["up"]:
                is_moving_up = False
            if event.key == BUTTONS["down"]:
                is_moving_down = False
            if event.key == BUTTONS["left"]:
                is_moving_left = False
            if event.key == BUTTONS["right"]:
                is_moving_right = False
            if event.key == BUTTONS["shoot"]:
                is_shooting = False

    # Adds player movement
    movement = Vector(0, 0)
    if is_moving_up: movement += Vector(0, -to_pixels(PLAYER.speed))
    if is_moving_down: movement += Vector(0, to_pixels(PLAYER.speed))
    if is_moving_right: movement += Vector(to_pixels(PLAYER.speed), 0)
    if is_moving_left: movement += Vector(-to_pixels(PLAYER.speed), 0)
    PLAYER.position += movement

    # Test for collisions
    collided = world.test_collisions(PLAYER)
    for c in collided:
        if c.name == "CHUNAMI PROJECTILE":
            current_scene = dead_scene
            world.objects.remove(c)
    
    collided = world.test_collisions(CHUNAMI)
    for c in collided:
        if c.name == "PLAYER PROJECTILE":
            if CHUNAMI.current_health >= 0:
                CHUNAMI.current_health -= player_damage
                world.objects.remove(c)
    
    # Draws background
    screen.fill((0,0,0))

    # Draws debug hitboxes
    for o in world.objects:
        pygame.draw.circle(screen, (255,255,255), o.hitbox.position.to_list(), o.hitbox.radius)
    
    # Player shooting
    if is_shooting and can_shoot:
        def can_shoot_func():
            global can_shoot
            can_shoot = True

        player_shooting_event = Sakuya.Event(PLAYER_SHOOTING_COOLDOWN, can_shoot_func)
        p = PLAYER.shoot(Vector(0,-2), PLAYER_PROJECTILE, math.radians(-90), 30)
        p.on_destroy(3000)
        world.objects.append(p)
        can_shoot = False
        sak_time.wait(player_shooting_event)

    # Draws debug values
    pixel_offset = to_pixels(2)
    fps = Sakuya.text(f"fps: {int(clock.get_fps())}", 20, "Arial", (0, 255, 0))
    objects_loaded = Sakuya.text(f"loaded objects: {len(world.objects)}", 20, "Arial", (0, 255, 0))
    screen.blit(fps, (0,pixel_offset))
    screen.blit(objects_loaded, (0,20 + pixel_offset))
    
    # Chunami's Boss Bar
    chunami_bossbar.current_health = CHUNAMI.current_health
    bossbar_percentage = chunami_bossbar.display_health / chunami_bossbar.max_health
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(0,0,to_pixels(30), to_pixels(2)))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(0,0,to_pixels(bossbar_percentage * 30), to_pixels(2)))
    
    # Update values
    pygame.display.update()
    world.advance_frame(delta_time)
    sak_time.update()
    chunami_bossbar.update()
    delta_time = 1 / clock.tick(60)

def dead_scene():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Draws background
    screen.fill((0,0,0))

    # Draws game over message
    game_over_text = Sakuya.text("gane oer", 20, "Arial", (0, 255, 0))
    screen.blit(game_over_text, (WINDOW_SIZE.x/2,WINDOW_SIZE.y/2))

    # Draws debug values
    fps = Sakuya.text(f"fps: {int(clock.get_fps())}", 20, "Arial", (0, 255, 0))
    objects_loaded = Sakuya.text(f"loaded objects: {len(world.objects)}", 20, "Arial", (0, 255, 0))
    screen.blit(fps, (0,0))
    screen.blit(objects_loaded, (0,20))

    # loop
    pygame.display.update()
    sak_time.update()
    delta_time = 1 / clock.tick(60)

current_scene = game_scene
if __name__ == "__main__":
    while(True):
        current_scene()