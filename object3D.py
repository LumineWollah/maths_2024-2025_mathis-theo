import numpy as np
from quaternion import Quaternion

class Object3D:
    def __init__(self, path, texture_id=None):
        self._vertices = []
        self._faces = []
        self._texcoords = []

        self._position = np.array([0.0, 0.0, 0.0])
        self._scale = np.array([1.0, 1.0, 1.0])
        self._rotation = Quaternion(1, 0, 0, 0)
        self._sheer = np.identity(3)
        self._pivot = np.array([0.0, 0.0, 0.0])
        self._rotation_matrix = np.identity(3) 
        self._use_rotation_matrix = False # Flag pour savoir quelle rotation utiliser

        self.load(path)
        self._texture_id = texture_id
        self._original_vertices = list(self._vertices)
        self.apply_transformations()

    def load(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.strip().split()
                    vertex = list(map(float, parts[1:4]))
                    self._vertices.append(vertex)
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    uv = list(map(float, parts[1:3]))
                    self._texcoords.append(uv)
                elif line.startswith('f '):
                    parts = line.strip().split()[1:]
                    face = []
                    for p in parts:
                        v_indices = p.split('/')
                        v_idx = int(v_indices[0]) - 1
                        vt_idx = int(v_indices[1]) - 1 if len(v_indices) > 1 and v_indices[1] != '' else None
                        face.append((v_idx, vt_idx))
                    if len(face) == 3:
                        self._faces.append(face)
                    elif len(face) == 4:
                        self._faces.append([face[0], face[1], face[2]])
                        self._faces.append([face[0], face[2], face[3]])

    def draw(self, wireframe=False, textured=False):
        from OpenGL.GL import glEnable, glDisable, glBindTexture, glColor3f, glBegin, glEnd, glTexCoord2f, glVertex3fv, GL_TEXTURE_2D, GL_TRIANGLES, GL_LINE_LOOP
        
        if textured and self._texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glColor3f(1, 1, 1)
        if wireframe:
            for face in self._faces:
                glBegin(GL_LINE_LOOP)
                for vertex in face:
                    v_idx = vertex[0]
                    glVertex3fv(self._vertices[v_idx])
                glEnd()
        else:
            glBegin(GL_TRIANGLES)
            for face in self._faces:
                for v_idx, vt_idx in face:
                    if textured and vt_idx is not None and self._texcoords:
                        glTexCoord2f(*self._texcoords[vt_idx])
                    glVertex3fv(self._vertices[v_idx])
            glEnd()

        if self._texture_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def apply_transformations(self):
        transformed_vertices = []
        for vertex in self._original_vertices:
            relative = np.array(vertex) - self._pivot
            # Échelle
            scaled = relative * self._scale
            # Cisaillement
            sheared = self._sheer @ scaled
            # Rotation (Quaternion ou Matrice)
            if self._use_rotation_matrix:
                rotated = self._rotation_matrix @ sheared
            else:
                rotated = self._rotation.rotate_vector(sheared)
            # Translation
            translated = rotated + self._pivot + self._position
            transformed_vertices.append(translated.tolist())
        self._vertices = transformed_vertices

    def rotate(self, quaternion):
        q = quaternion.normalize()
        self._rotation = q * self._rotation
        self._use_rotation_matrix = False
        self.apply_transformations()

    def set_rotation(self, quaternion):
        self._rotation = quaternion.normalize()
        self._use_rotation_matrix = False
        self.apply_transformations()

    def translate(self, dx, dy, dz):
        self._position += np.array([dx, dy, dz])
        self.apply_transformations()

    def set_position(self, x, y, z):
        self._position = np.array([x, y, z])
        self.apply_transformations()

    def scale(self, sx, sy, sz):
        self._scale += np.array([sx, sy, sz])
        self.apply_transformations()

    def set_scale(self, x, y, z):
        self._scale = np.array([x, y, z])
        self.apply_transformations()

    def shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        new_shear = np.array([
            [1,  xy, xz],
            [yx, 1,  yz],
            [zx, zy, 1 ]
        ])
        self._sheer = new_shear @ self._sheer
        self.apply_transformations()

    def set_shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        self._sheer = np.array([
            [1,  xy, xz],
            [yx, 1,  yz],
            [zx, zy, 1 ]
        ])
        self.apply_transformations()

    def rotateM(self, matrix):
        self._rotation_matrix = matrix @ self._rotation_matrix
        self._use_rotation_matrix = True
        self.apply_transformations()

    def set_rotationM(self, matrix):
        self._rotation_matrix = matrix
        self._use_rotation_matrix = True
        self.apply_transformations()

    def set_pivot(self, x, y, z):
        self._pivot = np.array([x, y, z])

    def set_pivot_world(self, x, y, z):
        pivot_world = np.array([x, y, z])
        relative = pivot_world - self._position
        inv_rot = self._rotation.inverse()
        pivot_local = inv_rot.rotate_vector(relative)
        self._pivot = pivot_local
