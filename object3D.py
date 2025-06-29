import numpy as np

from quaternion import Quaternion

class Object3D:
    def __init__(self, path, texture_id=None):
        self.vertices = []
        self.faces = []
        self.texcoords = []
        self.texture_id = None

        self.position = np.array([0.0, 0.0, 0.0])
        self.scale = np.array([1.0, 1.0, 1.0])
        self.rotation = Quaternion(0, 0, 0, 0) # Quaternion or rotation matrix
        self.pivot = np.array([0.0, 0.0, 0.0])

        self.load(path)
        self.texture_id = texture_id
        self.original_vertices = list(self.vertices)

    def load(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.strip().split()
                    vertex = list(map(float, parts[1:4]))
                    self.vertices.append(vertex)
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    uv = list(map(float, parts[1:3]))
                    self.texcoords.append(uv)
                elif line.startswith('f '):
                    parts = line.strip().split()[1:]
                    face = []
                    for p in parts:
                        v_indices = p.split('/')
                        v_idx = int(v_indices[0]) - 1
                        vt_idx = int(v_indices[1]) - 1 if len(v_indices) > 1 and v_indices[1] != '' else None
                        face.append((v_idx, vt_idx))
                    if len(face) == 3:
                        self.faces.append(face)
                    elif len(face) == 4:
                        self.faces.append([face[0], face[1], face[2]])
                        self.faces.append([face[0], face[2], face[3]])

    def draw(self, wireframe=False, textured=False):
        from OpenGL.GL import glEnable, glDisable, glBindTexture, glColor3f, glBegin, glEnd, glTexCoord2f, glVertex3fv, GL_TEXTURE_2D, GL_TRIANGLES, GL_LINE_LOOP

        if textured and self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glColor3f(1, 1, 1)
        if wireframe:
            for face in self.faces:
                glBegin(GL_LINE_LOOP)
                for vertex in face:
                    v_idx = vertex[0]
                    glVertex3fv(self.vertices[v_idx])
                glEnd()
        else:
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for v_idx, vt_idx in face:
                    if textured and vt_idx is not None and self.texcoords:
                        glTexCoord2f(*self.texcoords[vt_idx])
                    glVertex3fv(self.vertices[v_idx])
            glEnd()

        if self.texture_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def rotate(self, quaternion):
        """Applique une rotation à tous les sommets de l'objet autour du pivot."""
        q = quaternion.normalize()
        rotated_vertices = []

        for vertex in self.vertices:
            # Translation par rapport au pivot
            relative = np.array(vertex) - self.pivot
            rotated = q.rotate_vector(relative)
            rotated_vertex = np.array(rotated) + self.pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self.vertices = rotated_vertices
        self.rotation = q if self.rotation is None else (q * self.rotation).normalize()

    def rotate_with_matrix(self, matrix):
        """
        Applique une rotation par matrice 3x3 autour du pivot à tous les sommets de l'objet.
        Met aussi à jour self.rotation en tant que matrice cumulée.
        """
        rotated_vertices = []

        for vertex in self.vertices:
            relative = np.array(vertex) - self.pivot
            rotated = matrix @ relative
            rotated_vertex = rotated + self.pivot
            rotated_vertices.append(rotated_vertex.tolist())

        self.vertices = rotated_vertices

        # Mise à jour de la rotation cumulée
        if isinstance(self.rotation, np.ndarray):
            self.rotation = matrix @ self.rotation
        elif self.rotation is None or self.rotation == 0:  # cas initial si mal initialisé
            self.rotation = matrix
        else:
            self.rotation = matrix @ np.identity(3)  # fallback

    # def transform(self):
    #     """Met à jour self.vertices depuis self.original_vertices avec scale, rotation, translation."""
    #     transformed = []
    #     q = self.rotation or Quaternion(1, 0, 0, 0)
    #     for v in self.original_vertices:
    #         v = np.array(v) * self.scale
    #         v = q.rotate_vector(v - self.pivot) + self.pivot
    #         v = v + self.position
    #         transformed.append(v.tolist())
    #     self.vertices = transformed

