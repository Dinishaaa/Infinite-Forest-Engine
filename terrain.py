# game.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import config as settings

# --- TERRAIN MATH ---
def get_height(x, z, temp, base_height):
    noise = math.sin(x * 0.05) * math.cos(z * 0.05)
    noise += (math.sin(x * 0.1) * math.sin(z * 0.1)) * 0.5
    noise += (math.sin(x * 0.3) * math.cos(z * 0.35)) * 0.2
    return base_height + (noise * (temp * 40.0))

def get_color(h, temp):
    if h < -10 * temp: return (0.1, 0.2, 0.6)
    elif h < -2 * temp: return (0.1, 0.4, 0.8)
    elif h < 2: return (0.8, 0.7, 0.5)
    elif h < 20 * temp: return (0.2, 0.6, 0.2)
    elif h < 45 * temp: return (0.4, 0.4, 0.45)
    else: return (0.95, 0.95, 1.0)

class SmoothChunk:
    def __init__(self, x_o, z_o, is_menu=False):
        self.list_id = glGenLists(1)
        self.x_o, self.z_o, self.is_menu = x_o, z_o, is_menu
        self.generate_mesh()

    def generate_mesh(self):
        if self.is_menu:
            t_val, h_val = 1.2, 0.0 
        else:
            t_val = settings.terrain_params["temperature"]
            h_val = settings.terrain_params["pref_height"]
        
        glNewList(self.list_id, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        step = 1.0 
        for i in range(settings.CHUNK_SIZE):
            for j in range(settings.CHUNK_SIZE):
                x = (self.x_o * settings.CHUNK_SIZE + i) * step
                z = (self.z_o * settings.CHUNK_SIZE + j) * step
                
                h1 = get_height(x, z, t_val, h_val)
                h2 = get_height(x + step, z, t_val, h_val)
                h3 = get_height(x, z + step, t_val, h_val)
                h4 = get_height(x + step, z + step, t_val, h_val)

                glNormal3f(h1 - h2, 2.0, h1 - h3) 
                glColor3fv(get_color(h1, t_val)); glVertex3f(x, h1, z)
                glColor3fv(get_color(h2, t_val)); glVertex3f(x + step, h2, z)
                glColor3fv(get_color(h3, t_val)); glVertex3f(x, h3, z + step)

                glNormal3f(h2 - h4, 2.0, h2 - h3) 
                glColor3fv(get_color(h2, t_val)); glVertex3f(x + step, h2, z)
                glColor3fv(get_color(h4, t_val)); glVertex3f(x + step, h4, z + step)
                glColor3fv(get_color(h3, t_val)); glVertex3f(x, h3, z + step)
        glEnd()
        glEndList()

    def draw(self): glCallList(self.list_id)
    def destroy(self): glDeleteLists(self.list_id, 1)

class GameManager:
    def __init__(self):
        self.chunks = {}
        self.cam_pos = [0, 20, 0]
        self.cam_rot = [0, 0]
        self.first_mouse = True
        self.last_mx, self.last_my = 0, 0
        self.show_overlay = False

    def start(self):
        self.chunks.clear()
        p_h = settings.terrain_params["pref_height"]
        t = settings.terrain_params["temperature"]
        spawn_y = max(p_h + (t * 20) + 15, p_h + 10)
        self.cam_pos = [0, spawn_y, 0]
        self.cam_rot = [0, 0]
        self.first_mouse = True
        self.show_overlay = False
        
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [0.6, 0.8, 1.0, 1.0])
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 20.0)
        self.update_fog()

    def update_fog(self):
        dist = float(settings.terrain_params["render_dist"] * settings.CHUNK_SIZE)
        glFogf(GL_FOG_END, dist)

    def update(self, window):
        import glfw
        
        # Mouse Look
        if not self.show_overlay:
            mx, my = glfw.get_cursor_pos(window)
            if self.first_mouse: self.last_mx, self.last_my = mx, my; self.first_mouse = False
            
            dx, dy = mx - self.last_mx, self.last_my - my
            self.last_mx, self.last_my = mx, my
            
            self.cam_rot[0] += dx * 0.1
            self.cam_rot[1] = max(-89, min(89, self.cam_rot[1] + dy * 0.1))
        else:
            mx, my = glfw.get_cursor_pos(window)
            self.last_mx, self.last_my = mx, my
            self.first_mouse = True

        # Camera
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glRotatef(-self.cam_rot[1], 1, 0, 0)
        glRotatef(-self.cam_rot[0], 0, 1, 0)
        glTranslatef(-self.cam_pos[0], -self.cam_pos[1], -self.cam_pos[2])

        # Movement
        yaw_rad = math.radians(self.cam_rot[0])
        fwd_x, fwd_z = math.sin(yaw_rad), -math.cos(yaw_rad)
        right_x, right_z = math.cos(yaw_rad), math.sin(yaw_rad)

        # USE SETTINGS SPEED
        base_speed = settings.app_state["player_speed"]
        speed = base_speed if not glfw.get_key(window, glfw.KEY_LEFT_SHIFT) else base_speed * 3.0

        if glfw.get_key(window, glfw.KEY_W): 
            self.cam_pos[0] += fwd_x * speed; self.cam_pos[2] += fwd_z * speed
        if glfw.get_key(window, glfw.KEY_S): 
            self.cam_pos[0] -= fwd_x * speed; self.cam_pos[2] -= fwd_z * speed
        if glfw.get_key(window, glfw.KEY_A): 
            self.cam_pos[0] -= right_x * speed; self.cam_pos[2] -= right_z * speed
        if glfw.get_key(window, glfw.KEY_D): 
            self.cam_pos[0] += right_x * speed; self.cam_pos[2] += right_z * speed
            
        if glfw.get_key(window, glfw.KEY_SPACE): self.cam_pos[1] += speed
        if glfw.get_key(window, glfw.KEY_C): self.cam_pos[1] -= speed

    def render(self):
        cx, cz = int(self.cam_pos[0] // settings.CHUNK_SIZE), int(self.cam_pos[2] // settings.CHUNK_SIZE)
        r_dist = settings.terrain_params["render_dist"]
        
        for x in range(cx - r_dist, cx + r_dist + 1):
            for z in range(cz - r_dist, cz + r_dist + 1):
                if (x-cx)**2 + (z-cz)**2 <= r_dist**2:
                    if (x, z, 'game') not in self.chunks: 
                        self.chunks[(x, z, 'game')] = SmoothChunk(x, z, is_menu=False)
                    self.chunks[(x, z, 'game')].draw()
        
        keys_del = [k for k in self.chunks if k[2]=='game' and (k[0]-cx)**2+(k[1]-cz)**2 > (r_dist+1)**2]
        for k in keys_del: self.chunks[k].destroy(); del self.chunks[k]

    def regen_chunks(self):
        for k in list(self.chunks.keys()):
            self.chunks[k].destroy()
            del self.chunks[k]
        self.update_fog()