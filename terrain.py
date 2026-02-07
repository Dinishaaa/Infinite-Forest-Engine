import math
from OpenGL.GL import *

# --- Mathematical Noise for Infinite Terrain ---
def get_height(x, z):
    # Sinusoidal noise as suggested in the methodology
    s = 0.1
    h = (math.sin(x * s) * math.cos(z * s) * 8.0)
    h += (math.sin(x * s * 0.5) * 4.0)
    return h

class ForestEngine:
    def __init__(self, chunk_size=20):
        self.chunk_size = chunk_size
        self.chunks = {}

    def draw_tree(self, x, y, z):
        """Draws a simple procedural tree"""
        # Trunk
        glColor3f(0.3, 0.2, 0.1)
        glBegin(GL_LINES)
        glVertex3f(x, y, z); glVertex3f(x, y + 1.5, z)
        glEnd()
        # Leaves (Pyramid)
        glColor3f(0.0, 0.4, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(x-0.4, y+1, z-0.4); glVertex3f(x+0.4, y+1, z-0.4); glVertex3f(x, y+2.5, z)
        glVertex3f(x-0.4, y+1, z+0.4); glVertex3f(x+0.4, y+1, z+0.4); glVertex3f(x, y+2.5, z)
        glEnd()

    def render_chunk(self, x_o, z_o):
        """Renders a grid-based chunk with height-based biomes"""
        glBegin(GL_TRIANGLES)
        for i in range(self.chunk_size):
            for j in range(self.chunk_size):
                # World coordinates
                x1, z1 = (x_o * self.chunk_size + i) * 2, (z_o * self.chunk_size + j) * 2
                x2, z2 = x1 + 2, z1 + 2
                
                h1, h2, h3, h4 = get_height(x1, z1), get_height(x2, z1), get_height(x1, z2), get_height(x2, z2)

                def set_color(h):
                    if h < 0: glColor3f(0.1, 0.3, 0.7)    # Water
                    elif h < 5: glColor3f(0.1, 0.5, 0.1)  # Forest Floor
                    else: glColor3f(0.5, 0.5, 0.5)        # Mountains

                # Triangle 1 & 2
                set_color(h1); glVertex3f(x1, h1, z1)
                set_color(h2); glVertex3f(x2, h2, z1)
                set_color(h3); glVertex3f(x1, h3, z2)
                set_color(h2); glVertex3f(x2, h2, z1)
                set_color(h4); glVertex3f(x2, h4, z2)
                set_color(h3); glVertex3f(x1, h3, z2)
        glEnd()

        # Place trees on grass biomes
        for i in range(0, self.chunk_size, 2):
            for j in range(0, self.chunk_size, 2):
                tx, tz = (x_o * self.chunk_size + i) * 2, (z_o * self.chunk_size + j) * 2
                th = get_height(tx, tz)
                if 0.5 < th < 4.5: # Tree height range
                    if (math.sin(tx) + math.cos(tz)) > 1.2: # Simple spawn probability
                        self.draw_tree(tx, th, tz)