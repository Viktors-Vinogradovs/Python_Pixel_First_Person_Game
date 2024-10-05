from ursina import *
import random

# Function to generate the dungeon layout
def generate_dungeon(width, height, corridor_width=1, manual_layout=None):
    if manual_layout:
        # If a manual layout is provided, return it directly
        start_x, start_y = 1, 1  # Define the starting point in the manual layout
        return manual_layout, start_x, start_y

    if width % (corridor_width + 1) != 1:
        width += (corridor_width + 1) - (width % (corridor_width + 1))
    if height % (corridor_width + 1) != 1:
        height += (corridor_width + 1) - (height % (corridor_width + 1))

    dungeon = [[0 for x in range(width)] for y in range(height)]

    start_x = random.randrange(corridor_width, width, corridor_width + 1)
    start_y = random.randrange(corridor_width, height, corridor_width + 1)
    carve_out_area(dungeon, start_x, start_y, corridor_width)

    stack = [(start_x, start_y)]

    while stack:
        x, y = stack[-1]

        directions = []
        if x > corridor_width:
            directions.append((- (corridor_width + 1), 0))  # Left
        if x < width - (corridor_width + 1):
            directions.append((corridor_width + 1, 0))  # Right
        if y > corridor_width:
            directions.append((0, - (corridor_width + 1)))  # Up
        if y < height - (corridor_width + 1):
            directions.append((0, corridor_width + 1))  # Down

        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if dungeon[ny][nx] == 0:
                neighbors.append((nx, ny, dx, dy))

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

# Function to add extra walls
def add_extra_walls(dungeon, corridor_width, extra_walls_probability=0.1):
    width = len(dungeon[0])
    height = len(dungeon)
    for y in range(corridor_width, height - corridor_width):
        for x in range(corridor_width, width - corridor_width):
            if dungeon[y][x] == 1:
                neighbors = 0
                offsets = [(0, -(corridor_width + 1)), (0, corridor_width + 1), (-(corridor_width + 1), 0), (corridor_width + 1, 0)]
                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    if 0 <= ny < height and 0 <= nx < width:
                        if dungeon[ny][nx] == 1:
                            neighbors += 1
                if neighbors == 1 and random.random() < extra_walls_probability:
                    dungeon[y][x] = 0  # Turn this path into a wall
    return dungeon

def create_dungeon_entities(dungeon_map, wall_texture, floor_texture, roof_texture, torch_frames, cell_size=2, floor_tile_size=2, player=None, debug_mode=False):
    entities = []
    torches = []  # List to store torch entities for later updates
    torch_height = 2.5
    torch_offset = 0.2

    height = len(dungeon_map)
    width = len(dungeon_map[0])

    floor_positions = []

    # Define the torch placement probability (e.g., 0.2 = 20% chance)
    torch_placement_chance = 0.2

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

                torch_position = None
                torch_rotation = None

                # Place torches with a random chance
                if random.random() < torch_placement_chance:
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
                            model='cube',  # Thin cube for the torch
                            texture=torch_frames[0],  # Start with the first frame
                            scale=(1, 1, 0.1),  # Thinner and taller torch
                            position=torch_position,
                            rotation=torch_rotation,
                            always_on_top=False,
                            color=color.green if debug_mode else color.white
                        )

                        torch_light = PointLight(
                            parent=torch,
                            position=(0, 0.5, 0),
                            color=color.rgb(255, 140, 0),
                            attenuation=(1, 0.1, 0.05),
                            radius=8
                        )
                        entities.append(torch)

                        # Add the torch to the list
                        torches.append(torch)

                        if debug_mode:
                            debug_marker = Entity(
                                model='sphere',
                                color=color.red,
                                scale=0.1,
                                position=torch.position,
                                always_on_top=True
                            )
                            entities.append(debug_marker)
                            print(f"Torch placed at position: {torch_position}")

            if tile == 1 or tile == 3:
                floor = Entity(
                    model='cube',
                    texture=floor_texture,
                    collider='box',
                    scale=(cell_size * floor_tile_size, 0.05, cell_size * floor_tile_size),
                    position=(world_x, 0.025, world_z),
                )
                entities.append(floor)
                floor_positions.append((world_x, 0, world_z))

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
