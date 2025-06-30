# Libs
# - Pygane
# - PyOpenGL
# - numpy

from math import radians
import os
import pygame
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from constants import *
from object3D import Object3D
from object import *
from camera import Camera
from keymap import keymap

class Engine():
    def __init__(self):
        pygame.init()
        self.running = True
        self.screen_size = SCREEN_SIZE
        self.screen = pygame.display.set_mode((800,600), DOUBLEBUF | OPENGL)
        self.skybox_texture = self.load_skybox("assets/skybox/")
        self.camera = Camera()
        self.clock = pg.time.Clock()

        self.textures = {
            "placeholder": self.load_texture('assets/textures/placeholder.png'),
        }

        self.scene = {}

    def init_scene(self):
        cube1 = Object3D("assets/objs/cube.obj", self.textures['placeholder'])
        cube1.set_position(0, 0, 0)
        self.scene["cube1"] = cube1

        cylinder1 = Object3D("assets/objs/cylinder.obj", self.textures['placeholder'])
        cylinder1.set_position(3, 2, 0)
        cylinder1.set_pivot_world(0, 0, 0)
        self.scene["cylinder1"] = cylinder1

        pyramid1 = Object3D("assets/objs/pyramid.obj", self.textures['placeholder'])
        pyramid1.set_position(6, 0, 0)
        pyramid1.set_scale(2, 5, 1)
        self.scene["pyramid1"] = pyramid1

        tetrahedron1 = Object3D("assets/objs/tetrahedron.obj", self.textures['placeholder'])
        tetrahedron1.set_position(9, 0, 0)
        self.scene["tetrahedron1"] = tetrahedron1

        sphere1 = Object3D("assets/objs/sphere.obj", self.textures['placeholder'])
        sphere1.set_position(12, 0, 0)
        sphere1.shear(xy=1)
        self.scene["sphere1"] = sphere1

    def update_scene(self):
        q1 = Quaternion(0.9999619, 0.0087265, 0.0, 0.0) # 1deg x
        self.scene["cube1"].rotate(q1)

        angle = 0.1 # rad
        c = np.cos(angle)
        s = np.sin(angle)
        m = np.array([
            [1,  0,  0],
            [0,  c, -s],
            [0,  s,  c]
        ])
        self.scene["cylinder1"].rotateM(m)
        

    def draw_scene(self, wireframe, textured):
        for obj in self.scene.values():
            obj.draw(wireframe=wireframe, textured=textured)

    def run(self):
        # OpenGL default settings
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, SCREEN_SIZE[0]/SCREEN_SIZE[1], 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Pygame default settings
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

        # Custom default settings
        mouse_control = False
        wireframe = False
        texture = True
        running = True

        # Init scene
        self.init_scene()

        while running:
            dt = self.clock.tick(60) / 1000
            keys = pygame.key.get_pressed()
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False


                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_control = True
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.get_rel()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_control = False
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                
                elif event.type == pygame.MOUSEMOTION:
                    if mouse_control:
                        dx, dy = event.rel
                        self.camera.process_mouse_motion(dx, dy)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and mouse_control:
                        mouse_control = False
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                    if event.key == keymap["wireframe"]:
                        wireframe = not wireframe
                    if event.key == keymap["texture"]:
                        texture = not texture

            # Camera
            self.camera.update_position(keys, dt)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            self.camera.apply_view()

            # Draw and update
            self.draw_skybox(self.skybox_texture)
            self.draw_axes(length=5.0, width=5.0)
            self.draw_scene(wireframe=wireframe, textured=texture)
            self.update_scene()

            # Axis overlay
            m = glGetFloatv(GL_MODELVIEW_MATRIX).copy()
            # Supprimer la translation
            m[3][0] = m[3][1] = m[3][2] = 0.0
            self.draw_axes_overlay(m)

            # Update
            pygame.display.flip()
            self.clock.tick(60)

    def draw_cube(self):
        # Test function keeped
        vertices = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1),
        )
        edges = (
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,7),(7,6),(6,4),
            (0,4),(1,5),(2,7),(3,6),
        )
        glBegin(GL_LINES)
        glColor3f(1, 1, 1)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def draw_axes(self, length=1.0, width=1.0):
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_TEXTURE_CUBE_MAP)
        glLineWidth(width)

        glBegin(GL_LINES)

        # Axe X (rouge)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(length, 0.0, 0.0)

        # Axe Y (vert)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, length, 0.0)

        # Axe Z (bleu)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, length)

        glEnd()

        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glLineWidth(1.0)

    def draw_axes_overlay(self, camera_rotation_matrix):
        viewport = glGetIntegerv(GL_VIEWPORT)
        glViewport(0, viewport[3] - 100, 100, 100)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45, 1.0, 0.1, 10.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        gluLookAt(0, 0, 3,  0, 0, 0,  0, 1, 0)
        glMultMatrixf(camera_rotation_matrix)

        glDisable(GL_DEPTH_TEST)

        self.draw_axes(length=1.0, width=1.0)

        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glViewport(*viewport)

    def load_texture(self, path):
        from PIL import Image
        img = Image.open(path).convert("RGB")
        img_data = img.tobytes("raw", "RGB", 0, -1)
        width, height = img.size

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex_id

    def load_obj(self, filename):
        vertices = []
        texcoords = []
        faces = []

        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.strip().split()
                    vertex = list(map(float, parts[1:4]))
                    vertices.append(vertex)
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    uv = list(map(float, parts[1:3]))
                    texcoords.append(uv)
                elif line.startswith('f '):
                    parts = line.strip().split()[1:]
                    face = []
                    for p in parts:
                        v_indices = p.split('/')
                        v_idx = int(v_indices[0]) - 1
                        vt_idx = int(v_indices[1]) - 1 if len(v_indices) > 1 and v_indices[1] != '' else None
                        face.append((v_idx, vt_idx))
                    if len(face) == 3:
                        faces.append(face)
                    elif len(face) == 4:
                        faces.append([face[0], face[1], face[2]])
                        faces.append([face[0], face[2], face[3]])

        return vertices, faces, texcoords
 
    def draw_obj(self, vertices, faces, texcoords, texture_id=None, wireframe=False, texture=False):
        if texture and texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glColor3f(1, 1, 1)
        if wireframe == True:
            for face in faces:
                glBegin(GL_LINE_LOOP)
                for vertex in face:
                    v_idx = vertex[0]
                    glVertex3fv(vertices[v_idx])
                glEnd()
        else:
            glBegin(GL_TRIANGLES)  
            for face in faces:
                for v_idx, vt_idx in face:
                    if texture == True and vt_idx is not None and texcoords:
                        glTexCoord2f(*texcoords[vt_idx])
                    glVertex3fv(vertices[v_idx])
            glEnd()

        if texture_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def load_skybox(self, folder_path):
        from PIL import Image
        faces = [
            "right.png", "left.png",
            "top.png", "bottom.png",
            "front.png", "back.png",
        ]
        
        texID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texID)

        target_faces = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        ]

        for i in range(6):
            img = Image.open(os.path.join(folder_path, faces[i])).convert('RGB')
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            img_data = img.tobytes("raw", "RGB", 0, -1)
            glTexImage2D(target_faces[i], 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        return texID

    def draw_skybox(self, texture_id):
        size = 50.0
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_TEXTURE_CUBE_MAP)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
        glPushMatrix()
        
        # Supprime les translations de la caméra
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        m[3][0] = m[3][1] = m[3][2] = 0.0
        glLoadMatrixf(m)

        glBegin(GL_QUADS)

        # Face droite
        glTexCoord3f(1, -1, -1); glVertex3f( size, -size, -size)
        glTexCoord3f(1, -1,  1); glVertex3f( size, -size,  size)
        glTexCoord3f(1,  1,  1); glVertex3f( size,  size,  size)
        glTexCoord3f(1,  1, -1); glVertex3f( size,  size, -size)

        # Face gauche
        glTexCoord3f(-1, -1,  1); glVertex3f(-size, -size,  size)
        glTexCoord3f(-1, -1, -1); glVertex3f(-size, -size, -size)
        glTexCoord3f(-1,  1, -1); glVertex3f(-size,  size, -size)
        glTexCoord3f(-1,  1,  1); glVertex3f(-size,  size,  size)

        # Face top
        glTexCoord3f(-1, 1, -1); glVertex3f(-size,  size, -size)
        glTexCoord3f( 1, 1, -1); glVertex3f( size,  size, -size)
        glTexCoord3f( 1, 1,  1); glVertex3f( size,  size,  size)
        glTexCoord3f(-1, 1,  1); glVertex3f(-size,  size,  size)

        # Face bottom
        glTexCoord3f(-1, -1,  1); glVertex3f(-size, -size,  size)
        glTexCoord3f( 1, -1,  1); glVertex3f( size, -size,  size)
        glTexCoord3f( 1, -1, -1); glVertex3f( size, -size, -size)
        glTexCoord3f(-1, -1, -1); glVertex3f(-size, -size, -size)

        # Face front
        glTexCoord3f(-1, -1, -1); glVertex3f(-size, -size, -size)
        glTexCoord3f( 1, -1, -1); glVertex3f( size, -size, -size)
        glTexCoord3f( 1,  1, -1); glVertex3f( size,  size, -size)
        glTexCoord3f(-1,  1, -1); glVertex3f(-size,  size, -size)

        # Face back
        glTexCoord3f( 1, -1, 1); glVertex3f( size, -size, size)
        glTexCoord3f(-1, -1, 1); glVertex3f(-size, -size, size)
        glTexCoord3f(-1,  1, 1); glVertex3f(-size,  size, size)
        glTexCoord3f( 1,  1, 1); glVertex3f( size,  size, size)

        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_CUBE_MAP)
        glDepthFunc(GL_LESS)

if __name__ == "__main__":
    engine = Engine()
    engine.run()
