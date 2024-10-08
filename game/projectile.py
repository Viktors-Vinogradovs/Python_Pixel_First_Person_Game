# game/projectile.py
from ursina import *
from typing import TYPE_CHECKING


class Projectile(Entity):
    def __init__(self, position, direction, **kwargs):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.2,
            position=position,
            collider='sphere',  # Ensures the projectile has a collider
            **kwargs
        )
        self.direction = direction.normalized()
        self.speed = 20  # Speed of the projectile

    def update(self):
        # Move the projectile in the given direction
        self.position += self.direction * self.speed * time.dt

        # Destroy the projectile if it is too far away from the camera/player
        if distance(self.position, camera.position) > 50:
            print(f"Projectile destroyed due to range limit.")
            destroy(self)
            return  # Prevent further execution after destruction

        # Check for collision with any entity
        hit_info = self.intersects()
        if hit_info.hit:
            print(f"Projectile hit entity: {hit_info.entity}, Type: {type(hit_info.entity)}")

            # Check if the hit entity has the 'take_damage' method (i.e., it's an enemy)
            if hasattr(hit_info.entity, 'take_damage') and hit_info.entity.enabled:
                print("Projectile hit an enemy! Applying damage...")
                hit_info.entity.take_damage(25)  # Apply 25 damage to the enemy
                destroy(self)
                return  # Prevent further execution after destruction
            else:
                print("Projectile hit something, but it's not an enemy.")
                # Optionally destroy the projectile if it hits something else
                destroy(self)
                return  # Prevent further execution after destruction
