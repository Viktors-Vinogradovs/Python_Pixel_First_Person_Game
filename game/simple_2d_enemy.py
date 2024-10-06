from ursina import *

class Simple2DEnemy(Entity):
    class Simple3DEnemy(Entity):
        def __init__(self, player, position=(0, 0, 0), debug_mode=False, **kwargs):
            super().__init__(
                model='cube',  # Use a simple 3D cube
                color=color.blue,  # Color it blue for visibility
                position=position,
                scale=(1.5, 1.5, 1.5),  # Adjust the size
                **kwargs
            )
            self.player = player
            self.attack_range = 2.0  # Set attack range
            self.debug_mode = debug_mode

            if self.debug_mode:
                self.bounding_box = Entity(parent=self, model='wireframe_cube', scale=self.scale * 1.2, color=color.green)
                self.position_label = Text(text=f'Pos: {self.position}', position=(0, 2, 0), color=color.white, scale=2, parent=self)

    def update(self):
        # Make the 3D enemy face the player
        self.look_at(self.player.position)
        self.rotation_x = 0
        self.rotation_z = 0


