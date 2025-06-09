from Ponto import *
import random
import math

class Particle:
    def __init__(self, position):
        self.original_position = Ponto(*position)
        self.position = Ponto(*position)
        self.velocity = Ponto(0, 0, 0)
        self.alive = True
        self.tocou_chao = False
        self.em_espiral = False
        self.espiral_delay_frames = 0
        self.frames_esperando_espiral = 0

        # Parâmetros da espiral
        self.theta = 0.0
        self.theta_offset = random.uniform(0, 2 * math.pi)
        self.altura_espiral = 0.0
        self.chao = 0.0
        self.cx = self.position.x + random.uniform(-1.0, 1.0)
        self.cz = self.position.z + random.uniform(-1.0, 1.0)


        # Parâmetros de convergência e ruído
        self.target_cx = 0.0
        self.target_cz = 0.0
        self.convergence_rate = 0.05

        self.theta_velocidade = 0.2
        self.raio_ruido = 0.0
        self.altura_max = 3.5


    def rotate_around_point(self, point: Ponto, ang_x=0, ang_y=0, ang_z=0):
        self.position.x -= point.x
        self.position.y -= point.y
        self.position.z -= point.z

        if ang_x != 0:
            self.position.rotacionaX(ang_x)
        if ang_y != 0:
            self.position.rotacionaY(ang_y)
        if ang_z != 0:
            self.position.rotacionaZ(ang_z)

        self.position.x += point.x
        self.position.y += point.y
        self.position.z += point.z


    def reiniciar_para_espiral(self):
        self.em_espiral = False
        self.alive = True
        self.angulo = random.uniform(0, 360)
        self.altura_espiral = 0.0
        self.radius = random.uniform(0.2, 0.6)

        self.cx = self.position.x
        self.cz = self.position.z

        self.target_cx = 0.0
        self.target_cz = 0.0
        self.chao = self.position.y

        self.raio_ruido = random.uniform(-0.2, 0.2)
        self.theta_velocidade = random.uniform(0.2, 0.3)
        self.altura_max = random.uniform(2.3, 3.0)

        distancia = math.sqrt(self.position.x**2 + self.position.z**2)
        self.espiral_delay_frames = int(distancia * 80)
        self.frames_esperando_espiral = 0


    def update(self):
        if not self.tocou_chao:
            self.velocity.y -= 0.005
            self.position.y += self.velocity.y
            self.position.x = self.original_position.x
            self.position.z = self.original_position.z

            if self.position.y <= 0:
                self.position.y = 0
                self.tocou_chao = True
                self.velocity.y = random.uniform(0.13, 0.2)
                self.velocity.x = random.uniform(-0.07, 0.07)
                self.velocity.z = random.uniform(-0.04, 0.04)

        else:
            self.velocity.y -= 0.005
            self.position.x += self.velocity.x
            self.position.y += self.velocity.y
            self.position.z += self.velocity.z

            if self.position.y <= 0:
                self.position.y = 0
                self.velocity.y *= -0.8
                self.velocity.x *= 0.2
                self.velocity.z *= 0.2

                if abs(self.velocity.y) < 0.005:
                    if not self.em_espiral:
                        if self.frames_esperando_espiral < self.espiral_delay_frames:
                            self.frames_esperando_espiral += 1
                        else:
                            self.em_espiral = True
                    else:
                        self.alive = False

        # Movimento em espiral
        # Movimento em espiral (redemoinho afunilado e orgânico)
        if self.em_espiral:
            self.theta += self.theta_velocidade
            self.position.y += 0.05  # Subida vertical

            altura = self.position.y - self.chao
            t = min(altura / self.altura_max, 1.0)

            # Curva com afunilamento mais precoce (como easing out expo)
            t = 1 - pow(1 - t, 3.5)

            # Raio começa largo e afunila fortemente
            raio_base = 3.5 * (1 - t) + 0.05 * t
            raio = raio_base + self.raio_ruido

            # Convergência do centro do redemoinho
            self.cx += (self.target_cx - self.cx) * self.convergence_rate
            self.cz += (self.target_cz - self.cz) * self.convergence_rate

            self.position.x = self.cx + raio * math.cos(self.theta + self.theta_offset)
            self.position.z = self.cz + raio * math.sin(self.theta + self.theta_offset)

            # Ruído suave
            self.position.x += random.uniform(-0.002, 0.002)
            self.position.z += random.uniform(-0.002, 0.002)

            if self.position.y > self.chao + self.altura_max:
                self.alive = False
