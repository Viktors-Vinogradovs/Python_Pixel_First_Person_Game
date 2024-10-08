from ursina import *
from game.player import create_player
from game.dungeon_build import create_dungeon_entities
from game.manual_dungeon_layout import dungeon_layout
import time

from game.simple_2d_enemy import SimpleSpriteEnemy

app = Ursina()

# Load textures
wall_texture = load_texture('assets/textures/wall.png')
floor_texture = load_texture('assets/textures/floor2.png')
roof_texture = load_texture('assets/textures/roof4.png')
torch_frames = [load_texture(f'assets/textures/torch_frame_{i}.png') for i in range(1, 4)]

hands_texture = load_texture('assets/textures/weapon1.png')
enemy_texture = load_texture('assets/textures/enemy.png')

# Set parameters
cell_size = 2

# Initialize frame-related variables for torch animation
frame_index = 0
frame_timer = 0
frame_delay = 0.3  # Time between torch frame updates

# Find player start position from layout
player_start_x = None
player_start_y = None

for y, row in enumerate(dungeon_layout):
    for x, tile in enumerate(row):
        if tile == 4:  # '4' represents the player start
            player_start_x, player_start_y = x, y
            dungeon_layout[y][x] = 1
            break
    if player_start_x is not None:
        break

if player_start_x is None or player_start_y is None:
    print("Error: Player start position not found in dungeon layout!")
    application.quit()

# Generate dungeon entities
dungeon_entities, floor_positions, torches = create_dungeon_entities(
    dungeon_layout,
    wall_texture=wall_texture,
    floor_texture=floor_texture,
    roof_texture=roof_texture,
    torch_frames=torch_frames,
    cell_size=2,
    floor_tile_size=2,
    debug_mode=False
)

# Fog and lighting settings
scene.fog_density = 0.05
scene.fog_color = color.rgb(0, 0, 0)
ambient_light = AmbientLight(color=color.rgb(10, 10, 10))
ambient_light.parent = scene
directional_light = DirectionalLight()
directional_light.color = color.rgb(100, 100, 100)
directional_light.direction = Vec3(0, -1, -1)
directional_light.parent = scene

# Create the player
player = create_player(hands_texture)
player.position = (player_start_x * cell_size, 0, player_start_y * cell_size)

# Game class definition
class Game(Entity):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.enemies = []
        self.cell_size = cell_size
        self.enemy_spawn_rate = 2
        self.spawn_interval = 5
        self.next_spawn_time = time.time() + self.spawn_interval
        self.survival_start_time = time.time()
        self.spawn_increment_time = 60
        self.last_increment_time = time.time()

    def spawn_enemies(self, count):
        valid_floor_positions = [(pos[0], pos[2]) for pos in floor_positions]

        if not valid_floor_positions:
            print("No valid positions to spawn enemies.")
            return

        enemy_count = min(count, len(valid_floor_positions))
        selected_positions = random.sample(valid_floor_positions, enemy_count)

        for (x, z) in selected_positions:
            enemy_position = (x, 1, z)
            enemy = SimpleSpriteEnemy(player=player, position=enemy_position, texture='enemy.png')
            enemy.enabled = True
            enemy.visible = True
            self.enemies.append(enemy)

    def update_spawn_logic(self):
        current_time = time.time()
        if current_time >= self.next_spawn_time:
            self.spawn_enemies(self.enemy_spawn_rate)
            self.next_spawn_time = current_time + self.spawn_interval
        if current_time - self.last_increment_time >= self.spawn_increment_time:
            self.enemy_spawn_rate += 2
            self.last_increment_time = current_time

    def update_survival_time(self):
        return int(time.time() - self.survival_start_time)

game = Game()
game.spawn_enemies(game.enemy_spawn_rate)

# UI text for score and survival time
score_text = Text(text=f'Score: {game.score}', position=(-0.85, 0.4), scale=2, color=color.white, parent=camera.ui)
survival_time_text = Text(text='Survival Time: 0', position=(-0.85, 0.35), scale=2, color=color.white, parent=camera.ui)

# Update logic
def update():
    player.health_text.text = f'Health: {player.health}'
    score_text.text = f'Score: {game.score}'
    game.update_spawn_logic()
    survival_time_text.text = f'Survival Time: {game.update_survival_time()}s'

    # Update torch frames
    global frames
    for torch in torches:
        torch.texture = torch_frames[frame_index]
        player_position = Vec3(player.position.x, torch.position.y, player.position.z)
        torch.look_at(player_position)
    game.enemies = [enemy for enemy in game.enemies if enemy.enabled]

app.run()
