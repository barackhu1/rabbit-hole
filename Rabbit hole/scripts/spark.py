# Importing built-in modules
import math

# Importing installed modules
import pygame


class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)  # Convert position tuple to a mutable list
        self.angle = angle  # Set the angle of movement
        self.speed = speed  # Set the initial speed

    def update(self):
        # Update position based on current angle and speed
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        # Gradually decrease speed over time
        self.speed = max(0, self.speed - 0.1)

        # Return True if speed is zero (spark should be removed)
        return not self.speed

    def render(self, surf, offset=(0, 0)):
        # Calculate points to draw the spark's shape based on its position, angle, and speed
        render_points = [
            (
                self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
                self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5
                - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle + math.pi) * self.speed * 3
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi) * self.speed * 3
                - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5
                - offset[0],
                self.pos[1]
                + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5
                - offset[1],
            ),
        ]

        # Draw a polygon representing the spark on the surface
        pygame.draw.polygon(surf, (255, 255, 255), render_points)
