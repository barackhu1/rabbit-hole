# Importing built-in modules
import os

# Importing installed modules
import pygame

# Define the base image path
BASE_IMG_PATH = "game_data/assets/"


# Function to load an image from the specified path
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()  # Load the image
    img.set_colorkey((0, 0, 0))  # Set black color as transparent
    return img


# Function to load a sequence of images from the specified path
def load_images(path):
    images = []
    # Iterate over each image in the directory
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(
            load_image(path + "/" + img_name)
        )  # Load each image and append to the list
    return images


# Class for handling animations
class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images  # List of images for the animation
        self.loop = loop  # Whether the animation should loop
        self.img_duration = img_dur  # Duration of each frame
        self.done = False  # Flag to indicate if the animation is complete
        self.frame = 0  # Current frame index

    # Method to create a copy of the animation
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    # Method to update the animation frame
    def update(self):
        if self.loop:
            # Increment frame index and loop back if necessary
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            # Increment frame index until the end of animation
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True  # Mark animation as done when it reaches the end

    # Method to get the current frame image
    def img(self):
        return self.images[
            int(self.frame / self.img_duration)
        ]  # Return the current frame image
