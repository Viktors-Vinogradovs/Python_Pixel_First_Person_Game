from ursina import *
import time
import math

class Enemy(Entity):
    def __init__(self, player, game, position=(0, 0, 0), texture=None):
        super().__init__()
        self.player = player
        self.game = game
        self.health = 100
        self.speed = 2.5  # Adjust as needed
        self.attack_range = 1.5
        self.attack_damage = 10
        self.attack_cooldown = 1.5
        self.last_attack_time = 0

        # Set up the model and texture as a thin cube
        self.model = 'cube'
        self.texture = texture
        self.color = color.white
        self.scale = (1, 2, 0.05)  # Thin along Z-axis to make it almost like a plane
        self.position = Vec3(position[0], self.scale_y / 2, position[2])

        # Set up the collider
        self.collider = BoxCollider(
            self,
            center=Vec3(0, self.scale_y / 2, 0),
            size=self.scale
        )

        # Add a minimum separation distance from walls
        self.wall_separation = 0.5  # Distance from walls to avoid overlap

    def update(self):
        self.move_towards_player()
        self.face_player()

    def move_towards_player(self):
        # Calculate direction towards player
        direction = (self.player.position - self.position).normalized()
        direction.y = 0  # Ignore vertical difference

        # Move towards player if beyond attack range
        distance = distance_xz(self.position, self.player.position)
        if distance > self.attack_range:
            # Cast rays to check for walls ahead and to the sides
            if self.detect_wall_ahead(direction):
                # Try moving left or right to avoid the wall
                if not self.check_collision(self.left_direction(direction)):
                    self.position += self.left_direction(direction) * self.speed * time.dt
                   # print(f"Enemy at {self.position} is moving left to avoid wall.")
                elif not self.check_collision(self.right_direction(direction)):
                    self.position += self.right_direction(direction) * self.speed * time.dt
                   # print(f"Enemy at {self.position} is moving right to avoid wall.")
                else:
                    # If both left and right are blocked, try sliding along the wall
                    self.slide_along_wall(direction)
            else:
                # No wall detected, move directly towards the player
                self.position += direction * self.speed * time.dt
        else:
            self.attack()

    def face_player(self):
        # Calculate direction from enemy to player on the XZ plane (ignoring Y axis)
        direction = self.player.position - self.position
        direction.y = 0  # Keep the enemy on the same horizontal plane

        # Use atan2 to calculate the angle between the enemy and the player
        angle = math.degrees(math.atan2(direction.x, direction.z))

        # Rotate the enemy to face the player along the Y-axis
        self.rotation_y = angle

    def detect_wall_ahead(self, direction):
        # Cast a ray in front of the enemy to detect walls
        hit_info = raycast(
            origin=self.world_position + Vec3(0, self.scale_y / 2, 0),
            direction=direction,
            distance=1.0,  # Adjust distance based on how close you want the enemy to react
            ignore=(self, self.player)
        )
        return hit_info.hit  # Return True if a wall is detected ahead

    def left_direction(self, direction):
        # Calculate a direction to the left (90 degrees)
        return Vec3(-direction.z, 0, direction.x).normalized()

    def right_direction(self, direction):
        # Calculate a direction to the right (90 degrees)
        return Vec3(direction.z, 0, -direction.x).normalized()

    def slide_along_wall(self, direction):
        # Try sliding along the wall by moving along its surface
        # If the enemy detects a wall ahead, adjust its movement to "slide" along the wall
        slide_direction = Vec3(direction.x, 0, 0) if abs(direction.x) > abs(direction.z) else Vec3(0, 0, direction.z)
        self.position += slide_direction * self.speed * time.dt
        print(f"Enemy at {self.position} is sliding along the wall.")

    def check_collision(self, move):
        # Predict new position
        new_position = self.position + move
        # Cast a box in the move direction
        hit_info = boxcast(
            self.world_position + Vec3(0, self.scale_y / 2, 0),
            direction=move.normalized(),
            distance=move.length(),
            thickness=(self.scale_x * 0.9, self.scale_z * 0.9),
            ignore=(self, self.player)
        )
        return hit_info.hit  # Return True if collision detected

    def attack(self):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # Reduce player's health
            self.player.reduce_health(self.attack_damage)
            self.last_attack_time = current_time
            print(f"Enemy at {self.position} attacked player. Player health: {self.player.health}")

    def take_damage(self, amount):
        self.health -= amount
        print(f"Enemy at {self.position} took {amount} damage. Remaining health: {self.health}")
        if self.health <= 0:
            self.die()

    def die(self):
        print(f"Enemy at {self.position} died.")
        self.enabled = False
        if self in self.game.enemies:
            self.game.enemies.remove(self)
            print("Enemy removed from game.enemies")
        else:
            print("Enemy was not found in game.enemies")
        destroy(self)
        self.game.score += 10

def distance_xz(pos1, pos2):
    # Calculate the distance between two positions on the XZ plane
    return math.hypot(pos2.x - pos1.x, pos2.z - pos1.z)
