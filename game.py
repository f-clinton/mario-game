import pygame
import sys

from settings import (
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    SKY_BLUE, GROUND_BROWN, BRICK_RED, PIPE_GREEN, GOLD, WHITE, BLACK,
    FLAG_GREEN, POLE_GRAY,
)
from entities import Player, Goomba
from levels import LEVELS

ROWS = SCREEN_HEIGHT // TILE_SIZE  # 16

STATE_START = "start"
STATE_PLAYING = "playing"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"


class Block:
    def __init__(self, col, row, kind):
        self.rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.kind = kind  # "brick", "question", "used"

    def hit_from_below(self):
        if self.kind == "question":
            self.kind = "used"
            return True
        return False

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        if self.kind == "brick":
            color = BRICK_RED
        elif self.kind == "question":
            color = GOLD
        else:
            color = (120, 100, 80)
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)
        if self.kind == "question":
            font = pygame.font.SysFont("arial", 20, bold=True)
            text = font.render("?", True, BLACK)
            surface.blit(text, (x + TILE_SIZE // 2 - 5, y + TILE_SIZE // 2 - 10))


class Coin:
    def __init__(self, col, row):
        self.rect = pygame.Rect(col * TILE_SIZE + 10, row * TILE_SIZE + 10, 20, 20)
        self.collected = False

    def draw(self, surface, camera_x):
        if self.collected:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.ellipse(surface, GOLD, (x, y, self.rect.width, self.rect.height))
        pygame.draw.ellipse(surface, BLACK, (x, y, self.rect.width, self.rect.height), 2)


class Level:
    def __init__(self, data):
        self.data = data
        self.width_px = data["width"] * TILE_SIZE
        self.ground_row = data["ground_row"]
        self.gaps = data["gaps"]
        self.solids = []  # list of pygame.Rect (ground, pipes, stairs)
        self.blocks = []  # Block objects (also solid, but hittable)
        self.coins = [Coin(c, r) for c, r in data["coins"]]
        self.goombas = []
        self.flag_rect = None
        self.flag_col = data["flag_col"]
        self.spawn_x = 2 * TILE_SIZE
        self.spawn_y = (self.ground_row - 2) * TILE_SIZE
        self._build()

    def _in_gap(self, col):
        for start, end in self.gaps:
            if start <= col <= end:
                return True
        return False

    def _build(self):
        # ground
        for col in range(self.data["width"]):
            if self._in_gap(col):
                continue
            for row in range(self.ground_row, ROWS):
                self.solids.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                                TILE_SIZE, TILE_SIZE))

        # blocks (bricks / question blocks)
        for col, row, kind in self.data["blocks"]:
            self.blocks.append(Block(col, row, kind))

        # pipes
        for col, height in self.data["pipes"]:
            for h in range(height):
                row = self.ground_row - 1 - h
                for w in range(2):
                    self.solids.append(pygame.Rect((col + w) * TILE_SIZE, row * TILE_SIZE,
                                                    TILE_SIZE, TILE_SIZE))

        # ascending staircase leading to the flag
        stairs = self.data.get("stairs_up")
        if stairs:
            start_col = stairs["start_col"]
            steps = stairs["steps"]
            for i in range(steps):
                col = start_col + i
                for h in range(i + 1):
                    row = self.ground_row - 1 - h
                    self.solids.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                                    TILE_SIZE, TILE_SIZE))

        # goombas patrol a small range around their spawn point
        for col in self.data["goombas"]:
            x = col * TILE_SIZE
            y = (self.ground_row - 1) * TILE_SIZE
            self.goombas.append(Goomba(x, y, x - 3 * TILE_SIZE, x + 3 * TILE_SIZE))

        # flagpole
        pole_top_row = self.ground_row - 10
        self.flag_rect = pygame.Rect(self.flag_col * TILE_SIZE, pole_top_row * TILE_SIZE,
                                      TILE_SIZE // 2, (self.ground_row - pole_top_row) * TILE_SIZE)

    def all_solids(self):
        return self.solids + [b.rect for b in self.blocks if b.kind != "used" or True]

    def draw_background(self, surface, camera_x):
        surface.fill(SKY_BLUE)
        for solid in self.solids:
            if solid.right - camera_x < -TILE_SIZE or solid.left - camera_x > SCREEN_WIDTH:
                continue
            x = solid.x - camera_x
            y = solid.y
            row = solid.y // TILE_SIZE
            color = PIPE_GREEN if row < self.ground_row else GROUND_BROWN
            pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 1)

        for block in self.blocks:
            block.draw(surface, camera_x)

        for coin in self.coins:
            coin.draw(surface, camera_x)

        # flagpole
        pole_x = self.flag_rect.x - camera_x
        pygame.draw.rect(surface, POLE_GRAY, (pole_x, self.flag_rect.y, 6, self.flag_rect.height))
        pygame.draw.polygon(surface, FLAG_GREEN, [
            (pole_x + 6, self.flag_rect.y + 6),
            (pole_x + 6, self.flag_rect.y + 30),
            (pole_x - 26, self.flag_rect.y + 18),
        ])


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Python Bros")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arial", 48, bold=True)
        self.font_med = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)

        self.level_index = 0
        self.score = 0
        self.coin_count = 0
        self.lives = 3
        self.state = STATE_START
        self.camera_x = 0
        self.level = None
        self.player = None
        self.level_complete_timer = 0
        self._load_level(self.level_index)

    def _load_level(self, index):
        self.level = Level(LEVELS[index])
        self.player = Player(self.level.spawn_x, self.level.spawn_y)
        self.camera_x = 0

    def reset_game(self):
        self.level_index = 0
        self.score = 0
        self.coin_count = 0
        self.lives = 3
        self._load_level(0)
        self.state = STATE_PLAYING

    def kill_player(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
        else:
            self._load_level(self.level_index)

    def next_level(self):
        self.level_index += 1
        if self.level_index >= len(LEVELS):
            self.state = STATE_WIN
        else:
            self._load_level(self.level_index)
            self.state = STATE_PLAYING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.state in (STATE_START, STATE_GAME_OVER, STATE_WIN):
                        self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update_playing(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        solids = self.level.all_solids()
        collisions = self.player.update(solids)

        # hitting a question/brick block from below
        if collisions["top"]:
            for block in self.level.blocks:
                if block.rect.collidepoint(self.player.rect.centerx, self.player.rect.top - 1):
                    if block.hit_from_below():
                        self.score += 200
                        self.coin_count += 1

        # coin pickups
        for coin in self.level.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.coin_count += 1
                self.score += 100

        # goombas
        for goomba in self.level.goombas:
            goomba.update(solids)
            if not goomba.alive:
                continue
            if self.player.rect.colliderect(goomba.rect):
                falling_onto_top = (self.player.vel_y > 0 and
                                     self.player.rect.bottom - goomba.rect.top < 16)
                if falling_onto_top:
                    goomba.squish()
                    self.score += 100
                    self.player.vel_y = -10  # bounce
                else:
                    if self.player.take_hit():
                        self.kill_player()
                        return

        # fell into a pit
        if self.player.rect.top > SCREEN_HEIGHT + 200:
            self.kill_player()
            return

        # reached the flag
        if self.player.rect.colliderect(self.level.flag_rect.inflate(20, 0)):
            self.state = STATE_LEVEL_COMPLETE
            self.level_complete_timer = 90
            self.score += 500

        # camera follows player, clamped to level bounds
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(target_x, self.level.width_px - SCREEN_WIDTH))

    def update(self):
        if self.state == STATE_PLAYING:
            self.update_playing()
        elif self.state == STATE_LEVEL_COMPLETE:
            self.level_complete_timer -= 1
            if self.level_complete_timer <= 0:
                self.next_level()

    def draw_hud(self):
        score_text = self.font_small.render(f"SCORE {self.score:06d}", True, WHITE)
        coin_text = self.font_small.render(f"COINS x{self.coin_count:02d}", True, WHITE)
        lives_text = self.font_small.render(f"LIVES x{self.lives}", True, WHITE)
        level_text = self.font_small.render(self.level.data["name"], True, WHITE)
        self.screen.blit(score_text, (20, 15))
        self.screen.blit(coin_text, (220, 15))
        self.screen.blit(lives_text, (400, 15))
        self.screen.blit(level_text, (SCREEN_WIDTH - 220, 15))

    def draw_center_text(self, lines, y_start=200):
        y = y_start
        for text, font, color in lines:
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(surf, rect)
            y += rect.height + 10

    def draw(self):
        if self.state == STATE_START:
            self.screen.fill(SKY_BLUE)
            self.draw_center_text([
                ("SUPER PYTHON BROS", self.font_big, WHITE),
                ("Arrow keys / A-D to move, SPACE or UP to jump", self.font_small, WHITE),
                ("Stomp Goombas, collect coins, reach the flag!", self.font_small, WHITE),
                ("Press ENTER to start", self.font_med, GOLD),
            ])
        elif self.state in (STATE_PLAYING, STATE_LEVEL_COMPLETE):
            self.level.draw_background(self.screen, self.camera_x)
            for goomba in self.level.goombas:
                goomba.draw(self.screen, self.camera_x)
            self.player.draw(self.screen, self.camera_x)
            self.draw_hud()
            if self.state == STATE_LEVEL_COMPLETE:
                self.draw_center_text([
                    ("LEVEL COMPLETE!", self.font_big, GOLD),
                ], y_start=150)
        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            self.draw_center_text([
                ("GAME OVER", self.font_big, BRICK_RED),
                (f"Final Score: {self.score}", self.font_med, WHITE),
                ("Press ENTER to try again", self.font_small, WHITE),
            ])
        elif self.state == STATE_WIN:
            self.screen.fill(SKY_BLUE)
            self.draw_center_text([
                ("YOU WIN!", self.font_big, GOLD),
                (f"Final Score: {self.score}", self.font_med, WHITE),
                ("Press ENTER to play again", self.font_small, WHITE),
            ])

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


def main():
    Game().run()


if __name__ == "__main__":
    main()
