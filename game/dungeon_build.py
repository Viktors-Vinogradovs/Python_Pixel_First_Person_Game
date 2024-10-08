from ursina import *
import random

# Function to generate the dungeon layout
def generate_dungeon(width, height, corridor_width=1, manual_layout=None):
    if manual_layout:
        return manual_layout, 1, 1
    if width % (corridor_width + 1) != 1:
        width += (corridor_width + 1) - (width % (corridor_width + 1))
    if height % (corridor_width + 1) != 1:
        height += (corridor_width + 1) - (height % (corridor_width + 1))
    dungeon = [[0 for _ in range(width)] for _ in range(height)]
    start_x = random.randrange(corridor_width, width, corridor_width + 1)
    start_y = random.randrange(corridor_width, height, corridor_width + 1)
    carve_out_area(dungeon, start_x, start_y, corridor_width)
    stack = [(start_x, start_y)]
    while stack:
        x, y = stack[-1]
        directions = []
        if x > corridor_width: directions.append((- (corridor_width + 1), 0))
        if x < width - (corridor_width + 1): directions.append((corridor_width + 1, 0))
        if y > corridor_width: directions.append((0, - (corridor_width + 1)))
        if y < height - (corridor_width + 1): directions.append((0, corridor_width + 1))
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if dungeon[ny][nx] == 0: neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            for i in range(corridor_width + 1):
                ix = x + (dx // (corridor_width + 1)) * i
                iy = y + (dy // (corridor_width + 1)) * i
                carve_out_area(dungeon, ix, iy, corridor_width)
            stack.append((nx, ny))
        else:
            stack.pop()
    return dungeon, start_x, start_y

# Function to carve out paths
def carve_out_area(dungeon, x, y, corridor_width):
    half_width = corridor_width // 2
    for dx in range(-half_width, half_width + 1):
        for dy in range(-half_width, half_width + 1):
            nx = x + dx
            ny = y + dy
            if 0 <= ny < len(dungeon) and 0 <= nx < len(dungeon[0]):
                dungeon[ny][nx] = 1  # Mark as path

# Create torch glow effect
def create_torch_glow(torch_entity):
    """Function to create a glow effect for each torch."""
    torch_glow = Entity(
        model='sphere',
        color=color.rgba(255, 223, 0, 50),  # Warm yellow color with transparency
        scale=Vec3(1.5, 1.5, 1.5),  # Adjust the scale for appropriate light spread
        position=torch_entity.position + Vec3(0, 1.5, 0),  # Position glow slightly above the torch
        parent=torch_entity,  # Parent it to the torch so it moves with it
        double_sided=True
    )
    return torch_glow

def create_dungeon_entities(dungeon_map, wall_texture, floor_texture, roof_texture, torch_frames, cell_size=2, floor_tile_size=2, player=None, debug_mode=False):
    entities = []
    torches = []  # List to store torch entities for later updates
    torch_height = 2.5
    torch_offset = 0.2
    torch_probability = 0.25  # Probability of placing a torch (reduce the number of torches)

    height = len(dungeon_map)
    width = len(dungeon_map[0])

    floor_positions = []

    for y in range(height):
        for x in range(width):
            tile = dungeon_map[y][x]
            world_x = x * cell_size * floor_tile_size
            world_z = y * cell_size * floor_tile_size

            if tile == 0:
                wall = Entity(
                    model='cube',
                    texture=wall_texture,
                    collider='box',
                    scale=(cell_size * floor_tile_size, cell_size * 2, cell_size * floor_tile_size),
                    position=(world_x, cell_size, world_z),
                )
                entities.append(wall)

                if random.random() < torch_probability:  # Random chance to place a torch
                    torch_position = None
                    torch_rotation = None

                    if x > 0 and dungeon_map[y][x - 1] == 1:
                        torch_position = Vec3(world_x - cell_size * floor_tile_size / 2 - torch_offset, torch_height, world_z)
                        torch_rotation = Vec3(0, -90, 0)
                    elif x < width - 1 and dungeon_map[y][x + 1] == 1:
                        torch_position = Vec3(world_x + cell_size * floor_tile_size / 2 + torch_offset, torch_height, world_z)
                        torch_rotation = Vec3(0, 90, 0)
                    elif y > 0 and dungeon_map[y - 1][x] == 1:
                        torch_position = Vec3(world_x, torch_height, world_z - cell_size * floor_tile_size / 2 - torch_offset)
                        torch_rotation = Vec3(0, 0, 0)
                    elif y < height - 1 and dungeon_map[y + 1][x] == 1:
                        torch_position = Vec3(world_x, torch_height, world_z + cell_size * floor_tile_size / 2 + torch_offset)
                        torch_rotation = Vec3(0, 180, 0)

                    if torch_position:
                        torch = Entity(
                            model='quad',  # Use quad for torches
                            texture=torch_frames[0],  # First frame for initialization
                            scale=(1, 2),  # Adjust scale for the torch
                            position=torch_position,
                            rotation=torch_rotation,
                            always_on_top=False,
                            double_sided=True  # Ensure torch is visible from both sides
                        )

                        if player:  # Only make the torch look at the player if player is provided
                            torch.look_at(player.position)

                        # Create and attach the torch light with more contrast
                        torch_light = PointLight(
                            parent=torch,  # Make the light follow the torch
                            position=(0, 0.5, 0),  # Offset the light slightly above the torch
                            color=color.rgb(255, 140, 0),  # Warm torch color
                            attenuation=(0.1, 0.05, 0.02),  # More dramatic light falloff
                            radius=3  # Lower radius for higher contrast
                        )

                        # Ensure that the torch light is properly parented
                        torch.torch_light = torch_light
                        entities.append(torch)
                        torches.append(torch)  # Add to the list of torches

            if tile == 1 or tile == 3:
                floor = Entity(
                    model='cube',
                    texture=floor_texture,
                    collider='box',
                    scale=(cell_size * floor_tile_size, 0.05, cell_size * floor_tile_size),
                    position=(world_x, 0, world_z),  # Set Y to 0 to make sure the floor is at ground level
                )
                entities.append(floor)
                floor_positions.append((world_x, 0, world_z))  # Update floor Y position to match the floor entity


    total_dungeon_width = width * cell_size * floor_tile_size
    total_dungeon_height = height * cell_size * floor_tile_size

    roof = Entity(
        model='cube',
        texture=roof_texture,
        texture_scale=(total_dungeon_width, total_dungeon_height),
        scale=(total_dungeon_width, 0.1, total_dungeon_height),
        position=(total_dungeon_width / 2, cell_size * 2, total_dungeon_height / 2)
    )
    entities.append(roof)

    return entities, floor_positions, torches  # Return the torches list

def flicker_torch_lights(torches, time_passed, min_intensity=0.5, max_intensity=1.0, flicker_speed=0.1):
    """Simulate torch light flickering by adjusting light intensity randomly."""
    from random import uniform

    for torch in torches:
        if hasattr(torch, 'torch_light'):
            # Use time_passed to scale the flicker speed
            random_intensity = uniform(min_intensity, max_intensity)
            torch.torch_light.color = color.rgb(255, int(140 * random_intensity), 0)  # Flicker the light's intensity
            torch.torch_light.attenuation = (1, flicker_speed * random_intensity * time_passed, 0.05)  # Adjust falloff with flicker
