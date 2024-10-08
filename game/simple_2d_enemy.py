from ursina import BoxCollider, Vec3, time, destroy
from game.BaseEnemy import BaseEnemy  # Ensure you are importing BaseEnemy

class SimpleSpriteEnemy(BaseEnemy):  # Make sure it inherits from BaseEnemy
    def __init__(self, player, position=(0, 0, 0), texture='assets/textures/enemy.png', **kwargs):
        super().__init__(player, position=position, texture=texture, **kwargs)
        self.model = 'quad'
        self.double_sided = True
        self.scale = Vec3(1.5, 2.5, 1)  # Adjust size

        # Add a BoxCollider specific to the sprite
        self.collider = BoxCollider(self, center=Vec3(0, self.scale_y / 2, 0), size=self.scale)

        # Enemy attributes
        self.health = 100
        self.knockback = 0  # Initialize knockback force
        self.knockback_direction = Vec3(0, 0, 0)  # Initialize knockback direction

    def take_damage(self, damage):
        """Handles the enemy taking damage."""
        self.health -= damage
        print(f"Enemy took {damage} damage. Remaining health: {self.health}")
        if self.health <= 0:
            self.die()

    def apply_knockback(self, knockback_direction, knockback_force):
        """Apply knockback to the enemy."""
        self.knockback = knockback_force
        self.knockback_direction = knockback_direction.normalized()

    def update(self):
        """Handles enemy movement and knockback."""
        super().update()  # Ensure the base update logic (like gravity) is executed

        # Apply knockback if any
        if self.knockback > 0:
            self.position += self.knockback_direction * self.knockback * time.dt
            self.knockback -= time.dt * 10  # Reduce knockback over time

        # Ensure the enemy continues moving toward the player after knockback wears off
        if self.knockback <= 0:
            self.move_towards_player()

        # Make the sprite face the player
        self.look_at_2d(self.player.position, 'y')

    def die(self):
        """Handle enemy death."""
        print(f"Enemy at {self.position} died.")
        destroy(self)
