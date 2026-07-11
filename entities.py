import pygame

from settings import (
    TILE_SIZE, GRAVITY, PLAYER_SPEED, PLAYER_JUMP_STRENGTH, MAX_FALL_SPEED,
    ENEMY_SPEED, MARIO_RED, MARIO_SKIN, GOOMBA_BROWN, BLACK,
)


def move_and_collide(rect, vel_x, vel_y, solids):
    """Move rect by vel_x/vel_y one axis at a time, resolving collisions
    against a list of solid pygame.Rects. Returns (rect, collisions dict)."""
    collisions = {"left": False, "right": False, "top": False, "bottom": False}

    rect.x += vel_x
    for solid in solids:
        if rect.colliderect(solid):
            if vel_x > 0:
                rect.right = solid.left
                collisions["right"] = True
            elif vel_x < 0:
                rect.left = solid.right
                collisions["left"] = True

    rect.y += vel_y
    for solid in solids:
        if rect.colliderect(solid):
            if vel_y > 0:
                rect.bottom = solid.top
                collisions["bottom"] = True
            elif vel_y < 0:
                rect.top = solid.bottom
                collisions["top"] = True

    return rect, collisions


class Player:
    WIDTH = 30
    HEIGHT = 38

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.alive = True
        self.invincible_timer = 0  # brief invulnerability after taking a hit

    def handle_input(self, keys):
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

    def update(self, solids):
        self.apply_gravity()
        self.rect, collisions = move_and_collide(self.rect, self.vel_x, self.vel_y, solids)
        if collisions["bottom"]:
            self.on_ground = True
            self.vel_y = 0
        else:
            self.on_ground = False
        if collisions["top"]:
            self.vel_y = 0
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        return collisions

    def take_hit(self):
        if self.invincible_timer <= 0:
            self.invincible_timer = 90
            return True
        return False

    def draw(self, surface, camera_x):
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return  # flicker while invincible
        x = self.rect.x - camera_x
        y = self.rect.y
        # body
        pygame.draw.rect(surface, MARIO_RED, (x, y, self.rect.width, self.rect.height // 2))
        pygame.draw.rect(surface, MARIO_SKIN, (x, y + self.rect.height // 2,
                                                self.rect.width, self.rect.height // 2))
        # simple face direction indicator
        eye_x = x + (self.rect.width - 6) if self.facing_right else x + 2
        pygame.draw.rect(surface, BLACK, (eye_x, y + self.rect.height // 2 + 4, 4, 4))


class Goomba:
    WIDTH = 32
    HEIGHT = 30

    def __init__(self, x, y, patrol_min_x, patrol_max_x):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = -ENEMY_SPEED
        self.vel_y = 0
        self.alive = True
        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.squish_timer = 0

    def update(self, solids):
        if not self.alive:
            self.squish_timer -= 1
            return
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.rect, collisions = move_and_collide(self.rect, self.vel_x, self.vel_y, solids)
        if collisions["left"] or self.rect.left <= self.patrol_min_x:
            self.vel_x = ENEMY_SPEED
        if collisions["right"] or self.rect.right >= self.patrol_max_x:
            self.vel_x = -ENEMY_SPEED

    def squish(self):
        self.alive = False
        self.squish_timer = 20
        self.rect.height = 10

    def draw(self, surface, camera_x):
        if not self.alive and self.squish_timer <= 0:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (x, y, self.rect.width, self.rect.height))
        if self.alive:
            pygame.draw.rect(surface, BLACK, (x + 6, y + 8, 5, 5))
            pygame.draw.rect(surface, BLACK, (x + self.rect.width - 11, y + 8, 5, 5))
