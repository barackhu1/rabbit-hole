# Importing built-in modules
import sys
import os
import random
import math

# Importing installed modules
import pygame

# Imporing other modules
from scripts.utils import load_image, load_images, Animation
from scripts.entity import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class GameAI:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("rabbithole beta")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface(
            (320, 240), pygame.SRCALPHA
        )  # Create a transparent display surface
        self.display_2 = pygame.Surface(
            (320, 240)
        )  # Create a secondary display surface

        self.clock = pygame.time.Clock()

        # Load assets
        self.assets = {
            "dirt": load_images("tiles/dirt"),
            "background": load_image("background/background.png"),
            "clouds": load_images("clouds"),
            "player": load_image("entity/Roby.png"),
            "player/idle": Animation(load_images("entity/idle"), img_dur=6),
            "player/run": Animation(load_images("entity/run"), img_dur=4),
            "player/jump": Animation(load_images("entity/jump")),
            "decor": load_images("tiles/decor"),
            "particle/leaf": Animation(
                load_images("particles/leaf"), img_dur=12, loop=False
            ),
            "obstacle": load_images("tiles/obstacle"),
            "escape": load_images("tiles/escape"),
            "particle/particle": Animation(
                load_images("particles/particle"), img_dur=6, loop=False
            ),
        }

        self.clouds = Clouds(self.assets["clouds"])  # Create clouds object

        self.player = Player(self, (50, 50), (9, 20))  # Create player object

        self.tilemap = Tilemap(self, tile_size=20)  # Create tilemap object

        self.movement = [0, 0, 0]

        self.level = 0
        self.load_level(self.level)  # Load initial level

        self.screenshake = 0  # Initialize screenshake value

        self.distance = 0  # Initialize distance value between character and player
        self.no_tile_right = 0
        self.no_tile_left = 0
        self.spike_warning_right = 0
        self.spike_warning_left = 0

    # Load level from JSON file
    def load_level(self, map_id):
        self.tilemap.load("game_data/maps/" + str(map_id) + ".json")

        # Set player position to spawner position
        for spawner in self.tilemap.extract([("spawner", 0)]):
            self.player.pos = spawner["pos"]
            self.player.air_time = 0

        # Extract leaf spawner positions
        self.leaf_spawner = []
        for tree in self.tilemap.extract([("decor", 0)], keep=True):
            self.leaf_spawner.append(
                pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            )

        # Extract spike positions
        self.spikes = []
        for spike in self.tilemap.extract([("obstacle", 0)], keep=True):
            self.spikes.append(pygame.Rect(spike["pos"][0], spike["pos"][1], 10, 13))

        # Extract escape point position
        escape = self.tilemap.extract([("escape", 0)], keep=True)[0]
        self.escape_point = pygame.Rect(escape["pos"][0], escape["pos"][1], 14, 12)

        # Initialize lists for particles and sparks
        self.particles = []
        self.sparks = []

        # Scrolling, death handling parameters
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
        self.completed = False

        # Parameters for timer
        self.countdown = 20
        self.last_count = pygame.time.get_ticks()

    def play_step(self, action=[0, 0, 0]):
        self.distance = math.sqrt(
            (self.player.pos[0] - self.escape_point.left) ** 2
            + (self.player.pos[1] - self.escape_point.top) ** 2
        )
        for y in range(0, 61, 20):
            self.no_tile_right = self.tilemap.solid_check(
                [
                    self.player.pos[0] + self.player.size[0] // 2 + 20,
                    self.player.pos[1] + self.player.size[1] + y,
                ]
            )
            if self.no_tile_right:
                break

        for y in range(0, 61, 20):
            self.no_tile_left = self.tilemap.solid_check(
                [
                    self.player.pos[0] + self.player.size[0] // 2 - 20,
                    self.player.pos[1] + self.player.size[1] + y,
                ]
            )
            if self.no_tile_left:
                break

        self.spike_warning_right = [
            spike_rect
            for spike_rect in self.spikes
            if self.player.rect().move(20, 0).colliderect(spike_rect)
        ]

        self.spike_warning_left = [
            spike_rect
            for spike_rect in self.spikes
            if self.player.rect().move(-20, 0).colliderect(spike_rect)
        ]

        self.movement = action
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear display surfaces
        self.display.fill((0, 0, 0, 0))
        self.display_2.blit(self.assets["background"], (0, 0))

        # Screenshake update
        self.screenshake = max(0, self.screenshake - 1)

        # Calculate scrolling
        self.scroll[0] += (
            self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]
        ) / 30

        self.scroll[1] += (
            self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]
        ) / 30

        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        # Generate leaf particles
        for rect in self.leaf_spawner:
            if random.random() * 35555 < rect.width * rect.height:
                pos = (
                    rect.x + random.random() * rect.width,
                    rect.y + random.random() * rect.height,
                )
                self.particles.append(
                    Particle(
                        self,
                        "leaf",
                        pos,
                        velocity=[-0.3, 0.4],
                        frame=random.randint(0, 20),
                    )
                )

        # Clouds rendering
        self.clouds.update()
        self.clouds.render(self.display_2, offset=render_scroll)

        # Tilemap rendering
        self.tilemap.render(self.display, offset=render_scroll)

        # Spike collision handling
        spikes_collisions = [
            spike_rect
            for spike_rect in self.spikes
            if self.player.rect().colliderect(spike_rect)
        ]
        if spikes_collisions and not self.dead:
            self.dead = 1
            self.screenshake = max(16, self.screenshake)
            for i in range(10):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.sparks.append(
                    Spark(
                        self.player.rect().center,
                        angle,
                        2 + random.random(),
                    )
                )
                self.particles.append(
                    Particle(
                        self,
                        "particle",
                        self.player.rect().center,
                        velocity=[
                            math.cos(angle + math.pi) * speed * 0.5,
                            math.sin(angle + math.pi) * speed * 0.5,
                        ],
                        frame=random.randint(0, 7),
                    )
                )

        # Update player
        if not self.dead and not self.completed:
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            self.player.jump() if self.movement[2] else None

        reward = 0

        if (
            action[2]
            and self.player.collisions["down"]
            and self.no_tile_right
            and self.player.air_time < 1
        ):
            reward += 10
        elif not self.no_tile_right and self.player.collisions["down"]:
            reward -= 5
        elif not self.no_tile_left and self.player.collisions["down"]:
            reward -= 5
        elif action[2]:
            reward -= 1

        if (
            self.spike_warning_right
            and action[2]
            and action[1] - action[0] < 0
            and self.player.collisions["down"]
        ):
            reward += 10
        elif self.spike_warning_left:
            reward -= 5
        elif self.spike_warning_right:
            reward -= 5

        if int(self.distance) == 200:
            reward += 5
        elif int(self.distance) == 100:
            reward += 10
        elif int(self.distance) == 60:
            reward += 20
        elif int(self.distance) == 30:
            reward += 40

        # Check if player is dead
        if self.dead:
            self.dead += 1
            reward -= 60
            if self.dead >= 10:
                self.transition = min(30, self.transition + 1)
            if self.dead > 40:
                # self.level = max(0, self.level - 1)
                self.load_level(self.level)

        # Check if player collides with escape point
        if self.player.rect().colliderect(self.escape_point):
            self.transition += 1
            if self.transition == 2:
                self.completed = True
                reward += 60
            if self.transition > 30:
                self.level = min(self.level + 1, len(os.listdir("game_data/maps")) - 1)
                self.load_level(self.level)
        if self.transition < 0:
            self.transition += 1

        # Create display silhouette
        display_mask = pygame.mask.from_surface(self.display)
        display_sillhouette = display_mask.to_surface(
            setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0)
        )
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.display_2.blit(display_sillhouette, offset)

        # Update and render sparks
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

        # Update and render particles
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=render_scroll)
            if particle.type == "leaf":
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

        # Blit display onto secondary display
        self.display_2.blit(self.display, (0, 0))

        # Display countdown timer
        font = pygame.font.SysFont("Times New Roman", 30)
        img = font.render(str(self.countdown), True, (120, 120, 120))
        self.display_2.blit(img, (10, 0))
        count_timer = pygame.time.get_ticks()
        if count_timer - self.last_count > 1000:
            if self.countdown:
                self.countdown -= 1
            else:
                reward -= 60
                self.dead = 10
            self.last_count = count_timer

        # Display transition effect
        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(
                transition_surf,
                (255, 255, 255),
                (self.display.get_width() // 2, self.display.get_height() // 2),
                (30 - abs(self.transition)) * 8,
            )
            transition_surf.set_colorkey((255, 255, 255))
            self.display_2.blit(transition_surf, (0, 0))

        # Apply screenshake effect
        screenshake_offset = (
            random.random() * self.screenshake - self.screenshake / 2,
            random.random() * self.screenshake - self.screenshake / 2,
        )
        self.screen.blit(
            pygame.transform.scale(self.display_2, self.screen.get_size()),
            screenshake_offset,
        )
        pygame.display.update()

        self.clock.tick(60)

        return reward, self.level, self.dead > 0
