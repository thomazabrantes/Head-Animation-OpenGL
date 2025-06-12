""" Segundo Trabalho de CG - 2025/1: Animação procedural
Autores: Breno Spohr e Thomaz Abrantes 
Data: Junho de 2025
Disciplina: Computação Gráfica
Instituição de Ensino: Escola Politécnica - PUCRS
Trabalho baseado no material cedido pela Professora Soraia Raupp Musse
"""
#import random
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Objeto3D import *

from Particle import Particle

particles = []
espiral_ativa = False
camera_pos = [0.0, 6.0, -10.0]
camera_target = [0.0, 0.0, 0.0]
camera_up = [0.0, 1.0, 0.0]
camera_speed = 0.3
is_paused = False

# --- VARIÁVEIS GLOBAIS DE ROTAÇÃO ---
rotation_sequence = [ # Sequência de rotações simulam os movimentos que a cabeça faz no início do vídeo
    # Com base em algumas simulações feitas no Blender, obteve-se os seguintes valores:
    (0, -5, 0),     # Cabeça olhando para a esquerda da tela (estado inicial)   
    (10, -5, 0),    # Ainda olhando para a esquerda tela, cabeça se inclina para trás    
    (15, -10, 0),   # Cabeça se inclina mais para trás e olha mais para a esquerda da tela
    (15, 10, 0),    # Cabeça começa a olhar para a direita da tela      
    (-12, 15, 0),   # Cabeça olha mais para a direita e vai olhando para baixo    
    (-13, 20, 0),   # Cabeça olha mais para a direira e mais para baixo    
    (15, 20, 5),    # Cabeça volta a olhar para cima e se inclina na horizontal    
    (18, 15, 5),    # Cabeça olha mais pra cima e volta a olhar em direção à esquerda da tela
    (20, -5, 5)     # Cabeça olha mais em direção à esquerda da tela
]
rotation_index = 0                  # Índice da rotação atual na sequência
rotation_active = False             # Indica se as rotações estão ativas
frame_counter = 0                   # Contador de frames usados na interpolação atual
current_rotation = [0.0, 0.0, 0.0]  # Rotação atual aplicada ao objeto
target_rotation = [0.0, 0.0, 0.0]   # Próxima rotação alvo na sequência
interpolating = False               # Indica se está interpolando para a próxima rotação
rotation_step = [0.0, 0.0, 0.0]     # Incrementos por frame para interpolar a rotação
frames_to_interpolate = 10          # Quantidade de frames para completar a interpolação

# --- VARIÁVEIS GLOBAIS DE TRANSLAÇÃO ---
falling = False         # Indica se a cabeça está em queda
head_y = 0.0            # Posição atual da cabeça
head_speed = 0.0        # Velocidade vertical da cabeça
gravity = -0.01         # Aceleração aplicada na queda
impact_threshold = 0.0  # Posição Y onde ocorre o impacto com o chão
start_y = 0.0           # Posição inicial da cabeça antes de subir
target_y = 0.0          # Altura final ao fim da subida
dy_per_frame = 0.0      # Variação de altura por frame durante a subida
interpolating_y = False # Indica se a cabeça está interpolando a subida

o:Objeto3D

def init():
    global o
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    o = Objeto3D()
    o.LoadFile('Human_Head.obj')

    DefineLuz()
    PosicUser()

def DefineLuz():
    # Define cores para um objeto dourado
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]  # PosiÃ§Ã£o da Luz
    especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable(GL_COLOR_MATERIAL)

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    # Define os parametros da luz nÃºmero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Configura a matriz da projeção perspectiva (FOV, proporção da tela, distância do mínimo antes do clipping, distância máxima antes do clipping
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    gluPerspective(60, 16/9, 0.01, 50)  # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #Especifica a matriz de transformação da visualização
    # As três primeiras variáveis especificam a posição do observador nos eixos x, y e z
    # As três próximas especificam o ponto de foco nos eixos x, y e z
    # As três últimas especificam o vetor up
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    #gluLookAt(-2, 10, -camera_distance, 0, 0, 0, 0, 1.0, 0)

def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def DesenhaPiso():
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

def desenha():
    glLoadIdentity()
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],
        camera_target[0], camera_target[1], camera_target[2],
        camera_up[0], camera_up[1], camera_up[2]
    )

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    atualizar_particulas()

    DesenhaPiso()

    if not particles:
        glPushMatrix()
        glTranslatef(0.0, head_y, 0.0)  # Aplica altura vertical da queda
        o.Desenha() # Isso desenha os polígonos
        o.DesenhaWireframe() # Isso desenha as arestas
        o.DesenhaVertices()
        glPopMatrix()

    else:    
        desenhar_particulas()

    glutSwapBuffers()
    pass

def teclado(key, x, y):
    global rotation_active, is_paused, particles, falling, head_y, head_speed, espiral_ativa
    global current_rotation, rotation_index, frame_counter, interpolating
    
    key = key.decode("utf-8")

    if key == 'p': # Quando a tecla P é pressionada, a animação começa
        if not particles:
            rotation_active = True
    elif key == 'w':  # Frente
        camera_pos[2] += camera_speed
        camera_target[2] += camera_speed
    elif key == 's':  # Trás
        camera_pos[2] -= camera_speed
        camera_target[2] -= camera_speed
    elif key == 'd':  # Esquerda
        camera_pos[0] -= camera_speed
        camera_target[0] -= camera_speed
    elif key == 'a':  # Direita
        camera_pos[0] += camera_speed
        camera_target[0] += camera_speed
    elif key == 'q':  # Para cima
        camera_pos[1] += camera_speed
        camera_target[1] += camera_speed
    elif key == 'e':  # Para baixo
        camera_pos[1] -= camera_speed
        camera_target[1] -= camera_speed
    elif key == ' ':  # Barra de espaço para Play/Pause
        is_paused = not is_paused

"""Função para manter as proporções mesmo quando a janela é redimensinada"""
def redimensionar(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = w / h if h > 0 else 1
    gluPerspective(60, aspect, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)

# Funções de coordenção e gerenciamento de partículas

"""Gera partículas com base na posição atual dos vértices do modelo"""
def gerar_particulas(vertices):
    global particles
    particles = []
    for v in vertices:
        offset = (
        v.x,
        max(v.y, 0),
        v.z
    )
        p = Particle(offset)
        particles.append(p)

"""Atualiza o estado das partículas, incluindo rotação, subida, queda e movimento"""
def atualizar_particulas():
    global rotation_index, rotation_active, frame_counter, interpolating
    global current_rotation, target_rotation, rotation_step
    global falling, head_y, head_speed
    global start_y, target_y, dy_per_frame, interpolating_y
    global espiral_ativa
    if is_paused:
        return
    if rotation_active and not particles:
        if not interpolating:
            if rotation_index < len(rotation_sequence):
                target_rotation = rotation_sequence[rotation_index]
                rotation_step = [
                    (target_rotation[0] - current_rotation[0]) / frames_to_interpolate,
                    (target_rotation[1] - current_rotation[1]) / frames_to_interpolate,
                    (target_rotation[2] - current_rotation[2]) / frames_to_interpolate
                ]
                interpolating = True
                frame_counter = 0

                # Se for a última rotação (antes da queda), iniciar interpolação da subida
                if target_rotation == (20, -5, 5):
                    start_y = head_y
                    target_y = 3.0
                    dy_per_frame = (target_y - start_y) / frames_to_interpolate
                    interpolating_y = True
            else:
                # Rotações concluídas, inicia queda
                falling = True
                rotation_active = False

        else:
            # Interpolação de rotação
            centro = Ponto(0, 0, 0)
            for v in o.vertices:
                centro.x += v.x
                centro.y += v.y
                centro.z += v.z
            centro.x /= len(o.vertices)
            centro.y /= len(o.vertices)
            centro.z /= len(o.vertices)

            for v in o.vertices:
                v.rotaciona_em_torno(centro, rotation_step[0], rotation_step[1], rotation_step[2])

            current_rotation[0] += rotation_step[0]
            current_rotation[1] += rotation_step[1]
            current_rotation[2] += rotation_step[2]

            # Interpolação da subida
            if interpolating_y:
                head_y += dy_per_frame

            frame_counter += 1
            if frame_counter >= frames_to_interpolate:
                current_rotation = list(target_rotation)
                interpolating = False
                interpolating_y = False  # Finaliza a interpolação vertical
                head_y = target_y  # Garante que o valor final seja preciso
                rotation_index += 1

    # Controle da queda após rotações
    if falling and not particles:
        head_speed += gravity
        head_y += head_speed

        if head_y <= impact_threshold:
            head_y = impact_threshold
            falling = False
            gerar_particulas(o.vertices) # Gera partículas a partir dos vértices do modelo após a queda

    # Verifica se todas estabilizaram para ativar espiral
    if not espiral_ativa and all(not p.alive for p in particles):
        espiral_ativa = True
        for p in particles:
            p.reiniciar_para_espiral()

    # Atualização das partículas
    for p in particles:
        if p.alive:
            p.update()

    # Verifica se todas partículas estão reagrupadas e prontas para compressão
    if espiral_ativa and all(not p.alive and not p.comprimindo and not p.explodindo for p in particles):
        for p in particles:
            p.iniciar_compressao()

"""Renderiza as partículas na tela"""
def desenhar_particulas():
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for p in particles:
        glColor3f(*p.cor)
        glVertex3f(p.position.x, p.position.y, p.position.z)
    glEnd()

def main():

    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)

    # Especifica o tamnho inicial em pixels da janela GLUT
    glutInitWindowSize(400, 400)

    # Especifica a posição de início da janela
    glutInitWindowPosition(100, 100)

    # Cria a janela passando o título da mesma como argumento
    glutCreateWindow(b'Computacao Grafica - 3D')

    # Função responsável por fazer as inicializações
    init()

    # Registra a funcao callback de redesenho da janela de visualizacao
    glutDisplayFunc(desenha)

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)

    # Função responsável por fazer a redimensão
    glutReshapeFunc(redimensionar)

    glutIdleFunc(glutPostRedisplay)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
