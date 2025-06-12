""" Classe que representa uma partícula 3D animada no contexto de uma animação procedural, onde ela sofre várias 
transformações ao longo do tempo: queda, quique, dissolução, formação de espiral, reorganização, compressão e explosão"""
from Ponto import *
import random
import math

class Particle:
    def __init__(self, position): # Inicialização de variáveis globais
        # --- POSIÇÃO E MOVIMENTO INICIAL ---
        self.original_position = Ponto(*position)  # Posição de origem 
        self.position = Ponto(*position)           # Posição atual da partícula
        self.velocity = Ponto(0, 0, 0)             # Velocidade atual

        # --- FLAGS DE ESTADO GERAL ---
        self.alive = True               # Controla se a partícula ainda está ativa
        self.tocou_chao = False         # Marca se já colidiu com o chão

        # --- FASE: FORMAÇÃO DE ESPIRAL ---
        self.em_espiral = False                     # Controla se a partícula está em espiral
        self.espiral_delay_frames = 0               # Atraso antes da espiral começar
        self.frames_esperando_espiral = 0           # Contador de espera para o início da espiral
        self.theta = 0.0                            # Ângulo atual da espiral
        self.theta_offset = random.uniform(0, 2 * math.pi)  # Deslocamento inicial de fase
        self.altura_espiral = 0.0                   # Altura acumulada durante a espiral
        self.chao = 0.0                             # Nível do chão

        self.cx = self.position.x + random.uniform(-1.0, 1.0)  # Centro horizontal inicial da espiral
        self.cz = self.position.z + random.uniform(-1.0, 1.0)

        self.target_cx = 0.0                        # Centro de convergência do redemoinho
        self.target_cz = 0.0
        self.convergence_rate = 0.05                # Velocidade de convergência do centro

        self.theta_velocidade = 0.2                 # Velocidade angular da espiral
        self.raio_ruido = 0.0                       # Variação no raio para dar naturalidade
        self.altura_max = 3.5                       # Altura máxima da espiral

        # --- FASE: REAGRUPAMENTO ---
        self.reagrupando = False  # Indica se a partícula está reagrupando
        self.reagrupando_t = 0.0  # Tempo de interpolação entre posição atual e original

        # --- FASE: COMPRESSÃO ---
        self.comprimindo = False            # Indica se a partícula está sendo comprimida
        self.compressao_frames_totais = 180 # Total de frames para a compressão
        self.compressao_frame_atual = 0     # Contador de frames atuais na compressão

        # --- FASE: EXPLOSÃO COLORIDA ---
        self.explodindo = False
        self.t_explosao = 0.0
        self.explosao_velocidade = Ponto(0, 0, 0)  # Velocidade durante explosão
        self.cor = [0.1, 0.1, 0.1]                 # Cor atual da partícula

    # Função usada para preparar a partícula para subir em espiral, com parâmetros aleatórios que garantem um visual 
    # mais fluido — cada partícula sobe com velocidade, raio e tempo de início diferentes.
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

    # Seta a partícula para iniciar a compressão
    def iniciar_compressao(self):
        self.comprimindo = True

    # MÉTODO PRINCIPAL DA CLASSE: Atualiza a posição da partícula em cada frame
    def update(self):
        # =========================================
        # FASE 1 – QUEDA LIVRE VERTICAL
        # =========================================
        if not self.tocou_chao: # Se ainda não tocou o chão
            # Simula a queda com gravidade
            self.velocity.y -= 0.005  # Gravidade
            self.position.y += self.velocity.y # Atualiza a posição vertical

            # Mantém x e z fixos durante a queda
            self.position.x = self.original_position.x
            self.position.z = self.original_position.z

            # Detecção de contato com o chão
            if self.position.y <= 0: 
                self.position.y = 0 # Reseta a posição y para o chão
                self.tocou_chao = True # Marca que tocou o chão

                # Inicia movimento de quique
                self.velocity.y = random.uniform(0.13, 0.2) # Quique
                # Quando a partícula toca o chão, recebe uma velocidade aleatória nos eixos x e z
                self.velocity.x = random.uniform(-0.07, 0.07)
                self.velocity.z = random.uniform(-0.04, 0.04)

        # =========================================
        # FASE 2 – QUIQUE E ESPERA PELA ESPIRAL
        # =========================================
        else: # Se já tocou o chão
            self.velocity.y -= 0.005  # Gravidade contínua
            self.position.x += self.velocity.x # Aplica a velocidade em x
            self.position.y += self.velocity.y # Aplica o quique
            self.position.z += self.velocity.z # Aplica a velocidade em z

            if self.position.y <= 0: 
                self.position.y = 0 # Reseta a posição y para o chão
                self.velocity.y *= -0.8  # Rebote vertical
                self.velocity.x *= 0.2   # Amortecimento lateral
                self.velocity.z *= 0.2   # Realizando espalhamento

                # Quando o rebote enfraquece o suficiente, inicia a espera para a espiral
                if abs(self.velocity.y) < 0.005:
                    if not self.em_espiral:
                        if self.frames_esperando_espiral < self.espiral_delay_frames:
                            self.frames_esperando_espiral += 1
                        else:
                            self.em_espiral = True # Inicia a fase de espiral
                    else:
                        self.alive = False 

        # =========================================
        # FASE 3 – FORMAÇÃO DE ESPIRAL
        # =========================================
        if self.em_espiral: # Lógica de espiral começa
            self.theta += self.theta_velocidade
            self.position.y += 0.05  # Sobe lentamente

            altura = self.position.y - self.chao
            t = min(altura / self.altura_max, 1.0)
            t = 1 - pow(1 - t, 3.5)  # Suaviza a curva

            raio_base = 3.5 * (1 - t) + 0.05 * t
            raio = raio_base + self.raio_ruido

            # Convergência suave para o centro
            self.cx += (self.target_cx - self.cx) * self.convergence_rate
            self.cz += (self.target_cz - self.cz) * self.convergence_rate

            # Movimento circular em espiral
            self.position.x = self.cx + raio * math.cos(self.theta + self.theta_offset)
            self.position.z = self.cz + raio * math.sin(self.theta + self.theta_offset)

            # Pequeno ruído natural
            self.position.x += random.uniform(-0.002, 0.002)
            self.position.z += random.uniform(-0.002, 0.002)

            # Ao atingir altura máxima, inicia reorganização
            if altura >= self.altura_max * 0.98:
                self.reagrupando = True
                self.reagrupando_t = 0.0
                self.em_espiral = False

        # =========================================
        # FASE 4 – REAGRUPAMENTO SUAVE
        # =========================================
        if self.reagrupando: # Lógica de reagrupamento começa
            self.reagrupando_t += 0.01 # Incrementa o tempo de reagrupamento
            t = min(self.reagrupando_t, 1.0) # Limita t a 1.0

            # Interpolação suave entre a posição atual e a posição original
            self.position.x = (1 - t) * self.position.x + t * self.original_position.x
            self.position.y = (1 - t) * self.position.y + t * self.original_position.y
            self.position.z = (1 - t) * self.position.z + t * self.original_position.z

            if t >= 1.0:
                self.reagrupando = False # Finaliza a fase de reagrupamento
                self.comprimindo = True  # Inicia a fase de compressão

        # =========================================
        # FASE 5 – COMPRESSÃO CENTRAL
        # =========================================
        if self.comprimindo: # Lógica de compressão começa
            target = Ponto(0, 2, 0)  # Ponto de convergência
            t = self.compressao_frame_atual / self.compressao_frames_totais # Calcula o fator de interpolação baseado no frame atual
            t = min(t, 1.0) # Limita t a 1.0

            # Interpolação da posição atual até o ponto de compressão
            self.position.x = (1 - t) * self.position.x + t * target.x
            self.position.y = (1 - t) * self.position.y + t * target.y
            self.position.z = (1 - t) * self.position.z + t * target.z

            self.compressao_frame_atual += 1 # Avança o frame da compressão

            if self.compressao_frame_atual >= self.compressao_frames_totais:
                self.comprimindo = False # Finaliza a fase de compressão
                self.explodindo = True # Inicia a fase de explosão
                self.t_explosao = 0.0 # Reseta o tempo de explosão
                self.explosao_velocidade = Ponto( # Define uma velocidade aleatória para a explosão da partícula
                    random.uniform(-0.2, 0.2),
                    random.uniform(0.2, 0.6),
                    random.uniform(-0.2, 0.2)
                )
                self.cor = [random.random(), random.random(), random.random()] # Cor aleatória para explosão

        # =========================================
        # FASE 6 – EXPLOSÃO COLORIDA
        # =========================================
        if self.explodindo: # Lógica de explosão começa
            self.t_explosao += 0.01 # Incrementa o tempo de explosão
            # Atualiza a posição da partícula durante a explosão
            self.position.x += self.explosao_velocidade.x
            self.position.y += self.explosao_velocidade.y
            self.position.z += self.explosao_velocidade.z

            # Efeito de gravidade na explosão
            self.explosao_velocidade.y -= 0.01

            # Após um tempo, partícula finaliza
            if self.t_explosao > 7.0:
                self.explodindo = False
                self.alive = False
