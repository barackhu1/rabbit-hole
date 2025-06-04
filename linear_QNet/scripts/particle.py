class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)  # Convert position tuple to a mutable list
        self.velocity = list(velocity)  # Convert velocity list to a mutable list
        self.animation = self.game.assets[
            "particle/" + p_type
        ].copy()  # Initialize particle animation
        self.animation.frame = frame  # Set initial animation frame

    def update(self):
        kill = False  # Flag to determine if the particle should be removed

        # Check if animation is done (particle should be removed)
        if self.animation.done:
            kill = True

        # Update particle's position based on velocity
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # Update particle animation
        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        # Get the current image of the particle from its animation
        img = self.animation.img()

        # Blit the particle's image onto the surface
        surf.blit(
            img,
            (
                self.pos[0] - offset[0] - img.get_width() // 2,
                self.pos[1] - offset[1] - img.get_height() // 2,
            ),
        )
