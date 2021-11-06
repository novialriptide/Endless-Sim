from pygame import mouse
from pygame.display import update
import Sakuya
import pygame
import sys
import random
import math
import copy
from Sakuya.math import *
from Sakuya.object import Object
from Sakuya.replay import Frame
from assets import *

WINDOW_SIZE = Vector(480, 640)
BUTTONS = {
    "up": pygame.K_UP, 
    "left": pygame.K_LEFT, 
    "down": pygame.K_DOWN, 
    "right": pygame.K_RIGHT, 
    "shoot": pygame.K_z,
    "use": pygame.K_x,
    "select": pygame.K_a,
    "start": pygame.K_s
}
MAX_PROJECTILES = 1000
BOSSBAR_UPDATE_SPEED = to_pixels(0.2)
PLAYER_SHOOTING_COOLDOWN = 100

pygame.init()
Sakuya.init()
pg_flags = pygame.SCALED
screen = pygame.display.set_mode(size=(WINDOW_SIZE.x, WINDOW_SIZE.y), flags = pg_flags)
pygame.display.set_caption("Endless Sim (PRE-ALPHA)")
clock = pygame.time.Clock()
sak_time = Sakuya.Time()
delta_time = 0
current_scene = None
mouse_pos = Vector(0, 0)
angle_attack = 0
game_state = "Main" # Main, Game, Pause, Dead
score = 0

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

def attack(shooter: Sakuya.Entity, projectile_data, start_angle: float):
    bullet_time_offset = 0
    for atk in projectile_data["projectiles"]:
        def time_stuff(o, p, a, s):
            global score
            p = shooter.shoot(o, p, a+start_angle, s)
            p.on_destroy(2000)
            world.objects.append(p)
            score += 10

        t = Sakuya.Event(
            bullet_time_offset, time_stuff, 
            [Vector(0, 0), CHUNAMI_PROJECTILE, math.radians(atk) + random.uniform(-projectile_data["rng_range"], projectile_data["rng_range"]), projectile_data["speed"]]
        )
        sak_time.wait(t)
        bullet_time_offset += projectile_data["dpb"]

# Player Setup
PLAYER = Sakuya.Entity(
    Vector(to_units(WINDOW_SIZE.x/2), 40),
    Sakuya.Unit(0.5),
    pygame.Surface([10, 10]),
    name = "PLAYER"
)
PLAYER.speed = 0.03
is_moving_left = False
is_moving_right = False
is_moving_down = False
is_moving_up = False
is_shooting = False
can_shoot = True
player_damage = 10

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
    pygame.Surface([10, 10]),
    name = "CHUNAMI"
)
CHUNAMI.MAX_HEALTH = 1000
CHUNAMI.current_health = CHUNAMI.MAX_HEALTH
CHUNAMI.speed = 0.3
chunami_bossbar = Sakuya.BossBar(CHUNAMI.MAX_HEALTH, BOSSBAR_UPDATE_SPEED)

def chu_move0():
    CHUNAMI.target_position = Vector(random.randint(5, to_units(WINDOW_SIZE.x)-5), random.randint(5, int(to_units(WINDOW_SIZE.y * (1/3)))-5))

def chu_atk1(): attack(CHUNAMI, target_attack(10, 3, 50, 0, 10, 180), 0)
def chu_atk2(): attack(CHUNAMI, spread_attack(10, 10, 50, 0.008, 10, 90, -50, 50), 0)
def chu_atk3(): attack(CHUNAMI, spiral_attack(10, 10, 0, 0, 10), 0)

chunami_ai = Sakuya.AI(
    [
        Sakuya.Decision(chu_move0, 0.001),
        Sakuya.Decision(chu_atk1, 0.5),
        Sakuya.Decision(chu_atk2, 0.3),
        Sakuya.Decision(chu_atk3, 0.4)
    ], 10, max_decisions=2
)

world.objects.append(PLAYER)
world.objects.append(CHUNAMI)

def input():
    global is_moving_up
    global is_moving_down
    global is_moving_left
    global is_moving_right
    global is_shooting
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == BUTTONS["up"] and game_state == "Game":
                is_moving_up = True
            if event.key == BUTTONS["down"] and game_state == "Game":
                is_moving_down = True
            if event.key == BUTTONS["left"] and game_state == "Game":
                is_moving_left = True
            if event.key == BUTTONS["right"] and game_state == "Game":
                is_moving_right = True
            if event.key == BUTTONS["shoot"] and game_state == "Game":
                is_shooting = True
        if event.type == pygame.KEYUP:
            if event.key == BUTTONS["up"] and game_state == "Game":
                is_moving_up = False
            if event.key == BUTTONS["down"] and game_state == "Game":
                is_moving_down = False
            if event.key == BUTTONS["left"] and game_state == "Game":
                is_moving_left = False
            if event.key == BUTTONS["right"] and game_state == "Game":
                is_moving_right = False
            if event.key == BUTTONS["shoot"] and game_state == "Game":
                is_shooting = False

def main_menu():
    global delta_time
    global current_scene
    global game_state
    global score

    game_state = "Main"
    buttons = []
    input()

    # Draws background
    screen.fill((0,0,0))
    tLOGO1 = pygame.transform.scale(LOGO1, (LOGO1.get_width()*3, LOGO1.get_height()*3))
    screen.blit(tLOGO1, (WINDOW_SIZE.x/2-tLOGO1.get_width()/2, WINDOW_SIZE.y*(1/4)-tLOGO1.get_height()/2))

    # Buttons
    ## Play Button
    def play_button_f():
        global current_scene
        current_scene = game_scene
    play_text = Sakuya.text("Play", to_pixels(4), "Arial", (0,0,0))
    play_rect = play_text.get_rect()
    play_rect.x = WINDOW_SIZE.x/2 - play_rect.width/2
    play_rect.y = WINDOW_SIZE.y * (3/5) - play_rect.height/2
    play_button = Sakuya.Button(play_rect, [play_button_f], key=BUTTONS["start"])
    pygame.draw.rect(screen, (255,0,0), play_button.rect)
    screen.blit(play_text, (play_button.rect.x, play_button.rect.y))
    buttons.append(play_button)

    # Update values
    world.advance_frame(delta_time)
    sak_time.update()
    pygame.display.update()
    for b in buttons: b.update()
    delta_time = 1 / clock.tick(60)

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
    global game_state
    global score
    
    game_state = "Game"
    mouse_pos = to_vector(pygame.mouse.get_pos())
    angle_attack = math.degrees(get_angle(PLAYER.position, CHUNAMI.position))
    input()

    # Adds player movement
    movement = Vector(0, 0)
    if is_moving_up: movement += Vector(0, -to_pixels(PLAYER.speed))
    if is_moving_down: movement += Vector(0, to_pixels(PLAYER.speed))
    if is_moving_right: movement += Vector(to_pixels(PLAYER.speed), 0)
    if is_moving_left: movement += Vector(-to_pixels(PLAYER.speed), 0)
    PLAYER.position += movement

    # Test for collisions
    try:
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
    except ObjectNotInWorld:
        pass

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
    score_text = Sakuya.text(f"score: {score}", 20, "Arial", (0, 255, 0))
    screen.blit(fps, (0,pixel_offset))
    screen.blit(objects_loaded, (0,20 + pixel_offset))
    screen.blit(score_text, (0,40 + pixel_offset))
    
    # Chunami's Boss Bar & AI
    chunami_bossbar.current_health = CHUNAMI.current_health
    bossbar_percentage = chunami_bossbar.display_health / chunami_bossbar.max_health
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(0,0,to_pixels(30), to_pixels(2)))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(0,0,to_pixels(bossbar_percentage * 30), to_pixels(2)))
    
    chunami_ai.update_decisions(world.ticks_elapsed)

    # Update values
    world.advance_frame(delta_time)
    sak_time.update()
    chunami_bossbar.update()
    pygame.display.update()
    delta_time = 1 / clock.tick(60)

def dead_scene():
    global game_state
    global score

    game_state = "Dead"
    buttons = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Draws background
    screen.fill((0,0,0))

    # Draws game over message
    game_over_text = Sakuya.text("game over", 20, "Arial", (0, 255, 0))
    screen.blit(game_over_text, (WINDOW_SIZE.x/2 - game_over_text.get_rect().width/2,WINDOW_SIZE.y * (1/3) - game_over_text.get_rect().height/2))

    # Buttons
    ## Try Again Button
    def try_again_button_f():
        global current_scene
        global score
        global is_moving_down
        global is_moving_left
        global is_moving_right
        global is_moving_up
        global is_shooting
        global CHUNAMI

        world.objects = []
        is_moving_up = False
        is_moving_down = False
        is_moving_right = False
        is_moving_left = False
        is_shooting = False
        CHUNAMI.current_health = CHUNAMI.MAX_HEALTH
        world.objects.append(PLAYER)
        world.objects.append(CHUNAMI)
        current_scene = main_menu
        score = 0

    try_again_text = Sakuya.text("Try Again?", to_pixels(4), "Arial", (0,0,0))
    try_again_rect = try_again_text.get_rect()
    try_again_rect.x = WINDOW_SIZE.x/2 - try_again_rect.width/2
    try_again_rect.y = WINDOW_SIZE.y * (3/5) - try_again_rect.height/2
    try_again_button = Sakuya.Button(try_again_rect, [try_again_button_f], key=BUTTONS["start"])
    pygame.draw.rect(screen, (255,0,0), try_again_button.rect)
    screen.blit(try_again_text, (try_again_button.rect.x, try_again_button.rect.y))
    buttons.append(try_again_button)

    # Draws debug values
    fps = Sakuya.text(f"fps: {int(clock.get_fps())}", 20, "Arial", (0, 255, 0))
    objects_loaded = Sakuya.text(f"loaded objects: {len(world.objects)}", 20, "Arial", (0, 255, 0))
    score_text = Sakuya.text(f"score: {score}", 20, "Arial", (0, 255, 0))
    screen.blit(fps, (0,0))
    screen.blit(objects_loaded, (0,20))
    screen.blit(score_text, (0,40))

    # loop
    pygame.display.update()
    sak_time.update()
    for b in buttons: b.update()
    delta_time = 1 / clock.tick(60)

current_scene = main_menu
if __name__ == "__main__":
    while(True):
        current_scene()