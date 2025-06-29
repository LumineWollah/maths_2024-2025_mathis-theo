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
        """Applique une rotation à tous les sommets de l'objet autour du pivot."""
        q = quaternion.normalize()
        rotated_vertices = []

        for vertex in self._vertices:
            # Translation par rapport au pivot
            relative = np.array(vertex) - self._pivot
            rotated = q.rotate_vector(relative)
            rotated_vertex = np.array(rotated) + self._pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self._vertices = rotated_vertices
        self.rotation = q if self.rotation is None else (q * self.rotation).normalize()

    def rotate_with_matrix(self, matrix):
        """
        Applique une rotation par matrice 3x3 autour du pivot à tous les sommets de l'objet.
        Met aussi à jour self.rotation en tant que matrice cumulée.
        """
        rotated_vertices = []

        for vertex in self._vertices:
            relative = np.array(vertex) - self._pivot
            rotated = matrix @ relative
            rotated_vertex = rotated + self._pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self._vertices = rotated_vertices

        # Mise à jour de la rotation cumulée
        if isinstance(self._rotation, np.ndarray):
            self._rotation = matrix @ self._rotation
        elif self._rotation is None or self._rotation == 0:  # cas initial si mal initialisé
            self._rotation = matrix
        else:
            self._rotation = matrix @ np.identity(3)  # fallback

    def translate(self, dx, dy, dz):
        """
        Applique une translation simple aux sommets.
        """
        self.set_position(self._position[0] + dx, self._position[1] + dy, self._position[2] + dz)

    def set_position(self, x, y, z):
        """
        Applique une translation simple aux sommets.
        """
        translation = np.array([x, y, z])
        self._position = translation

        translated_vertices = []
        for vertex in self._vertices:
            translated_vertex = np.array(vertex) + translation
            translated_vertices.append(translated_vertex.tolist())

        self._vertices = translated_vertices

    def scale(self, sx, sy, sz):
        """
        Applique un scaling autour du pivot.
        """
        self.set_scale(self._scale[0] + sx, self._scale[1] + sy, self._scale[2] + sz)

    def set_scale(self, x, y, z):
        """Applique une mise à l'échelle absolue à partir des sommets d'origine."""
        self._scale = np.array([x, y, z])
        scaled_vertices = []

        for vertex in self._original_vertices:
            relative = np.array(vertex) - self._pivot
            scaled = relative * self._scale
            scaled_vertex = scaled + self._pivot
            scaled_vertices.append(scaled_vertex.tolist())

        self._vertices = scaled_vertices

    def shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        """
        Applique un cisaillement RELATIF en composant avec le cisaillement existant (_sheer).
        Utilise la fonction shear() pour mettre à jour les sommets de manière absolue.
        """
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
        """
        Applique un cisaillement absolu à l'objet autour du pivot.
        Met à jour self.vertices et self._sheer.
        """
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

