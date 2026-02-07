import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from terrain import ForestEngine, get_height

# Window Settings [cite: 46]
WIDTH, HEIGHT = 1280, 720

def main():
    if not glfw.init(): return
    window = glfw.create_window(WIDTH, HEIGHT, "Infinite Forest Engine", None, None)
    glfw.make_context_current(window)

    # Perspective and Depth [cite: 24, 34]
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, WIDTH/HEIGHT, 0.1, 400.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    # Exponential Fog [cite: 38]
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, [0.5, 0.7, 1.0, 1.0])
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.02)

    engine = ForestEngine()
    cam_x, cam_y, cam_z = 0, 10, 20

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glLoadIdentity()

        # Navigation: Arrow keys move the camera 
        if glfw.get_key(window, glfw.KEY_UP): cam_z -= 0.8
        if glfw.get_key(window, glfw.KEY_DOWN): cam_z += 0.8
        if glfw.get_key(window, glfw.KEY_LEFT): cam_x -= 0.8
        if glfw.get_key(window, glfw.KEY_RIGHT): cam_x += 0.8

        # Dynamic height to stay above ground
        cam_y = get_height(cam_x, cam_z) + 6.0
        
        # Camera look-at logic [cite: 34]
        gluLookAt(cam_x, cam_y, cam_z, cam_x, cam_y - 2, cam_z - 40, 0, 1, 0)

        # Chunking System: Load chunks around player [cite: 25, 32, 48]
        cx, cz = int(cam_x // 40), int(cam_z // 40)
        for x in range(cx - 2, cx + 2):
            for z in range(cz - 5, cz + 1):
                engine.render_chunk(x, z)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()