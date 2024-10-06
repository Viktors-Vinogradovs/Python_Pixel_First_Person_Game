from ursina import *
from game.enemy import Enemy
from game.player import create_player
from game.dungeon_generator import create_dungeon_entities
from game.manual_dungeon_layout import dungeon_layout
from pathlib import Path
import os
import time

app = Ursina()

# Load textures
wall_texture = load_texture('assets/textures/wall0.png')
floor_texture = load_texture('assets/textures/floor_texture.png')
roof_texture = load_texture('assets/textures/roof0.png')
torch_frames = [load_texture(f'assets/textures/torch_frame_{i}.png') for i in range(1, 4)]  # Assuming you have torch_frame_1.png to torch_frame_4.png

hands_texture = load_texture('assets/textures/arms_with_spear.png')
if not hands_texture:
    print("Error: Hands texture not found.")
    application.quit()

# Load enemy texture
enemy_texture = load_texture('assets/textures/enemy.png')
if not enemy_texture:
    print("Error: Enemy texture not found.")
    application.quit()

# Define parameters
cell_size = 2  # Adjust as needed

# Find player start position from layout (where '4' is in the layout)
player_start_x = None
player_start_y = None

for y, row in enumerate(dungeon_layout):
    for x, tile in enumerate(row):
        if tile == 4:  # '4' represents the player start
            player_start_x, player_start_y = x, y
            dungeon_layout[y][x] = 1  # Make sure it's treated as floor (1) now
            break
    if player_start_x is not None:
        break

if player_start_x is None or player_start_y is None:
    print("Error: Player start position not found in dungeon layout!")
    application.quit()

# Get the list of torches from the dungeon generation
dungeon_entities, floor_positions, torches = create_dungeon_entities(
    dungeon_layout,
    wall_texture=wall_texture,
    floor_texture=floor_texture,
    roof_texture=roof_texture,
    torch_frames=torch_frames,  # Use torch_frames instead of torch_texture
    cell_size=2,
    floor_tile_size=2,
    debug_mode=False
)

# Add fog to limit the player's visibility (optional)
scene.fog_density = 0.05  # Adjust the density of the fog
scene.fog_color = color.rgb(0, 0, 0)  # Set the fog to black to simulate darkness

# **New: Increase emissiveness (glow) for torch textures**
for torch in torches:
    for frame in torch_frames:
        frame.emissive = False

# Create the player
player = create_player(hands_texture)
player.position = (player_start_x * cell_size, -1, player_start_y * cell_size)  # Set player position from the layout

# Define the Game class
class Game(Entity):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.enemies = []
        self.cell_size = cell_size
        self.enemy_spawn_rate = 2  # Initial number of enemies to spawn
        self.spawn_interval = 5  # Seconds between enemy spawns
        self.next_spawn_time = time.time() + self.spawn_interval  # Track next spawn time
        self.survival_start_time = time.time()  # Start time of survival
        self.spawn_increment_time = 60  # Time after which spawn rate increases
        self.last_increment_time = time.time()  # Time tracking for spawn rate increment

    def spawn_enemies(self, count):
        valid_floor_positions = [(pos[0], pos[2]) for pos in floor_positions]

        if not valid_floor_positions:
            print("No valid positions to spawn enemies.")
            return

        enemy_count = min(count, len(valid_floor_positions))
        selected_positions = random.sample(valid_floor_positions, enemy_count)

        for (x, z) in selected_positions:
            enemy_position = (x, 1.1, z)  # Y-position set to 1.1 for enemy height
            enemy = Enemy(
                player=player,
                game=self,
                position=enemy_position,
                texture=enemy_texture  # Pass the loaded texture
            )
            enemy.enabled = True
            enemy.visible = True
            self.enemies.append(enemy)

    def update_spawn_logic(self):
        current_time = time.time()

        # Check if it's time to spawn more enemies
        if current_time >= self.next_spawn_time:
            self.spawn_enemies(self.enemy_spawn_rate)
            self.next_spawn_time = current_time + self.spawn_interval  # Set next spawn time

        # Increase enemy spawn rate every minute
        if current_time - self.last_increment_time >= self.spawn_increment_time:
            self.enemy_spawn_rate += 2  # Increase the spawn rate every minute
            self.last_increment_time = current_time  # Reset the timer for the next increment

    def update_survival_time(self):
        return int(time.time() - self.survival_start_time)  # Return total survival time

game = Game()
game.spawn_enemies(game.enemy_spawn_rate)  # Spawn initial enemies

# Display the score and survival time
score_text = Text(
    text=f'Score: {game.score}',
    position=(-0.85, 0.4),
    scale=2,
    color=color.white,
    parent=camera.ui
)

survival_time_text = Text(
    text='Survival Time: 0',
    position=(-0.85, 0.35),
    scale=2,
    color=color.white,
    parent=camera.ui
)

# Set a very dim ambient light to make the dungeon dark
ambient_light = AmbientLight(color=color.rgb(10, 10, 10))  # Very dim light
ambient_light.parent = scene

# Optional: Add a very dim directional light for soft lighting
directional_light = DirectionalLight()
directional_light.color = color.rgb(100, 100, 100)  # Very dim light
directional_light.direction = Vec3(0, -1, -1)
directional_light.parent = scene

frame_index = 0
frame_timer = 0
frame_delay = 0.3

def update():
    # Update health and score displays
    player.health_text.text = f'Health: {player.health}'
    score_text.text = f'Score: {game.score}'

    # Update enemy spawn logic
    game.update_spawn_logic()

    # Update survival time and display it
    survival_time = game.update_survival_time()
    survival_time_text.text = f'Survival Time: {survival_time}s'

    # Update torch frames and facing direction
    global frame_index, frame_timer
    frame_timer += time.dt  # Accumulate time

    if frame_timer >= frame_delay:
        frame_index = (frame_index + 1) % len(torch_frames)
        frame_timer = 0  # Reset the timer

    # Update each torch's texture and make them face the player
    for torch in torches:
        torch.texture = torch_frames[frame_index]
        player_position = Vec3(player.position.x, torch.position.y, player.position.z)  # Only track X and Z axis
        torch.look_at(player_position)

    # Remove disabled enemies
    game.enemies = [enemy for enemy in game.enemies if enemy.enabled]

app.run()
