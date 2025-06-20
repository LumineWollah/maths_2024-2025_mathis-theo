# TODO
# - Composé de rotations avec quaternons, cisaillement, scalling, translation avec quaternon
# - Scènes

# Remarques
# - Rotation faites avec openGL et pas une implementation maths pure, est-ce un problème ? (Sachant qu'on a toujours les fichiers avec l'implémentation maths)

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
from object import *
from camera import Camera
from keymap import keymap

class Engine():
    def __init__(self):
        pygame.init()
        self.running = True
        self.screen_size = SCREEN_SIZE
        self.screen = pygame.display.set_mode((800,600), DOUBLEBUF | OPENGL)
        self.clock = pg.time.Clock()
        self.surf = pg.surface.Surface(SCREEN_SIZE)
        self.skybox_texture = self.load_skybox("assets/skybox/")
        self.camera = Camera()

        self.scene = [
            Sphere(),
        ]

    def run(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, SCREEN_SIZE[0]/SCREEN_SIZE[1], 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        camera = Camera()
        clock = pygame.time.Clock()

        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

        cube_obj = self.load_obj('assets/objs/cube.obj')
        cube_tex = self.load_texture('assets/textures/placeholder.png')

        # angle = 0.0
        rotation_q = Quaternion(1, 0, 0, 0)

        mouse_control = False
        wireframe = False
        texture = False
        running = True
        while running:
            dt = clock.tick(60) / 1000
            # angle += 90 * dt # Rotation matrice

            angle_speed = 90  # deg/s
            angle_rad = radians(angle_speed * dt)
            half = angle_rad / 2
            sin_half = math.sin(half)
            axis = (1, 0.75, 0.5)
            delta_q = Quaternion(
                math.cos(half),
                axis[0] * sin_half,
                axis[1] * sin_half,
                axis[2] * sin_half
            )
            rotation_q = (delta_q * rotation_q).normalize()

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
                        camera.process_mouse_motion(dx, dy)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and mouse_control:
                        mouse_control = False
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                    if event.key == keymap["wireframe"]:
                        wireframe = not wireframe
                    if event.key == keymap["texture"]:
                        texture = not texture

            keys = pygame.key.get_pressed()
            camera.update_position(keys, dt)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            camera.apply_view()

            self.draw_skybox(self.skybox_texture)

            self.draw_axes(length=5.0, width=5.0)

            rot = rotation_q.to_rotation_matrix()
            pivot = (1.0, 1.0, 1.0)
            glPushMatrix()
            # glTranslatef(0, 0, 0) # Rotation matrice
            # glRotatef(angle, 0, 1, 0)  # Rotation matrice
            glTranslatef(*pivot)
            glMultMatrixf([
                rot[0][0], rot[1][0], rot[2][0], 0.0,
                rot[0][1], rot[1][1], rot[2][1], 0.0,
                rot[0][2], rot[1][2], rot[2][2], 0.0,
                0.0,       0.0,       0.0,       1.0
            ])
            glTranslatef(*(-np.array(pivot)))
            self.draw_obj(*cube_obj, texture_id=cube_tex, wireframe=wireframe, texture=texture)  
            glPopMatrix()

            m = glGetFloatv(GL_MODELVIEW_MATRIX).copy()
            # Supprimer la translation
            m[3][0] = m[3][1] = m[3][2] = 0.0
            self.draw_axes_overlay(m)

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
        print(vertices)
        print(faces)
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
