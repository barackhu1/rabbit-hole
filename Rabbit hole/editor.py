# Importing built-in modules
import sys

# Importing installed modules
import pygame

# Importing other modules
from scripts.utils import load_images, load_image
from scripts.tilemap import Tilemap

# Define the render scale
RENDER_SCALE = 2.0


# Define the Editor class
class Editor:
    # Initialize the editor
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set window caption and create the main display surface
        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((640, 480))

        # Create the main display surface
        self.display = pygame.Surface((320, 240))

        # Create a clock to control the frame rate
        self.clock = pygame.time.Clock()

        # Load assets
        self.assets = {
            "dirt": load_images("tiles/dirt"),
            "decor": load_images("tiles/decor"),
            "obstacle": load_images("tiles/obstacle"),
            "spawner": load_images("tiles/spawner"),
            "escape": load_images("tiles/escape"),
        }

        # Initialize movement flags
        self.movement = [False, False, False, False]

        # Create a tilemap object
        self.tilemap = Tilemap(self, tile_size=20)

        # Load existing map if available
        try:
            self.tilemap.load("map.json")
        except FileNotFoundError:
            pass

        # Initialize scroll position
        self.scroll = [0, 0]

        # Initialize variables for tile selection
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        # Initialize variables for mouse interaction
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    # Run the editor
    def run(self):
        while True:
            # Clear the display
            self.display.fill((0, 0, 0))

            # Update scroll position based on movement flags
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Render the tilemap
            self.tilemap.render(self.display, offset=render_scroll)

            # Render the currently selected tile with transparency
            current_tile_img = self.assets[self.tile_list[self.tile_group]][
                self.tile_variant
            ].copy()
            current_tile_img.set_alpha(100)

            # Get mouse position
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (
                int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size),
            )

            # Render the currently selected tile at mouse position
            if self.ongrid:
                self.display.blit(
                    current_tile_img,
                    (
                        tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                        tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                    ),
                )
            else:
                self.display.blit(current_tile_img, mpos)

            # Handle left and right mouse clicks
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ";" + str(tile_pos[1])] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_pos,
                }
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]

            # Display the currently selected tile in the top left corner
            self.display.blit(current_tile_img, (5, 5))

            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append(
                                {
                                    "type": self.tile_list[self.tile_group],
                                    "variant": self.tile_variant,
                                    "pos": (
                                        mpos[0] + self.scroll[0],
                                        mpos[1] + self.scroll[1],
                                    ),
                                }
                            )
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                # Handle keyboard input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save("map.json")
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # Scale and blit the display surface to the screen
            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()

            # Control the frame rate
            self.clock.tick(60)


# Run the editor
Editor().run()
