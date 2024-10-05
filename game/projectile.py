# game/projectile.py
from ursina import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.enemy import Enemy

class Projectile(Entity):
    def __init__(self, position, direction, **kwargs):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.2,
            position=position,
            collider='sphere',
            **kwargs
        )
        self.direction = direction.normalized()
        self.speed = 20

    def update(self):
        self.position += self.direction * self.speed * time.dt
        # Destroy if out of range
        if distance(self.position, camera.position) > 50:
            destroy(self)

        # Check collision with enemies
        hit_info = self.intersects()
        if hit_info.hit:
            # Instead of isinstance, check if entity has 'take_damage' method
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(25)  # Damage the enemy
                destroy(self)
