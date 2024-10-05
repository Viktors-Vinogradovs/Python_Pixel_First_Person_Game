# game/environment.py
from ursina import *
import random

def create_environment(texture):
    # Create the ground
    ground = Entity(
        model='plane',
        texture=texture,
        collider='box',
        scale=(100, 1, 100),
        texture_scale=(100, 100)
    )

    # Add environment objects
    for _ in range(10):
        Entity(
            model='cube',
            texture=texture,
            collider='box',
            scale=2,
            position=(random.uniform(-10, 10), 1, random.uniform(-10, 10))
        )

    # Add lighting
    DirectionalLight().look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgb(100, 100, 100))
