from ursina import *
from game.enemy import Enemy
from game.player import create_player
from game.dungeon_generator import create_dungeon_entities
from game.manual_dungeon_layout import dungeon_layout
from pathlib import Path
import os

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
        self.wave = 1
        self.enemies = []
        self.cell_size = cell_size

    def spawn_enemies(self):
        enemy_count = self.wave * 2
        exclusion_radius = 1  # Reduced radius to allow closer spawns

        # Extract only the (x, z) coordinates from floor_positions
        valid_floor_positions = [(pos[0], pos[2]) for pos in floor_positions]

        if not valid_floor_positions:
            print("No valid positions to spawn enemies.")
            return

        enemy_count = min(enemy_count, len(valid_floor_positions))
        selected_positions = random.sample(valid_floor_positions, enemy_count)

        for (x, z) in selected_positions:
            spawn_x = x  # x-coordinate from floor position
            spawn_z = z  # z-coordinate from floor position
            enemy_position = (spawn_x, 1.1, spawn_z)  # Y-position set to 1.1 for enemy height
            enemy = Enemy(
                player=player,
                game=self,
                position=enemy_position,
                texture=enemy_texture  # Pass the loaded texture
            )
            enemy.enabled = True
            enemy.visible = True
            self.enemies.append(enemy)

game = Game()
game.spawn_enemies()

# Display the score and wave information
score_text = Text(
    text=f'Score: {game.score}',
    position=(-0.85, 0.4),
    scale=2,
    color=color.white,
    parent=camera.ui
)
wave_text = Text(
    text=f'Wave: {game.wave}',
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

# Print the current working directory to debug the file path issue
print(f"Current working directory: {os.getcwd()}")

# Define the path to the shaders relative to the working directory
vertex_shader_path = Path('assets/shaders/bloom_vertex.glsl')
fragment_shader_path = Path('assets/shaders/bloom_fragment.glsl')

# Check if the files exist before attempting to read them
if not vertex_shader_path.is_file():
    print(f"Error: Vertex shader file not found at {vertex_shader_path}")
if not fragment_shader_path.is_file():
    print(f"Error: Fragment shader file not found at {fragment_shader_path}")

# Attempt to load the shaders if they exist
if vertex_shader_path.is_file() and fragment_shader_path.is_file():
    bloom_shader = Shader(
        language=Shader.GLSL,
        vertex=vertex_shader_path.read_text(),
        fragment=fragment_shader_path.read_text()
    )

    # Apply the shader to the camera
    camera.shader = bloom_shader
else:
    print("Shader files not found. Ensure the paths are correct.")

# Print light details for debugging
print(f"Ambient Light: {ambient_light}, Directional Light: {directional_light}")

# If nothing changes, try force-enabling shadow and lighting settings
for entity in scene.entities:
    if hasattr(entity, 'cast_shadows'):
        entity.cast_shadows = True

    if hasattr(entity, 'receive_shadows'):
        entity.receive_shadows = True

frame_index = 0
frame_timer = 0
frame_delay = 0.3

def update():
    # Update health, score, and wave displays
    player.health_text.text = f'Health: {player.health}'
    score_text.text = f'Score: {game.score}'
    wave_text.text = f'Wave: {game.wave}'

    # Update torch frames and facing direction
    global frame_index, frame_timer
    frame_timer += time.dt  # Accumulate time

    if frame_timer >= frame_delay:
        frame_index = (frame_index + 1) % len(torch_frames)
        frame_timer = 0  # Reset the timer

    # Update each torch's texture and make them face the player
    for torch in torches:  # No tuple unpacking needed, just loop through torches
        torch.texture = torch_frames[frame_index]  # Cycle through the frames
        # Make the torch face the player's current position
        player_position = Vec3(player.position.x, torch.position.y, player.position.z)  # Only track X and Z axis
        torch.look_at(player_position)

    # Remove disabled enemies
    game.enemies = [enemy for enemy in game.enemies if enemy.enabled]

    # Check if all enemies are defeated
    if not game.enemies:
        game.wave += 1
        game.spawn_enemies()



app.run()
