# ************************************************
#   Linha.py
#   Define a classe Linha
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import Ponto

from random import randint as rand

""" Classe Linha """
class Linha:
    def __init__(self, a: Ponto, b: Ponto):
        self.a = a
        self.b = b

    def __init__(self, x1: float = 0, y1: float = 0, z1 : float = 0, x2: float = 0, y2: float = 0, z2: float = 0):
        self.a = Ponto(x1, y1, z1)
        self.b = Ponto(x2, y2, z2)

    """ Desenha a linha na tela atual """
    def desenhaLinha(self):
        glBegin(GL_LINES)
        
        glVertex3f(self.a.x, self.a.y, self.a.z)
        glVertex3f(self.b.x, self.b.y, self.b.z)

        glEnd()
