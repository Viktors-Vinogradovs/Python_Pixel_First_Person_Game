from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import (
    Text, camera, application, color, Entity, load_texture, held_keys, raycast, Vec3, invoke, time, sin, cos
)

from game.BaseEnemy import BaseEnemy
from game.projectile import Projectile


class Player(FirstPersonController):
    def __init__(self, texture, **kwargs):
        super().__init__(
            model='cube',
            texture=texture,
            height=2,
            speed=5,
            jump_height=2,
            gravity=2,
            **kwargs
        )
        self.health = 100  # Initialize player's health
        self.attack_damage = 50  # Damage per melee attack
        self.attack_range = 5.0  # Range of melee attack
        self.attack_cooldown = 0.5  # Cooldown in seconds for melee
        self.last_attack_time = 0  # Time of the last attack

        # Weapon selection (1: Spear, 2: Projectile)
        self.weapon = 1  # Default to spear
        self.weapon_name_text = Text(
            text=f'Weapon: Spear',
            position=(-0.85, 0.5),
            scale=2,
            color=color.white,
            parent=camera.ui
        )

        # Knockback force
        self.knockback_force = 15  # You can adjust this value for stronger or weaker knockback

        # Create a health bar UI element
        self.health_text = Text(
            text=f'Health: {self.health}',
            position=(-0.85, 0.45),
            scale=2,
            color=color.white,
            parent=camera.ui
        )

        # Load the hands texture for the spear
        hands_texture_path = 'assets/textures/weapon1.png'
        self.hands_texture = load_texture(hands_texture_path)
        if not self.hands_texture:
            print(f"Error: Hands texture not found at '{hands_texture_path}'")
            application.quit()

        # Create the hands Entity (arms holding spear)
        self.hands = Entity(
            parent=camera.ui,
            model='quad',
            texture=texture,
            scale=(1, 1),
            position=(1, 1),
            origin=(0.4, -0.6),
            rotation_z=0,
            color=color.white
        )

        # Variables for camera bobbing effect
        self.bobbing_amount = 0.05  # How much the camera should move up/down
        self.bob_speed = 15  # Speed of the bobbing effect
        self.bob_phase = 0  # Used to calculate the bobbing phase over time
        self.original_camera_y = camera.position.y  # Store the original camera Y position

    def reduce_health(self, amount):
        """Reduce player's health when hit by an enemy."""
        self.health -= amount
        print(f"Player took {amount} damage. Remaining health: {self.health}")

        # Update the health display
        self.health_text.text = f'Health: {self.health}'

        # Check if player's health drops to zero or below
        if self.health <= 0:
            self.health = 0
            print("Player died. Game over.")
            self.game_over()

    def game_over(self):
        """Handle game over when player's health reaches zero."""
        # Display Game Over message
        game_over_text = Text(
            text='Game Over',
            origin=(0, 0),
            scale=3,
            color=color.red,
            background=True
        )
        # Pause the game
        application.pause()

    def perform_attack(self):
        """Player performs a melee attack."""
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            self.animate_attack()
            self.attack()

    def animate_attack(self):
        """Animate spear thrusting during attack."""
        original_rotation = self.hands.rotation_z
        self.hands.animate_rotation_z(-20, duration=0.1)
        invoke(self.hands.animate_rotation_z, original_rotation, duration=0.1, delay=0.1)

    def attack(self):
        """Player performs a melee attack with the spear."""
        print("Player is attacking with spear")

        # Adjust the attack origin to be at chest/weapon level
        attack_origin = self.position + Vec3(0, self.height * 0.8, 0)  # Adjust to player's head/weapon level
        attack_direction = self.forward  # Forward direction from the player

        # Perform a raycast to detect entities within attack range
        hit_info = raycast(
            origin=attack_origin,
            direction=attack_direction,
            distance=self.attack_range,
            ignore=(self,),  # Ignore the player itself
            debug=True  # Visualize the raycast line for debugging
        )

        # Check if we hit anything
        if hit_info.hit:
            print(f"Hit entity: {hit_info.entity}, Type: {type(hit_info.entity)}")

            # Ensure the hit entity is a valid enemy and can take damage
            if hasattr(hit_info.entity, 'take_damage'):
                print("Hit an enemy, dealing damage")

                # Capture enemy's position before applying damage
                enemy_position = hit_info.entity.position

                # Apply damage to the enemy
                hit_info.entity.take_damage(self.attack_damage)  # Apply damage to the enemy

                # Check if the enemy is still enabled before applying knockback
                if hit_info.entity.enabled:
                    knockback_direction = enemy_position - self.position  # Knockback direction away from player
                    hit_info.entity.apply_knockback(knockback_direction, self.knockback_force)
                else:
                    print("Enemy was destroyed before knockback could be applied")
            else:
                print("Hit entity is not an enemy")
        else:
            print("No hit detected")

    def update(self):
        super().update()

        # Apply camera bobbing effect when player is moving
        if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
            self.apply_camera_bob()
        else:
            # Reset camera position when not moving
            camera.position = Vec3(camera.position.x, self.original_camera_y, camera.position.z)

    def apply_camera_bob(self):
        """Applies a smooth camera bobbing effect based on player movement."""
        self.bob_phase += self.bob_speed * time.dt
        bobbing_offset_y = sin(self.bob_phase) * self.bobbing_amount

        # Apply camera bobbing
        camera.position = Vec3(
            camera.position.x,
            self.original_camera_y + bobbing_offset_y,
            camera.position.z
        )

        # Apply bobbing to hands entity to keep the hands synced with the camera bobbing
        self.hands.position = Vec3(
            0.7,  # X position of the hands
            -0.7 + bobbing_offset_y * 1,  # Y position of the hands, exaggerated bobbing
            0
        )

    def input(self, key):
        super().input(key)

        if key == 'left mouse down':
            if self.weapon == 1:
                self.perform_attack()  # Perform spear attack
            elif self.weapon == 2:
                self.fire_projectile()  # Fire projectile

        if key == '1':
            self.weapon = 1
            self.weapon_name_text.text = 'Weapon: Spear'
            print("Spear selected")

        if key == '2':
            self.weapon = 2
            self.weapon_name_text.text = 'Weapon: Projectile'
            print("Projectile selected")

    def fire_projectile(self):
        """Create and fire a projectile from the player."""
        direction = self.forward  # Fire in the forward direction of the player
        position = self.position + Vec3(0, 1, 0)  # Adjust for player height

        # Create a new projectile
        projectile = Projectile(position=position, direction=direction)
        print(f"Fired projectile from {position} in direction {direction}")


# Ensure this function is at the module level
def create_player(texture):
    player = Player(texture)
    return player
