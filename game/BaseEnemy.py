from ursina import *
import time
import math

class BaseEnemy(Entity):
    def __init__(self, player, position=(0, 0, 0), texture=None, **kwargs):
        super().__init__(position=position, texture=texture, **kwargs)
        self.player = player
        self.health = 100
        self.speed = 2.5
        self.attack_range = 1.5
        self.attack_damage = 10
        self.attack_cooldown = 1.5
        self.last_attack_time = 0
        self.gravity = -9.81
        self.velocity_y = 0
        self.collider = BoxCollider(self, center=Vec3(0, self.scale_y / 2, 0), size=self.scale)

    def update(self):
        self.velocity_y += self.gravity * time.dt
        self.position += Vec3(0, self.velocity_y * time.dt, 0)
        if self.position.y < self.scale_y / 2:
            self.position = Vec3(self.position.x, self.scale_y / 2, self.position.z)
            self.velocity_y = 0
        self.move_towards_player()

    def move_towards_player(self):
        direction = (self.player.position - self.position).normalized()
        direction.y = 0
        distance_to_player = distance_xz(self.position, self.player.position)
        if distance_to_player > self.attack_range:
            self.position += direction * self.speed * time.dt
        else:
            self.attack_player()

    def attack_player(self):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.player.reduce_health(self.attack_damage)
            self.last_attack_time = current_time
            print(f"Enemy attacked player. Player health: {self.player.health}")

    def take_damage(self, amount):
        self.health -= amount
        print(f"Enemy took {amount} damage. Remaining health: {self.health}")
        if self.health <= 0:
            self.die()

    def die(self):
        print(f"Enemy at {self.position} died.")
        self.enabled = False
        destroy(self)

def distance_xz(pos1, pos2):
    return math.hypot(pos2.x - pos1.x, pos2.z - pos1.z)
