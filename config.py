# settings.py

# --- CONSTANTS ---
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CHUNK_SIZE = 16 

# --- SHARED PARAMETERS ---
terrain_params = {
    "temperature": 0.5,      # Chaos (0.0 to 2.0)
    "pref_height": 10.0,     # Base height
    "render_dist": 8         # Radius of chunks
}

# --- APP STATE ---
app_state = {
    "bg_fly_speed": 0.07,    # Hidden fixed background speed
    "flight_z": 0.0,         # Animation position
    "player_speed": 0.5      # Controlled in Settings
}