import numpy as np

from quaternion import Quaternion

class Object3D:
    def __init__(self, path, texture_id=None):
        self._vertices = []
        self._faces = []
        self._texcoords = []

        self._position = np.array([0.0, 0.0, 0.0])
        self._scale = np.array([1.0, 1.0, 1.0])
        self._rotation = Quaternion(0, 0, 0, 0) # Quaternion or rotation matrix
        self._sheer = np.array([[1, 0, 0], [0, 1, 0] ,[0, 0, 1]])
        self._pivot = np.array([0.0, 0.0, 0.0])

        self.load(path)
        self._texture_id = texture_id
        self._original_vertices = list(self._vertices)

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

    def rotate(self, quaternion):
        q = quaternion.normalize()
        composed_rotation = q * self._rotation
        self.set_rotation(composed_rotation)

    def set_rotation(self, quaternion):
        q = quaternion.normalize()
        rotated_vertices = []

        for vertex in self._original_vertices:
            # Translation par rapport au pivot
            relative = np.array(vertex) - self._pivot
            rotated = q.rotate_vector(relative)
            rotated_vertex = np.array(rotated) + self._pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self._vertices = rotated_vertices
        self._rotation = q

    def rotateM(self, matrix):
        if isinstance(self._rotation, np.ndarray):
            composed_rotation = matrix @ self._rotation
        else:
            composed_rotation = matrix

        self.set_rotationM(composed_rotation)

    def set_rotationM(self, matrix):
        rotated_vertices = []

        for vertex in self._original_vertices:
            relative = np.array(vertex) - self._pivot
            rotated = matrix @ relative
            rotated_vertex = rotated + self._pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self._vertices = rotated_vertices
        self._rotation = matrix 

    def translate(self, dx, dy, dz):
        self.set_position(self._position[0] + dx, self._position[1] + dy, self._position[2] + dz)

    def set_position(self, x, y, z):
        translation = np.array([x, y, z])
        self._position = translation

        translated_vertices = []
        for vertex in self._vertices:
            translated_vertex = np.array(vertex) + translation
            translated_vertices.append(translated_vertex.tolist())

        self._vertices = translated_vertices

    def scale(self, sx, sy, sz):
        self.set_scale(self._scale[0] + sx, self._scale[1] + sy, self._scale[2] + sz)

    def set_scale(self, x, y, z):
        self._scale = np.array([x, y, z])
        scaled_vertices = []

        for vertex in self._original_vertices:
            relative = np.array(vertex) - self._pivot
            scaled = relative * self._scale
            scaled_vertex = scaled + self._pivot
            scaled_vertices.append(scaled_vertex.tolist())

        self._vertices = scaled_vertices

    def shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        new_shear = np.array([
            [1,  xy, xz],
            [yx, 1,  yz],
            [zx, zy, 1 ]
        ])

        composed_shear = np.dot(new_shear, self._sheer)

        xy_new = composed_shear[0,1]
        xz_new = composed_shear[0,2]
        yx_new = composed_shear[1,0]
        yz_new = composed_shear[1,2]
        zx_new = composed_shear[2,0]
        zy_new = composed_shear[2,1]

        self.set_shear(xy=xy_new, xz=xz_new, yx=yx_new, yz=yz_new, zx=zx_new, zy=zy_new)

    def set_shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        shear_matrix = np.array([
            [1,  xy, xz],
            [yx, 1,  yz],
            [zx, zy, 1 ]
        ])

        # Appliquer le cisaillement aux sommets originaux
        sheared_vertices = []
        for vertex in self._original_vertices:
            relative = np.array(vertex) - self._pivot
            sheared = np.dot(shear_matrix, relative)
            sheared_vertex = sheared + self._pivot
            sheared_vertices.append(sheared_vertex.tolist())

        self._vertices = sheared_vertices
        self._sheer = shear_matrix

