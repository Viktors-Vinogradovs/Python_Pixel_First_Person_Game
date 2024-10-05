from ursina import *
from game.enemy import Enemy
from game.player import create_player
from game.dungeon_generator import create_dungeon_entities
from game.manual_dungeon_layout import dungeon_layout

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
    debug_mode=True
)



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

# Set a low-intensity ambient light so that textures on walls and enemies are visible
ambient_light = AmbientLight(color=color.rgb(40, 40, 40))  # Dim light but enough to see textures
ambient_light.parent = scene

# Add directional light for a dim directional effect
directional_light = DirectionalLight()
directional_light.color = color.rgb(60, 60, 60)  # Slightly brighter directional light
directional_light.direction = Vec3(0, -1, -1)
directional_light.parent = scene

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

    # Update each torch's texture and make them face the player in every frame
    for torch in torches:
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
