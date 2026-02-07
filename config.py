# config.py
class Settings:
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768
        self.fps = 60
        self.flight_speed = 0.2  # Increase this if movement feels too slow
        self.noise_scale = 0.08  # Higher = more rugged mountains
        self.terrain_size = 50   # Size of the grid
        self.render_distance = 100.0

settings = Settings()