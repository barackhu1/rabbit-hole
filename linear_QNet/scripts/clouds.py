# Importing built-in modules
import random


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)  # Convert position tuple to a mutable list
        self.img = img  # Image representing the cloud
        self.speed = speed  # Horizontal speed of the cloud
        self.depth = depth  # Depth of the cloud, affecting movement and rendering

    def update(self):
        self.pos[0] += self.speed  # Move the cloud horizontally

    def render(self, surf, offset=(0, 0)):
        # Calculate the position to render the cloud with parallax effect
        render_pos = (
            self.pos[0] - offset[0] * self.depth,
            self.pos[1] - offset[1] * self.depth,
        )

        # Blit the cloud's image onto the surface with parallax effect
        surf.blit(
            self.img,
            (
                render_pos[0] % (surf.get_width() + self.img.get_width())
                - self.img.get_width(),
                render_pos[1] % (surf.get_height() + self.img.get_height())
                - self.img.get_height(),
            ),
        )


class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []  # List to hold Cloud objects

        # Generate clouds with random positions, images, speeds, and depths
        for i in range(count):
            self.clouds.append(
                Cloud(
                    (
                        random.random() * 99999,
                        random.random() * 99999,
                    ),  # Random position
                    random.choice(cloud_images),  # Random cloud image
                    random.random() * 0.05 + 0.05,  # Random speed between 0.05 and 0.1
                    random.random() * 0.6 + 0.2,  # Random depth between 0.2 and 0.8
                )
            )

        # Sort clouds based on depth for proper rendering order
        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()  # Update each cloud's position

    def render(self, surf, offset=(0, 0)):
        # Render each cloud on the surface with the specified offset
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
