# Importing installed modules
import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)  # Convert position tuple to a mutable list
        self.size = size
        self.velocity = [0, 0]  # Initial velocity of the entity
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        self.action = ""  # Current action of the entity
        self.flip = False  # Flag to indicate horizontal flipping of the entity
        self.set_action("idle")  # Set initial action

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )

        # Horizontal movement collision detection and resolution
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        # Vertical movement collision detection and resolution
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y

        # Horizontal flipping based on movement direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        # Apply gravity and check for collisions with ground
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

        # Update animation frame
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # Blit the entity's current animation frame onto the surface
        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (
                self.pos[0] - offset[0],
                self.pos[1] - offset[1],
            ),
        )


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0  # Time spent in the air
        self.jumps = 1  # Remaining number of jumps

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        # Check for falling off the screen
        if self.air_time > 120:
            self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead = 1

        # Increment air time and reset jumps on landing
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1

        # Set player action based on movement and air time
        if self.air_time > 4:
            self.set_action("jump")
        elif movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

    def jump(self):
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5  # Reset air time on jump
