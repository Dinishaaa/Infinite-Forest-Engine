# main.py
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import config as settings
import terrain as game

# --- UI HELPERS ---
def draw_rect(x, y, w, h, color):
    glColor3fv(color)
    glRectf(x, y, x+w, y+h)

def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    try:
        for char in str(text):
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    except: pass

def check_hover(window, x, y, w, h):
    mx, my = glfw.get_cursor_pos(window)
    my = settings.WINDOW_HEIGHT - my 
    return x <= mx <= x + w and y <= my <= y + h

def draw_background_animation(game_manager):
    # ANIMATION (Uses hidden fixed bg_fly_speed)
    settings.app_state["flight_z"] -= settings.app_state["bg_fly_speed"]
    
    glViewport(0, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(60, settings.WINDOW_WIDTH/settings.WINDOW_HEIGHT, 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    
    cam_y = 60
    gluLookAt(0, cam_y, settings.app_state["flight_z"], 0, cam_y - 20, settings.app_state["flight_z"] - 50, 0, 1, 0)
    
    cz = int(settings.app_state["flight_z"] // settings.CHUNK_SIZE)
    chunks = game_manager.chunks
    for x in range(-2, 3):
        for z in range(cz - 4, cz + 1):
            if (x, z, 'menu') not in chunks: 
                chunks[(x, z, 'menu')] = game.SmoothChunk(x, z, is_menu=True)
            chunks[(x, z, 'menu')].draw()
            
    keys_del = [k for k in chunks if k[2] == 'menu' and k[1] > cz + 2]
    for k in keys_del: chunks[k].destroy(); del chunks[k]
    
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluOrtho2D(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_FOG)
    glColor4f(0, 0, 0, 0.5); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRectf(0, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT); glDisable(GL_BLEND)

# --- SCREENS ---
def draw_home_screen(window):
    cx, cy = settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2
    draw_text(cx - 130, settings.WINDOW_HEIGHT - 150, "TERRAIN GENERATOR")

    play_rect = (cx - 100, cy + 20, 200, 50)
    hover_play = check_hover(window, *play_rect)
    draw_rect(*play_rect, (0.3, 0.8, 0.3) if hover_play else (0.2, 0.6, 0.2))
    draw_text(cx - 20, cy + 35, "PLAY")

    sett_rect = (cx - 100, cy - 60, 200, 50)
    hover_sett = check_hover(window, *sett_rect)
    draw_rect(*sett_rect, (0.3, 0.6, 0.8) if hover_sett else (0.2, 0.4, 0.6))
    draw_text(cx - 35, cy - 45, "SETTINGS")

    return play_rect, sett_rect

def draw_settings_screen(window):
    cx, cy = settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2
    draw_text(cx - 100, settings.WINDOW_HEIGHT - 150, "SETTINGS MENU")

    # PLAYER MOVE SPEED SLIDER
    draw_text(cx - 150, cy + 20, f"Player Fly Speed: {settings.app_state['player_speed']:.2f}")
    speed_bar = (cx - 150, cy - 10, 300, 20)
    draw_rect(*speed_bar, (0.4, 0.4, 0.4))
    
    # Scale 0.1 to 2.0 (Slider math: 0.0-1.0 map to 0.1-2.0)
    current_val = settings.app_state["player_speed"]
    norm_val = (current_val - 0.1) / 1.9
    norm_val = max(0.0, min(1.0, norm_val))
    
    knob_x = norm_val * 300
    draw_rect(cx - 150 + knob_x - 5, cy - 10, 10, 20, (1.0, 0.4, 0.4))

    back_rect = (cx - 100, cy - 80, 200, 50)
    hover = check_hover(window, *back_rect)
    draw_rect(*back_rect, (0.8, 0.3, 0.3) if hover else (0.6, 0.2, 0.2))
    draw_text(cx - 20, cy - 65, "BACK")

    return speed_bar, back_rect

def draw_controls_overlay(window):
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST); glDisable(GL_FOG)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

    glColor3f(1, 1, 1)
    draw_text(20, 100, "CONTROLS:")
    draw_text(20, 75, "W, A, S, D : Move")
    draw_text(20, 50, "Space/C : Fly Up/Down")
    draw_text(20, 25, "TAB : Settings Overlay | ESC : Exit")

    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_FOG)

def draw_game_overlay(window, game_manager):
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST); glDisable(GL_FOG)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, settings.WINDOW_WIDTH, 0, settings.WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    cx, cy = settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2
    
    glColor4f(0.1, 0.1, 0.1, 0.8); glEnable(GL_BLEND)
    glRectf(cx - 200, cy - 150, cx + 200, cy + 200)
    glDisable(GL_BLEND)
    
    draw_text(cx - 80, cy + 160, "GAME SETTINGS")
    
    draw_text(cx - 150, cy + 120, f"Chaos: {settings.terrain_params['temperature']:.2f}")
    t_bar = (cx - 150, cy + 90, 300, 20)
    draw_rect(*t_bar, (0.5, 0.5, 0.5))
    draw_rect(cx - 150 + (settings.terrain_params["temperature"]/2.0)*300 - 5, cy + 90, 10, 20, (1, 0.3, 0.3))
    
    draw_text(cx - 150, cy + 50, f"Height: {int(settings.terrain_params['pref_height'])}")
    h_bar = (cx - 150, cy + 20, 300, 20)
    draw_rect(*h_bar, (0.5, 0.5, 0.5))
    h_norm = (settings.terrain_params["pref_height"] + 20) / 100.0
    draw_rect(cx - 150 + h_norm*300 - 5, cy + 20, 10, 20, (0.3, 0.3, 1))

    draw_text(cx - 150, cy - 20, f"Render Dist: {settings.terrain_params['render_dist']}")
    d_bar = (cx - 150, cy - 50, 300, 20)
    draw_rect(*d_bar, (0.5, 0.5, 0.5))
    d_norm = (settings.terrain_params["render_dist"] - 2) / 14.0
    draw_rect(cx - 150 + d_norm*300 - 5, cy - 50, 10, 20, (0.3, 1, 0.3))

    close_rect = (cx - 100, cy - 120, 200, 40)
    hover = check_hover(window, *close_rect)
    draw_rect(*close_rect, (0.8, 0.3, 0.3) if hover else (0.6, 0.2, 0.2))
    draw_text(cx - 60, cy - 110, "CLOSE OVERLAY")

    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_FOG)
    
    return t_bar, h_bar, d_bar, close_rect

# --- MAIN ---
def main():
    if not glfw.init(): return
    glutInit()
    window = glfw.create_window(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, "Terrain Gen", None, None)
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.5, 1.0, 0.5, 0.0]); glEnable(GL_COLOR_MATERIAL)

    game_manager = game.GameManager()
    state = "HOME"
    active_slider = None
    tab_pressed = False

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.6, 0.8, 1.0, 1.0)

        if state == "HOME":
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            draw_background_animation(game_manager)
            play_btn, sett_btn = draw_home_screen(window)

            if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                if check_hover(window, *play_btn):
                    state = "GAME"
                    game_manager.start()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                elif check_hover(window, *sett_btn):
                    state = "SETTINGS"

        elif state == "SETTINGS":
            draw_background_animation(game_manager)
            speed_bar, back_btn = draw_settings_screen(window)

            if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                mx, my = glfw.get_cursor_pos(window)
                if active_slider is None:
                    if check_hover(window, *back_btn): state = "HOME"
                    elif check_hover(window, *speed_bar): active_slider = 'speed'
                
                if active_slider == 'speed':
                    # Slider maps 0.0-1.0 -> 0.1-2.0
                    val = (mx - speed_bar[0]) / speed_bar[2]
                    val = max(0.0, min(1.0, val))
                    settings.app_state["player_speed"] = 0.1 + (val * 1.9)
            else:
                active_slider = None

        elif state == "GAME":
            glMatrixMode(GL_PROJECTION); glLoadIdentity()
            gluPerspective(60, settings.WINDOW_WIDTH/settings.WINDOW_HEIGHT, 0.1, 500.0)
            
            game_manager.update(window)
            game_manager.render()
            draw_controls_overlay(window)

            if glfw.get_key(window, glfw.KEY_TAB) == glfw.PRESS:
                if not tab_pressed:
                    game_manager.show_overlay = not game_manager.show_overlay
                    mode = glfw.CURSOR_NORMAL if game_manager.show_overlay else glfw.CURSOR_DISABLED
                    glfw.set_input_mode(window, glfw.CURSOR, mode)
                    tab_pressed = True
            else:
                tab_pressed = False

            if game_manager.show_overlay:
                t_bar, h_bar, d_bar, close_btn = draw_game_overlay(window, game_manager)
                if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                    mx, my = glfw.get_cursor_pos(window)
                    if active_slider is None:
                        if check_hover(window, *close_btn):
                            game_manager.show_overlay = False
                            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                        elif check_hover(window, *t_bar): active_slider = 'temp'
                        elif check_hover(window, *h_bar): active_slider = 'height'
                        elif check_hover(window, *d_bar): active_slider = 'dist'
                    
                    changed = False
                    if active_slider == 'temp':
                        settings.terrain_params["temperature"] = max(0.0, min(2.0, (mx - t_bar[0]) / t_bar[2] * 2.0))
                        changed = True
                    elif active_slider == 'height':
                        settings.terrain_params["pref_height"] = -20 + (max(0.0, min(1.0, (mx - h_bar[0]) / h_bar[2])) * 100.0)
                        changed = True
                    elif active_slider == 'dist':
                        settings.terrain_params["render_dist"] = int(2 + (max(0.0, min(1.0, (mx - d_bar[0]) / d_bar[2])) * 14.0))
                        changed = True
                    if changed: game_manager.regen_chunks()
                else:
                    active_slider = None

            if glfw.get_key(window, glfw.KEY_ESCAPE): state = "HOME"

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()