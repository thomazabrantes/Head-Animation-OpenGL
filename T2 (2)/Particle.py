from Ponto import *
import random

class Particle:
    def __init__(self, position):
        self.original_position = Ponto(*position)
        self.position = Ponto(*position)
        self.velocity = Ponto(0, 0, 0)  # começa parada na vertical
        self.alive = True
        self.tocou_chao = False

    def update(self):
        if not self.tocou_chao:
            # Queda vertical: apenas y muda, x e z fixos
            self.velocity.y -= 0.005  # gravidade
            self.position.y += self.velocity.y
            self.position.x = self.original_position.x
            self.position.z = self.original_position.z

            if self.position.y <= 0:
                self.position.y = 0
                self.tocou_chao = True
                # inicia velocidades para quicar e espalhar
                self.velocity.y = random.uniform(0.13, 0.2)  # impulso maior = mais quicadas
                self.velocity.x = random.uniform(-0.07, 0.07)  # mais espalhamento lateral em X
                self.velocity.z = random.uniform(-0.04, 0.04)  # mais espalhamento lateral em Z
        else:
            # física após tocar o chão (quicar e espalhar)
            self.velocity.y -= 0.005
            self.position.x += self.velocity.x
            self.position.y += self.velocity.y
            self.position.z += self.velocity.z

            if self.position.y <= 0:
                self.position.y = 0
                self.velocity.y *= -0.8  # quica mais vezes
                self.velocity.x *= 0.2   # menos perda lateral
                self.velocity.z *= 0.2

                if abs(self.velocity.y) < 0.005:
                    self.alive = False


