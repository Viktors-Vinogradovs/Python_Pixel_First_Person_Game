from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import (
    Text, camera, application, color, Entity, load_texture, held_keys, raycast, Vec3, invoke, time, sin, cos
)

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
        self.attack_damage = 50  # Damage per attack
        self.attack_range = 5.0  # Range of melee attack
        self.attack_cooldown = 0.5  # Cooldown in seconds
        self.last_attack_time = 0  # Time of the last attack

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

        # Load the hands texture
        hands_texture_path = 'assets/textures/arms_with_spear.png'  # Adjust path if necessary
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
            position=(0.6, -0.6),
            origin=(0.1, -0.1),
            rotation_z=0,
            color=color.white
        )

        # Variables for camera bobbing effect
        self.bobbing_amount = 0.05  # How much the camera should move up/down
        self.bob_speed = 15  # Speed of the bobbing effect
        self.bob_phase = 0  # Used to calculate the bobbing phase over time
        self.original_camera_y = camera.position.y  # Store the original camera Y position

    def reduce_health(self, amount):
        self.health -= amount
        print(f"Player took {amount} damage. Remaining health: {self.health}")
        if self.health <= 0:
            self.health = 0
            print("Game Over!")
            self.game_over()
        # Update the health display
        self.health_text.text = f'Health: {self.health}'

    def game_over(self):
        # Display Game Over message
        self.game_over_text = Text(
            text='Game Over!',
            origin=(0, 0),
            scale=3,
            color=color.red,
            background=True
        )
        # Pause the game
        application.pause()

    def input(self, key):
        super().input(key)
        if key == 'left mouse down':
            self.perform_attack()

    def perform_attack(self):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            self.animate_attack()
            self.attack()

    def animate_attack(self):
        original_rotation = self.hands.rotation_z
        self.hands.animate_rotation_z(-20, duration=0.1)
        invoke(self.hands.animate_rotation_z, original_rotation, duration=0.1, delay=0.1)

    def attack(self):
        attack_origin = self.position + Vec3(0, self.height * 0.5, 0)  # Start from player's chest height
        attack_direction = self.forward

        # Perform a raycast to detect enemies within attack range
        hit_info = raycast(
            origin=attack_origin,
            direction=attack_direction,
            distance=self.attack_range,
            ignore=(self,)
        )

        if hit_info.hit:
            hit_entity = hit_info.entity
            if hasattr(hit_entity, 'take_damage'):
                # Calculate knockback direction
                knockback_direction = hit_entity.position - self.position

                # Pass damage and knockback information to the enemy
                hit_entity.take_damage(self.attack_damage, knockback_direction, self.knockback_force)

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

# Ensure this function is at the module level
def create_player(texture):
    player = Player(texture)
    return player
