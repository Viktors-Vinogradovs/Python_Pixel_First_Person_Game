from ursina import *

class AnimatedSpriteEnemy(Entity):
    def __init__(self, player, position=(0, 0, 0), texture='assets/sprites/enemy.png', **kwargs):
        super().__init__(
            model='quad',  # 2D plane
            texture=texture,  # The sprite sheet image
            position=position,
            scale=(1.5, 1.5),  # Adjust size
            **kwargs
        )
        self.player = player
        self.frame_index = 0
        self.frames_per_row = 4  # Number of frames per row in your sprite sheet
        self.total_frames = 16  # Total number of frames in the sprite sheet
        self.frame_delay = 0.1  # Time between frames
        self.frame_timer = 0

    def update(self):
        # Make the sprite face the player
        self.look_at_2d(self.player.position, 'y')

        # Update the animation frames
        self.frame_timer += time.dt
        if self.frame_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % self.total_frames
            self.frame_timer = 0
            self.set_texture_frame(self.frame_index)

    def set_texture_frame(self, frame_index):
        # Calculate the correct UV coordinates for the frame
        frame_row = frame_index // self.frames_per_row
        frame_column = frame_index % self.frames_per_row

        uv_scale_x = 1 / self.frames_per_row
        uv_scale_y = 1 / (self.total_frames // self.frames_per_row)

        self.texture_coords = [
            (frame_column * uv_scale_x, 1 - (frame_row + 1) * uv_scale_y),
            ((frame_column + 1) * uv_scale_x, 1 - (frame_row + 1) * uv_scale_y),
            ((frame_column + 1) * uv_scale_x, 1 - frame_row * uv_scale_y),
            (frame_column * uv_scale_x, 1 - frame_row * uv_scale_y)
        ]
