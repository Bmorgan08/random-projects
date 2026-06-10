import math
import ctypes
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, FULLSCREEN
from OpenGL.GL import *

class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class camera:
    def __init__(self, x, y, z, pitch, yaw):
        self.pos = vec3(x, y, z)
        self.pitch = pitch
        self.yaw = yaw

class triangle:
    def __init__(self, v1, v2, v3, color=None):
        self.v1 = vec3(v1.x, v1.y, v1.z)
        self.v2 = vec3(v2.x, v2.y, v2.z)
        self.v3 = vec3(v3.x, v3.y, v3.z)
        self.color = color or (200, 200, 200)

class mesh:
    def __init__(self, tris, pos, spin_rate=0.0):
        self.tris = tris
        self.pos = pos
        self.spin_rate = spin_rate
        self.yaw = 0.0

def mat_vec(v, m):
    x = v.x*m[0][0] + v.y*m[0][1] + v.z*m[0][2] + m[0][3]
    y = v.x*m[1][0] + v.y*m[1][1] + v.z*m[1][2] + m[1][3]
    z = v.x*m[2][0] + v.y*m[2][1] + v.z*m[2][2] + m[2][3]
    w = v.x*m[3][0] + v.y*m[3][1] + v.z*m[3][2] + m[3][3]
    if w != 0:
        x /= w; y /= w; z /= w
    return vec3(x, y, z)

def mat_mat(a, b):
    r = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            r[i][j] = sum(a[i][k] * b[k][j] for k in range(4))
    return r

def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]]

def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1,0,0,0],[0,c,s,0],[0,-s,c,0],[0,0,0,1]]

def translation(x, y, z):
    return [[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]]

def define_projection_matrix(aspect_ratio):
    fov = math.pi / 2
    near, far = 0.1, 1000
    f = 1 / math.tan(fov / 2)
    return [
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ]

def dot(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z

def cross(a, b):
    return vec3(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x)

def normalize(v):
    l = math.sqrt(v.x**2 + v.y**2 + v.z**2)
    return vec3(v.x/l, v.y/l, v.z/l) if l > 0 else vec3(0, 0, 0)

def sub(a, b):
    return vec3(a.x-b.x, a.y-b.y, a.z-b.z)

def lerp_v(a, b, t):
    return vec3(a.x+t*(b.x-a.x), a.y+t*(b.y-a.y), a.z+t*(b.z-a.z))

def clip_near(v1, v2, v3, near=0.1):
    inside  = [v for v in (v1,v2,v3) if v.z >= near]
    outside = [v for v in (v1,v2,v3) if v.z <  near]
    if len(inside) == 3: return [(v1,v2,v3)]
    if len(inside) == 0: return []
    if len(inside) == 1:
        a = inside[0]; b,c = outside
        t1 = (near-a.z)/(b.z-a.z); t2 = (near-a.z)/(c.z-a.z)
        return [(a, lerp_v(a,b,t1), lerp_v(a,c,t2))]
    a,b = inside; c = outside[0]
    t1 = (near-a.z)/(c.z-a.z); t2 = (near-b.z)/(c.z-b.z)
    ac = lerp_v(a,c,t1); bc = lerp_v(b,c,t2)
    return [(a,b,ac),(b,bc,ac)]

def screen_pt(v, w, h):
    return (int(v.x * w//2 + w//2), int(-v.y * h//2 + h//2))

def make_cube_mesh(pos, spin_rate=0.0):
    v = [
        vec3(-0.5,-0.5,-0.5), vec3( 0.5,-0.5,-0.5),
        vec3( 0.5, 0.5,-0.5), vec3(-0.5, 0.5,-0.5),
        vec3(-0.5,-0.5, 0.5), vec3( 0.5,-0.5, 0.5),
        vec3( 0.5, 0.5, 0.5), vec3(-0.5, 0.5, 0.5),
    ]
    face_colors = [
        (200,100,100),(200,100,100),
        (100,200,100),(100,200,100),
        (100,100,200),(100,100,200),
        (200,200,100),(200,200,100),
        (200,100,200),(200,100,200),
        (100,200,200),(100,200,200),
    ]
    faces = [
        (v[0],v[2],v[1]),(v[0],v[3],v[2]),
        (v[4],v[5],v[6]),(v[4],v[6],v[7]),
        (v[0],v[1],v[5]),(v[0],v[5],v[4]),
        (v[3],v[7],v[6]),(v[3],v[6],v[2]),
        (v[0],v[4],v[7]),(v[0],v[7],v[3]),
        (v[1],v[2],v[6]),(v[1],v[6],v[5]),
    ]
    tris = [triangle(a,b,c,fc) for (a,b,c),fc in zip(faces,face_colors)]
    return mesh(tris, pos, spin_rate)

def load_obj(path, pos, color=(180,180,180), spin_rate=0.0):
    verts = []
    tris = []
    try:
        with open(path) as f:
            for line in f:
                parts = line.strip().split()
                if not parts: continue
                if parts[0] == 'v':
                    verts.append(vec3(float(parts[1]), -float(parts[2]), float(parts[3])))
                elif parts[0] == 'f':
                    indices = [int(p.split('/')[0])-1 for p in parts[1:]]
                    for i in range(1, len(indices)-1):
                        tris.append(triangle(verts[indices[0]], verts[indices[i+1]], verts[indices[i]], color))
    except FileNotFoundError:
        print(f"OBJ not found: {path}")
    return mesh(tris, pos, spin_rate)

def main():
    pygame.init()
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    pygame.display.set_mode((W, H), FULLSCREEN | DOUBLEBUF | OPENGL)
    pygame.display.set_caption("rasterizer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 20)

    # set up OpenGL for 2D screen-space rendering
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W, H, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

    proj = define_projection_matrix(W / H)
    light_dir = normalize(vec3(0.5, -1, -0.5))
    cam = camera(0, 0, -4, 0, 0)
    mouse_sensitivity = 0.002

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    try:
        sdl2 = ctypes.CDLL("libSDL2-2.0.so.0")
        sdl2.SDL_SetRelativeMouseMode(1)
    except OSError:
        pass

    scene = [
        make_cube_mesh(vec3( 0, 0, 0), spin_rate=0.7),
        make_cube_mesh(vec3( 2, 0, 2), spin_rate=-0.5),
        make_cube_mesh(vec3(-2, 0, 3), spin_rate=1.0),
        load_obj("/home/benm/Downloads/teapot.obj", vec3(0,0,5), color=(180,140,100), spin_rate=0.3),
    ]

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                dx, dy = event.rel
                cam.yaw   -= dx * mouse_sensitivity
                cam.pitch -= dy * mouse_sensitivity
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                    running = False

        keys = pygame.key.get_pressed()
        speed = 4 * dt
        fwd_x = math.sin(cam.yaw)
        fwd_z = math.cos(cam.yaw)
        if keys[pygame.K_w]:      cam.pos.x += fwd_x*speed; cam.pos.z += fwd_z*speed
        if keys[pygame.K_s]:      cam.pos.x -= fwd_x*speed; cam.pos.z -= fwd_z*speed
        if keys[pygame.K_a]:      cam.pos.x += fwd_z*speed; cam.pos.z -= fwd_x*speed
        if keys[pygame.K_d]:      cam.pos.x -= fwd_z*speed; cam.pos.z += fwd_x*speed
        if keys[pygame.K_SPACE]:  cam.pos.y += speed
        if keys[pygame.K_LSHIFT]: cam.pos.y -= speed

        for obj in scene:
            obj.yaw += obj.spin_rate * dt

        # clear
        glClearColor(0.08, 0.08, 0.08, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        view_rot = mat_mat(rot_x(cam.pitch), rot_y(-cam.yaw))

        tris_to_draw = []
        for obj in scene:
            obj_world = mat_mat(translation(obj.pos.x, obj.pos.y, obj.pos.z), rot_y(obj.yaw))
            for tri in obj.tris:
                w1 = mat_vec(tri.v1, obj_world)
                w2 = mat_vec(tri.v2, obj_world)
                w3 = mat_vec(tri.v3, obj_world)

                c1 = vec3(w1.x-cam.pos.x, w1.y-cam.pos.y, w1.z-cam.pos.z)
                c2 = vec3(w2.x-cam.pos.x, w2.y-cam.pos.y, w2.z-cam.pos.z)
                c3 = vec3(w3.x-cam.pos.x, w3.y-cam.pos.y, w3.z-cam.pos.z)

                c1 = mat_vec(c1, view_rot)
                c2 = mat_vec(c2, view_rot)
                c3 = mat_vec(c3, view_rot)

                normal = normalize(cross(sub(c2,c1), sub(c3,c1)))
                if dot(normal, c1) > 0:
                    continue

                world_normal = normalize(cross(sub(w2,w1), sub(w3,w1)))
                brightness = max(0.15, -dot(world_normal, light_dir))
                r,g,b = tri.color
                color = (int(r*brightness), int(g*brightness), int(b*brightness))

                for r1,r2,r3 in clip_near(c1, c2, c3):
                    p1 = mat_vec(r1, proj)
                    p2 = mat_vec(r2, proj)
                    p3 = mat_vec(r3, proj)
                    avg_z = (r1.z + r2.z + r3.z) / 3
                    tris_to_draw.append((avg_z, color, p1, p2, p3))

        tris_to_draw.sort(key=lambda t: -t[0])

        # draw triangles
        glBegin(GL_TRIANGLES)
        for _, color, p1, p2, p3 in tris_to_draw:
            pts = [screen_pt(p1,W,H), screen_pt(p2,W,H), screen_pt(p3,W,H)]
            glColor3f(color[0]/255, color[1]/255, color[2]/255)
            for x,y in pts:
                glVertex2f(x, y)
        glEnd()

        # draw edges
        glColor3f(0, 0, 0)
        for _, color, p1, p2, p3 in tris_to_draw:
            pts = [screen_pt(p1,W,H), screen_pt(p2,W,H), screen_pt(p3,W,H)]
            glBegin(GL_LINE_LOOP)
            for x,y in pts:
                glVertex2f(x, y)
            glEnd()

        # HUD text — flip surface vertically since glDrawPixels is bottom-up
        text = f"FPS: {fps:.0f}  x:{cam.pos.x:.1f} y:{cam.pos.y:.1f} z:{cam.pos.z:.1f}"
        text_surf = pygame.transform.flip(font.render(text, True, (200,200,200)), False, True).convert_alpha()
        tw, th = text_surf.get_size()
        raw = pygame.image.tostring(text_surf, "RGBA", False)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glWindowPos2i(10, H - th - 10)
        glDrawPixels(tw, th, GL_RGBA, GL_UNSIGNED_BYTE, raw)
        glDisable(GL_BLEND)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
