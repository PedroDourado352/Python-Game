# ==================== IMPORTAÇÕES ====================

import math    # Biblioteca padrão do Python para funções matemáticas (sin, cos, pi, etc.)
import sys     # Biblioteca padrão para interagir com o sistema (ex: encerrar o programa)
import random  # Biblioteca padrão para geração de números e escolhas aleatórias

import pygame  # Biblioteca externa de jogos 2D: janela, eventos, desenho, som, etc.

# Inicializa todos os módulos do pygame (gráficos, eventos, fontes, etc.)
pygame.init()

# ==================== CONSTANTES DO JOGO ====================

LARGURA, ALTURA = 960, 540   # Dimensões da janela em pixels (960 de largura, 540 de altura)
FPS = 60                      # Quadros por segundo — velocidade máxima de atualização do jogo
GRAVIDADE = 0.8               # Aceleração para baixo aplicada ao jogador a cada frame
FORCA_PULO = -15              # Velocidade vertical negativa ao pular (negativo = para cima)
VELOCIDADE = 6                # Velocidade horizontal do jogador em pixels por frame

# ==================== PALETA DE CORES (R, G, B) ====================

BRANCO       = (240, 240, 240)   # Branco levemente suavizado
PRETO        = (20, 20, 30)      # Preto com leve tom azulado (mais agradável visualmente)
AZUL_CEU     = (110, 180, 230)   # Azul claro usado no gradiente do fundo
AZUL_ESCURO  = (40, 60, 100)     # Azul escuro usado nas montanhas do fundo
VERDE        = (90, 200, 110)    # Verde principal das plataformas
VERDE_ESCURO = (50, 140, 70)     # Verde mais escuro usado no topo das plataformas
VERMELHO     = (230, 80, 80)     # Vermelho usado nos espinhos e na bandeira da meta
AMARELO      = (250, 210, 80)    # Amarelo usado no título e nas plataformas móveis
LARANJA      = (240, 140, 60)    # Laranja usado no efeito de glow do título
CINZA        = (120, 120, 130)   # Cinza usado nas dicas de controles e topo de plataformas especiais
ROXO_NEON    = (140, 0, 255)     # Roxo neon para efeitos de partículas
CIANO        = (0, 210, 255)     # Ciano (azul-turquesa) para detalhes do personagem e partículas
VERDE_NEON   = (0, 255, 120)     # Verde brilhante neon para partículas
ROSA_NEON    = (255, 50, 180)    # Rosa neon para partículas

# Lista com todas as cores neon — usada para escolher cores aleatórias em efeitos
CORES_GLITCH = [CIANO, ROXO_NEON, VERDE_NEON, ROSA_NEON, AMARELO]

# Lista de símbolos matemáticos que aparecem como partículas ao pular
FORMULAS = ["π", "Σ", "√2", "∫", "∂", "∞", "x²", "λ", "Δ", "θ", "f(x)", "n!"]

# ==================== CONFIGURAÇÃO DA JANELA ====================

# Cria a janela do jogo com as dimensões definidas acima
tela = pygame.display.set_mode((LARGURA, ALTURA))

# Define o título exibido na barra da janela
pygame.display.set_caption("πXEL RUN")

# Objeto responsável por controlar o tempo e limitar os FPS
clock = pygame.time.Clock()

# Fonte padrão usada no HUD (tempo, mortes, pulos) — Arial tamanho 24, negrito
fonte = pygame.font.SysFont("arial", 24, bold=True)

# Fonte grande usada nos títulos das telas (início, vitória) — Arial tamanho 56, negrito
fonte_grande = pygame.font.SysFont("arial", 56, bold=True)

# Fonte pequena usada nos símbolos matemáticos que aparecem como partículas — Arial tamanho 13, negrito
fonte_formula = pygame.font.SysFont("arial", 13, bold=True)


# ==================== CLASSE PARTICULA ====================

class Particula:
    # Representa um efeito visual temporário que aparece no jogo (triângulo, fórmula ou pixel)
    def __init__(self, x, y, tipo):
        self.x = float(x)   # Posição horizontal da partícula no mundo (convertida para float para movimento suave)
        self.y = float(y)   # Posição vertical da partícula no mundo
        self.tipo = tipo     # Tipo da partícula: "triangulo", "formula" ou "pixel"

        if tipo == "triangulo":
            # Partícula triangular — aparece atrás do jogador enquanto ele se move
            self.vel_x = random.uniform(-1.2, 1.2)    # Velocidade horizontal aleatória pequena
            self.vel_y = random.uniform(-1.8, -0.4)   # Velocidade vertical aleatória (sempre para cima)
            self.vida = random.randint(16, 26)         # Duração em frames antes de desaparecer
            self.vida_max = self.vida                  # Guarda o valor inicial para calcular transparência
            self.tamanho = random.randint(4, 9)        # Tamanho do triângulo em pixels
            self.cor = random.choice(CORES_GLITCH)     # Cor aleatória da lista neon

        elif tipo == "formula":
            # Partícula de fórmula matemática — aparece ao pular
            self.vel_x = random.uniform(-0.7, 0.7)    # Movimento horizontal leve
            self.vel_y = random.uniform(-2.8, -1.2)   # Sobe mais rápido que o triângulo
            self.vida = random.randint(40, 65)         # Dura mais frames (mais visível)
            self.vida_max = self.vida
            self.texto = random.choice(FORMULAS)       # Símbolo matemático aleatório (π, Σ, etc.)
            self.cor = random.choice([CIANO, VERDE_NEON, AMARELO, BRANCO])  # Cor clara para legibilidade

        elif tipo == "pixel":
            # Partícula quadrada — aparece quando o jogador morre (explosão) e no efeito glitch
            self.vel_x = random.uniform(-5, 5)         # Movimento horizontal mais intenso
            self.vel_y = random.uniform(-5, 1)         # Pode ir para cima ou levemente para baixo
            self.vida = random.randint(8, 22)          # Dura pouco (efeito rápido)
            self.vida_max = self.vida
            self.tamanho = random.randint(2, 5)        # Quadradinho pequeno
            self.cor = random.choice(CORES_GLITCH)

    def atualizar(self):
        # Move a partícula conforme sua velocidade
        self.x += self.vel_x
        self.y += self.vel_y
        self.vida -= 1  # Diminui a vida a cada frame; quando chegar a 0, a partícula é removida

        if self.tipo == "pixel":
            # Pixels sofrem gravidade leve — caem após o impulso inicial
            self.vel_y += 0.4

    def desenhar(self, superficie, camera_x):
        # Calcula a transparência: de 1.0 (opaco) até 0.0 (invisível) conforme a vida diminui
        alpha = self.vida / self.vida_max

        # Converte posição do mundo para posição na tela, descontando o deslocamento da câmera
        sx = int(self.x - camera_x)
        sy = int(self.y)

        # Escurece a cor proporcionalmente ao alpha (simulando transparência sem Surface extra)
        cor = tuple(int(c * alpha) for c in self.cor)

        if self.tipo == "triangulo":
            s = self.tamanho
            # Desenha um triângulo apontando para cima com vértices calculados a partir do centro
            pygame.draw.polygon(superficie, cor, [(sx, sy - s), (sx - s, sy + s), (sx + s, sy + s)])

        elif self.tipo == "formula":
            # Renderiza o símbolo matemático como texto e o coloca na tela
            txt = fonte_formula.render(self.texto, True, cor)
            superficie.blit(txt, (sx, sy))

        elif self.tipo == "pixel":
            # Desenha um quadrado pequeno na posição da partícula
            pygame.draw.rect(superficie, cor, (sx, sy, self.tamanho, self.tamanho))


# ==================== CLASSE JOGADOR ====================

class Jogador:
    def __init__(self, x, y):
        self.largura = 32    # Largura da hitbox do jogador em pixels
        self.altura = 48     # Altura da hitbox do jogador em pixels

        # pygame.Rect é o retângulo de colisão — define posição e tamanho do jogador
        self.rect = pygame.Rect(x, y, self.largura, self.altura)

        self.vel_x = 0          # Velocidade horizontal atual (pixels por frame)
        self.vel_y = 0          # Velocidade vertical atual (pixels por frame, positivo = cai)
        self.no_chao = False     # True se o jogador está em contato com uma plataforma abaixo
        self.pulos_restantes = 2 # Contador de pulos disponíveis (permite pulo duplo)
        self.spawn = (x, y)      # Posição inicial salva para respawnar ao morrer
        self.mortes = 0          # Contador de mortes acumuladas durante a sessão
        self.olhando_direita = True  # Direção que o personagem está virado (afeta efeitos visuais)

        self.particulas = []    # Lista de partículas ativas associadas ao jogador
        self.t = 0              # Contador de frames — usado para animações e temporizadores
        self.glitch_timer = 0   # Conta quantos frames o efeito de glitch ainda vai durar
        self.glitch_dx = 0      # Deslocamento horizontal do efeito de glitch

    def resetar(self):
        # Gera 18 partículas pixel no centro do jogador simulando uma "explosão" de morte
        for _ in range(18):
            self.particulas.append(Particula(self.rect.centerx, self.rect.centery, "pixel"))

        # Reposiciona o jogador na posição de spawn (início da fase)
        self.rect.x, self.rect.y = self.spawn

        # Zera velocidades e restaura pulos
        self.vel_x = 0
        self.vel_y = 0
        self.pulos_restantes = 2

        # Registra mais uma morte
        self.mortes += 1

    def atualizar(self, teclas, plataformas, perigos, meta):
        self.t += 1      # Avança o contador de frames
        self.vel_x = 0   # Reseta a velocidade horizontal a cada frame (movimento só se tecla pressionada)

        # Verifica se as teclas de movimento para a esquerda estão pressionadas
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VELOCIDADE     # Move para a esquerda
            self.olhando_direita = False

        # Verifica se as teclas de movimento para a direita estão pressionadas
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VELOCIDADE      # Move para a direita
            self.olhando_direita = True

        # Aplica gravidade: aumenta a velocidade de queda a cada frame
        self.vel_y += GRAVIDADE

        # Limita a velocidade de queda máxima para evitar que o jogador atravesse plataformas
        if self.vel_y > 18:
            self.vel_y = 18

        # ---- Movimento horizontal + colisão lateral ----

        # Move o rect horizontalmente
        self.rect.x += self.vel_x

        # Verifica colisão com cada plataforma após mover horizontalmente
        for p in plataformas:
            if self.rect.colliderect(p.rect):  # colliderect retorna True se os rects se sobrepõem
                if self.vel_x > 0:
                    # Movendo para a direita: encosta o lado direito do jogador na borda esquerda da plataforma
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    # Movendo para a esquerda: encosta o lado esquerdo do jogador na borda direita da plataforma
                    self.rect.left = p.rect.right

        # ---- Movimento vertical + colisão com o chão/teto ----

        # Move o rect verticalmente
        self.rect.y += self.vel_y
        self.no_chao = False  # Assume que não está no chão até verificar colisões

        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    # Caindo: o jogador pousou no topo da plataforma
                    self.rect.bottom = p.rect.top  # Alinha o rodapé do jogador com o topo da plataforma
                    self.vel_y = 0                 # Zera a queda
                    self.no_chao = True            # Marca que está no chão
                    self.pulos_restantes = 2       # Restaura os pulos ao tocar o chão
                elif self.vel_y < 0:
                    # Subindo: colidiu com a parte inferior de uma plataforma (teto)
                    self.rect.top = p.rect.bottom  # Empurra o jogador para baixo da plataforma
                    self.vel_y = 0                 # Zera o impulso para cima

        # ---- Efeito visual: rastro de triângulos ao se mover ----
        # A cada 3 frames em que o jogador se move, gera uma partícula atrás dele
        if self.vel_x != 0 and self.t % 3 == 0:
            # px: posição atrás do jogador (oposto à direção que ele olha)
            px = self.rect.centerx - (12 if self.olhando_direita else -12)
            py = self.rect.bottom - 10  # Próximo aos pés
            self.particulas.append(Particula(px, py, "triangulo"))

        # ---- Efeito de glitch periódico + burst de pixels ----
        # Acontece a cada 90 frames OU com 0.6% de chance aleatória por frame
        if self.t % 90 == 0 or (random.random() < 0.006):
            self.glitch_timer = random.randint(5, 12)   # Duração do efeito visual de glitch
            self.glitch_dx = random.randint(-10, 10)     # Deslocamento do distorção de glitch

            # Gera 12 partículas pixel espalhadas ao redor do centro do jogador
            for _ in range(12):
                self.particulas.append(Particula(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.centery + random.randint(-14, 14),
                    "pixel",
                ))

        # Decrementa o temporizador do efeito de glitch
        if self.glitch_timer > 0:
            self.glitch_timer -= 1

        # Remove partículas que já esgotaram a vida (vida <= 0)
        self.particulas = [p for p in self.particulas if p.vida > 0]

        # Atualiza posição e vida de todas as partículas ativas
        for p in self.particulas:
            p.atualizar()

        # ---- Verificação de colisão com perigos ----
        for perigo in perigos:
            if self.rect.colliderect(perigo):
                self.resetar()   # Mata o jogador e o manda para o spawn
                return False     # Retorna False indicando que o jogador morreu

        # ---- Verificação de queda para fora da tela ----
        # Se o jogador cair muito abaixo da tela visível, é considerado morto
        if self.rect.top > ALTURA + 400:
            self.resetar()
            return False

        # ---- Verificação de chegada à meta ----
        if self.rect.colliderect(meta):
            return "vitoria"  # Retorna a string "vitoria" para sinalizar que completou a fase

        return True  # Jogo continua normalmente

    def pular(self):
        # Só executa se ainda há pulos disponíveis (permite pulo duplo)
        if self.pulos_restantes > 0:
            self.vel_y = FORCA_PULO      # Aplica velocidade para cima
            self.pulos_restantes -= 1    # Consome um pulo

            # Gera 5 partículas de fórmula matemática ao redor do jogador ao pular
            for _ in range(5):
                self.particulas.append(Particula(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.centery + random.randint(-10, 10),
                    "formula",
                ))

    def _cor_ciclica(self, offset=0):
        # Gera uma cor RGB que oscila suavemente ao longo do tempo usando funções seno
        # Cada canal (R, G, B) oscila de 0 a 255 com fases diferentes, criando um arco-íris animado
        t = self.t * 0.05                                     # Fator de tempo (velocidade da oscilação)
        r = int(127 + 127 * math.sin(t + offset))             # Canal vermelho
        g = int(127 + 127 * math.sin(t + offset + 2.1))       # Canal verde (defasado em ~120°)
        b = int(127 + 127 * math.sin(t + offset + 4.2))       # Canal azul (defasado em ~240°)
        return (r, g, b)

    def desenhar(self, superficie, camera_x):
        # ---- Desenha partículas ANTES do personagem (ficam atrás) ----
        for p in self.particulas:
            p.desenhar(superficie, camera_x)

        # Posição do jogador na tela (descontando o scroll da câmera)
        x = self.rect.x - camera_x
        y = self.rect.y
        W = self.largura   # 32 — largura do personagem
        H = self.altura    # 48 — altura do personagem
        cx = x + W // 2   # Centro horizontal do personagem na tela

        # Duas cores animadas usadas nos detalhes do personagem
        cor_vivo   = self._cor_ciclica(0)    # Cor principal ciclando
        cor_accent = self._cor_ciclica(2.1)  # Cor secundária defasada em ~120°

        # ---- Cubos orbitando ao redor do personagem ----
        # 3 cubinhos giram em torno do personagem em ângulos separados por 120°
        for i in range(3):
            # Calcula o ângulo de cada cubo em função do tempo (rotação contínua)
            ang = self.t * 0.035 + i * (2 * math.pi / 3)

            # Posição do cubo usando coordenadas polares convertidas para cartesianas
            bx = cx + int(math.cos(ang) * 26)             # 26 pixels de raio horizontal
            by = y + H // 2 + int(math.sin(ang) * 16)     # 16 pixels de raio vertical (elipse)

            # Cor do cubo varia por índice (cicla pelas cores neon)
            cube_cor = CORES_GLITCH[i % len(CORES_GLITCH)]

            # Desenha o cubo preenchido e depois o contorno branco por cima
            pygame.draw.rect(superficie, cube_cor, (bx - 4, by - 4, 8, 8))
            pygame.draw.rect(superficie, BRANCO, (bx - 4, by - 4, 8, 8), 1)  # 1 = espessura do contorno

        # ---- Efeito de glitch: faixa de cor deslocada horizontalmente ----
        if self.glitch_timer > 0:
            band_y = y + random.randint(4, H - 12)         # Altura aleatória da faixa dentro do personagem
            band_h = random.randint(4, 10)                 # Altura da faixa em pixels
            glitch_cor = random.choice(CORES_GLITCH)       # Cor neon aleatória

            # Surface com canal alpha para semi-transparência
            glitch_surf = pygame.Surface((W + 4, band_h), pygame.SRCALPHA)
            glitch_surf.fill((*glitch_cor, 140))           # 140/255 de opacidade
            superficie.blit(glitch_surf, (x + self.glitch_dx - 2, band_y))

        # ==================== DESENHO DO PERSONAGEM ====================

        # ---- Pernas (dois blocos escuros na parte inferior) ----
        pygame.draw.rect(superficie, (25, 15, 50), (x + 3,      y + H - 11, 11, 11))   # Perna esquerda
        pygame.draw.rect(superficie, (25, 15, 50), (x + W - 14, y + H - 11, 11, 11))   # Perna direita

        # Detalhes coloridos nos pés (parte de baixo das pernas)
        pygame.draw.rect(superficie, cor_accent, (x + 5,      y + H - 6, 7, 3))  # Detalhe perna esquerda
        pygame.draw.rect(superficie, cor_accent, (x + W - 12, y + H - 6, 7, 3))  # Detalhe perna direita

        # ---- Corpo (moletom roxo escuro futurista) ----
        pygame.draw.rect(superficie, (55, 15, 95), (x + 1, y + 15, W - 2, H - 26))

        # ---- Diamante geométrico no peito ----
        ds = 8  # Metade do tamanho do diamante em pixels
        # Polígono de 4 vértices formando um losango/diamante preenchido com a cor animada
        pygame.draw.polygon(superficie, cor_vivo, [
            (cx,      y + 23 - ds),   # Vértice superior
            (cx + ds, y + 23),        # Vértice direito
            (cx,      y + 23 + ds),   # Vértice inferior
            (cx - ds, y + 23),        # Vértice esquerdo
        ])
        # Contorno branco fino por cima do diamante
        pygame.draw.polygon(superficie, BRANCO, [
            (cx,      y + 23 - ds),
            (cx + ds, y + 23),
            (cx,      y + 23 + ds),
            (cx - ds, y + 23),
        ], 1)

        # ---- Bordas ciano verticais do moletom (efeito tech) ----
        pygame.draw.line(superficie, CIANO, (x + 1,     y + 15), (x + 1,     y + H - 11), 2)  # Borda esquerda
        pygame.draw.line(superficie, CIANO, (x + W - 1, y + 15), (x + W - 1, y + H - 11), 2)  # Borda direita

        # ---- Triângulos decorativos nas laterais do moletom ----
        # Triângulo decorativo esquerdo
        pygame.draw.polygon(superficie, cor_accent, [
            (x + 6,     y + H - 22),
            (x + 1,     y + H - 14),
            (x + 11,    y + H - 14),
        ])
        # Triângulo decorativo direito (simétrico)
        pygame.draw.polygon(superficie, cor_accent, [
            (x + W - 6,  y + H - 22),
            (x + W - 11, y + H - 14),
            (x + W - 1,  y + H - 14),
        ])

        # ---- Hood (fundo da capuz — retângulo horizontal na parte superior do corpo) ----
        pygame.draw.rect(superficie, (45, 12, 75), (x, y + 5, W, 12))

        # ---- Cabeça (bloco escuro azulado) ----
        pygame.draw.rect(superficie, (28, 28, 58), (x + 5, y + 2, 22, 13))

        # ---- Pico da capuz (triângulo que aponta para cima acima da cabeça) ----
        pygame.draw.polygon(superficie, (45, 12, 75), [
            (cx,         y - 7),   # Ponta do capuz
            (x + 7,      y + 5),   # Base esquerda
            (x + W - 7,  y + 5),   # Base direita
        ])

        # Redesenha a cabeça por cima da capuz para corrigir a sobreposição visual
        pygame.draw.rect(superficie, (28, 28, 58), (x + 5, y + 2, 22, 13))

        # ---- Óculos digitais / visor (dois retângulos ciano com cor animada interna) ----
        pygame.draw.rect(superficie, CIANO,    (x + 7,  y + 6, 7, 4))   # Lente esquerda (contorno ciano)
        pygame.draw.rect(superficie, CIANO,    (x + 18, y + 6, 7, 4))   # Lente direita (contorno ciano)
        pygame.draw.rect(superficie, cor_vivo, (x + 8,  y + 7, 5, 2))   # Interior animado lente esquerda
        pygame.draw.rect(superficie, cor_vivo, (x + 19, y + 7, 5, 2))   # Interior animado lente direita

        # ---- Glitch corporal: fatia do personagem em cor neon deslocada ----
        # Só ocorre quando o glitch_timer está acima de 3 (fase mais intensa do efeito)
        if self.glitch_timer > 3:
            glitch_body_cor = random.choice(CORES_GLITCH)           # Cor aleatória neon
            slice_y = y + random.randint(0, H - 8)                  # Posição vertical aleatória da fatia
            slice_h = random.randint(3, 7)                           # Espessura da fatia
            pygame.draw.rect(superficie, glitch_body_cor,
                             (x + self.glitch_dx, slice_y, W, slice_h))  # Desenha a fatia deslocada

        # ---- Pescoço (pequeno retângulo entre cabeça e corpo) ----
        pygame.draw.rect(superficie, (40, 18, 68), (x + 11, y + 15, 10, 4))


# ==================== CLASSE PLATAFORMA ====================

class Plataforma:
    def __init__(self, x, y, largura, altura, cor=VERDE):
        # pygame.Rect define posição (x, y) e tamanho (largura, altura) — usado para colisão e desenho
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor  # Cor de preenchimento da plataforma (padrão: verde)

    def desenhar(self, superficie, camera_x):
        r = self.rect.copy()    # Cria uma cópia do rect para não modificar o original
        r.x -= camera_x         # Converte a posição do mundo para posição na tela

        # Otimização: não desenha plataformas fora da área visível da câmera
        if r.right < 0 or r.left > LARGURA:
            return

        # Desenha o corpo principal da plataforma
        pygame.draw.rect(superficie, self.cor, r)

        # Desenha uma faixa mais escura no topo da plataforma (detalhe visual)
        topo = pygame.Rect(r.x, r.y, r.width, 6)
        pygame.draw.rect(superficie, VERDE_ESCURO if self.cor == VERDE else CINZA, topo)

        # Contorno preto ao redor de toda a plataforma
        pygame.draw.rect(superficie, PRETO, r, 2)


# ==================== CLASSE PLATAFORMAMOVEL ====================

class PlataformaMovel(Plataforma):
    # Herda de Plataforma e adiciona movimento oscilatório (vai e volta)
    def __init__(self, x, y, largura, altura, dx, dy, alcance):
        # Chama o construtor da classe pai com cor amarela para distinguir visualmente
        super().__init__(x, y, largura, altura, cor=AMARELO)

        self.origem = (x, y)   # Posição central do movimento (ponto de equilíbrio)
        self.dx = dx           # Componente de direção horizontal (0 = não se move na horizontal)
        self.dy = dy           # Componente de direção vertical (0 = não se move na vertical)
        self.alcance = alcance # Amplitude máxima do movimento em pixels
        self.t = 0             # Contador de tempo para calcular a oscilação

    def atualizar(self):
        self.t += 1  # Avança o tempo

        # Usa seno para criar oscilação suave: vai de -alcance até +alcance e volta
        offset = math.sin(self.t * 0.02) * self.alcance

        # Atualiza posição com base na origem + deslocamento oscilatório
        self.rect.x = self.origem[0] + int(self.dx * offset)
        self.rect.y = self.origem[1] + int(self.dy * offset)


# ==================== FUNÇÃO: CRIAR FASE ====================

def criar_fase():
    # Cria e retorna todas as plataformas, perigos e a posição da meta da fase
    plataformas = []
    perigos = []

    # ---- Seção 1: Início da fase ----
    plataformas.append(Plataforma(0, 480, 400, 60))         # Plataforma inicial ampla (chão de saída)
    plataformas.append(Plataforma(500, 440, 120, 20))        # Plataforma flutuante após o vazio
    plataformas.append(Plataforma(700, 380, 120, 20))        # Sequência ascendente de plataformas
    plataformas.append(Plataforma(900, 320, 120, 20))

    perigos.append(pygame.Rect(1050, 470, 200, 70))          # Zona de espinhos — primeiro obstáculo

    # ---- Seção 2: Plataformas escalonadas e primeira plataforma móvel ----
    plataformas.append(Plataforma(1280, 400, 140, 20))
    plataformas.append(Plataforma(1500, 340, 100, 20))
    plataformas.append(PlataformaMovel(1700, 300, 100, 20, 0, 1, 80))  # Move verticalmente (dy=1, alcance=80)
    plataformas.append(Plataforma(1920, 360, 120, 20))

    perigos.append(pygame.Rect(2080, 470, 300, 70))          # Segunda zona de espinhos (mais larga)

    # ---- Seção 3: Sequência em ziguezague ----
    plataformas.append(Plataforma(2150, 280, 80, 20))
    plataformas.append(Plataforma(2300, 220, 80, 20))
    plataformas.append(Plataforma(2450, 280, 80, 20))
    plataformas.append(Plataforma(2600, 360, 120, 20))

    plataformas.append(Plataforma(2780, 440, 200, 100))      # Plataforma maior (área de descanso)
    perigos.append(pygame.Rect(2980, 510, 220, 30))          # Espinhos no chão logo após

    # ---- Seção 4: Segunda plataforma móvel (horizontal) ----
    plataformas.append(PlataformaMovel(3050, 380, 100, 20, 1, 0, 120))  # Move horizontalmente (dx=1, alcance=120)
    plataformas.append(Plataforma(3300, 360, 100, 20))
    plataformas.append(Plataforma(3480, 300, 100, 20))
    plataformas.append(Plataforma(3660, 240, 100, 20))

    # ---- Seção 5: Subida intensa + perigo ----
    plataformas.append(Plataforma(3850, 200, 80, 20))
    perigos.append(pygame.Rect(3950, 470, 200, 70))

    # ---- Seção 6: Plataformas pequenas em escada descendente ----
    plataformas.append(Plataforma(4000, 180, 60, 20))
    plataformas.append(Plataforma(4140, 220, 60, 20))
    plataformas.append(Plataforma(4280, 260, 60, 20))
    plataformas.append(Plataforma(4420, 300, 60, 20))

    # ---- Seção 7: Chegada à meta ----
    plataformas.append(Plataforma(4560, 350, 300, 20))                      # Plataforma de aproximação
    plataformas.append(Plataforma(4900, 350, 200, 190, cor=VERDE_ESCURO))   # Plataforma-base da meta (bloco sólido)

    # Retângulo invisível que define a área de chegada (colisão com ela = vitória)
    meta = pygame.Rect(4980, 270, 40, 80)

    return plataformas, perigos, meta


# ==================== FUNÇÃO: DESENHAR FUNDO ====================

def desenhar_fundo(superficie, camera_x):
    # ---- Gradiente de céu: linhas horizontais que ficam levemente mais escuras de cima para baixo ----
    for y in range(ALTURA):
        cor = (
            int(AZUL_CEU[0] - y * 0.1),   # Vermelho diminui ligeiramente conforme desce
            int(AZUL_CEU[1] - y * 0.05),  # Verde diminui ainda mais levemente
            int(AZUL_CEU[2]),              # Azul constante
        )
        pygame.draw.line(superficie, cor, (0, y), (LARGURA, y))  # Linha horizontal de ponta a ponta

    # ---- Nuvens (2 elipses sobrepostas, com parallax lento) ----
    for i in range(8):
        # Parallax: a câmera se move, mas as nuvens se movem só 20% disso (0.2) — parecem distantes
        nx = (i * 700 - camera_x * 0.2) % (LARGURA + 200) - 100

        # Duas elipses brancas levemente deslocadas formam cada nuvem
        pygame.draw.ellipse(superficie, (220, 230, 245), (nx,      60 + (i % 3) * 40, 140, 50))
        pygame.draw.ellipse(superficie, (220, 230, 245), (nx + 30, 50 + (i % 3) * 40, 120, 50))

    # ---- Montanhas ao fundo (triângulos com parallax médio) ----
    for i in range(6):
        # Parallax: as montanhas se movem 40% da câmera (mais próximas que as nuvens)
        mx = (i * 400 - camera_x * 0.4) % (LARGURA + 300) - 150

        # Triângulo representando uma montanha
        pygame.draw.polygon(superficie, AZUL_ESCURO, [
            (mx,       480),   # Base esquerda
            (mx + 150, 280),   # Pico da montanha
            (mx + 300, 480),   # Base direita
        ])


# ==================== FUNÇÃO: DESENHAR PERIGO ====================

def desenhar_perigo(superficie, rect, camera_x):
    r = rect.copy()    # Cópia do rect para não modificar o original
    r.x -= camera_x    # Converte para posição na tela

    # Não desenha se estiver fora da área visível
    if r.right < 0 or r.left > LARGURA:
        return

    # Base preta do perigo (área preenchida)
    pygame.draw.rect(superficie, PRETO, r)

    # Calcula quantos espinhos cabem na largura do perigo (1 a cada 20 pixels)
    n = max(1, r.width // 20)

    # Desenha n espinhos (triângulos vermelhos apontados para cima) distribuídos uniformemente
    for i in range(n):
        x0 = r.x + i * (r.width / n)            # Início do espinho
        x1 = r.x + (i + 0.5) * (r.width / n)   # Ponta do espinho (meio)
        x2 = r.x + (i + 1) * (r.width / n)      # Fim do espinho
        pygame.draw.polygon(superficie, VERMELHO, [
            (x0, r.y + 10),    # Base esquerda
            (x1, r.y - 12),    # Ponta superior
            (x2, r.y + 10),    # Base direita
        ])


# ==================== FUNÇÃO: DESENHAR META ====================

def desenhar_meta(superficie, rect, camera_x, t):
    r = rect.copy()
    r.x -= camera_x   # Converte para posição na tela

    # Mastro vertical preto (4px de largura, sobe 80px acima do rect da meta)
    pygame.draw.rect(superficie, PRETO, (r.x + r.width // 2 - 2, r.y - 80, 4, r.height + 80))

    # Animação da bandeira: ondula usando seno multiplicado pelo tempo
    onda = math.sin(t * 0.1) * 4  # Oscila entre -4 e +4 pixels horizontalmente

    # Vértices do triângulo da bandeira vermelha
    bandeira = [
        (r.x + r.width // 2 + 2,          r.y - 80),          # Topo fixo no mastro
        (r.x + r.width // 2 + 50 + onda,  r.y - 65),          # Ponta direita ondulante
        (r.x + r.width // 2 + 2,          r.y - 50),          # Base no mastro
    ]
    pygame.draw.polygon(superficie, VERMELHO, bandeira)


# ==================== TELA INICIAL ====================

def tela_inicial():
    # Cria o mundo como fundo animado da tela inicial (câmera se move automaticamente)
    plataformas_bg, perigos_bg, meta_bg = criar_fase()
    camera_x = 0.0    # Posição da câmera no mundo (float para movimento suave)
    t = 0             # Contador de frames para animações
    FADE_DUR = 52     # Duração do fade de saída em frames (~0.87 segundos a 60fps)
    fade_timer = 0    # 0 = aguardando input; quando > 0, conta até FADE_DUR e encerra a tela

    while True:
        # ---- Processamento de eventos ----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                # Usuário fechou a janela
                pygame.quit()
                sys.exit()

            # Qualquer tecla pressionada inicia o fade de saída (se ainda não começou)
            if evento.type == pygame.KEYDOWN and fade_timer == 0:
                fade_timer = 1

        t += 1  # Avança o tempo

        # Atualiza posição das plataformas móveis no fundo
        for p in plataformas_bg:
            if isinstance(p, PlataformaMovel):  # isinstance verifica se p é do tipo PlataformaMovel
                p.atualizar()

        # Câmera avança automaticamente para criar sensação de movimento
        camera_x += 1.4
        if camera_x > 4200:
            camera_x = 0.0   # Reinicia a câmera para criar um loop suave

        # ---- Desenha o mundo como fundo ----
        desenhar_fundo(tela, camera_x)
        for p in plataformas_bg:
            p.desenhar(tela, camera_x)
        for perigo in perigos_bg:
            desenhar_perigo(tela, perigo, camera_x)
        desenhar_meta(tela, meta_bg, camera_x, t)

        # Progresso do fade: 0.0 (início) → 1.0 (tela totalmente preta)
        fade_prog = (fade_timer / FADE_DUR) if fade_timer > 0 else 0.0

        # ---- Overlay escuro semi-transparente que fica mais opaco ao sair ----
        overlay_alpha = int(150 + 105 * fade_prog)   # De 150 (tela inicial) até 255 (preto total)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)  # Surface com canal alpha
        overlay.fill((5, 5, 20, overlay_alpha))       # Azul muito escuro com transparência variável
        tela.blit(overlay, (0, 0))                    # Desenha o overlay sobre tudo

        # Alpha dos elementos de UI (título, subtítulo, etc.) — somem durante o fade
        elem_alpha = int(255 * (1.0 - fade_prog))

        # ---- Efeito de glow do título: 4 cópias laranja levemente deslocadas ----
        for dx2, dy2 in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            glow = fonte_grande.render("πXEL RUN", True, LARANJA)
            glow.set_alpha(int(90 * (1.0 - fade_prog)))  # Glow some junto com o fade
            tela.blit(glow, (LARGURA // 2 - glow.get_width() // 2 + dx2, 155 + dy2))

        # ---- Título principal em amarelo ----
        titulo_surf = fonte_grande.render("πXEL RUN", True, AMARELO)
        titulo_surf.set_alpha(elem_alpha)
        tela.blit(titulo_surf, (LARGURA // 2 - titulo_surf.get_width() // 2, 155))

        # ---- Subtítulo em ciano ----
        sub = fonte.render("um jogo de plataforma matemático", True, CIANO)
        sub.set_alpha(int(elem_alpha * 0.75))   # Ligeiramente mais transparente que o título
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 228))

        # ---- Texto "Pressione qualquer tecla" com pulsação ----
        # pulse oscila entre 190 e 255, criando um efeito de piscar suave
        pulse = int(190 + 65 * math.sin(t * 0.08))
        prompt = fonte.render("Pressione qualquer tecla para começar", True, (pulse, pulse, pulse))
        prompt.set_alpha(elem_alpha)
        tela.blit(prompt, (LARGURA // 2 - prompt.get_width() // 2, 330))

        # ---- Dicas de controles em cinza (discretas) ----
        hint = fonte.render("WASD / Setas — mover   |   ESPAÇO — pulo duplo", True, CINZA)
        hint.set_alpha(int(elem_alpha * 0.65))   # Mais transparente que os outros textos
        tela.blit(hint, (LARGURA // 2 - hint.get_width() // 2, 420))

        pygame.display.flip()   # Envia o frame desenhado para a tela (atualiza o display)
        clock.tick(FPS)         # Limita a velocidade do loop a 60 frames por segundo

        # ---- Controla o fade de saída ----
        if fade_timer > 0:
            fade_timer += 1           # Avança o timer do fade
            if fade_timer > FADE_DUR:
                return                # Saí da função quando o fade terminar → vai para jogar()


# ==================== TELA DE VITÓRIA ====================

def tela_vitoria(tempo, mortes):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True   # Retorna True → o jogo reinicia (jogar() é chamado novamente)
                if evento.key == pygame.K_ESCAPE:
                    return False  # Retorna False → encerra o jogo

        tela.fill(VERDE_ESCURO)   # Limpa a tela com verde escuro como fundo da tela de vitória

        # Título de vitória centralizado
        titulo = fonte_grande.render("VOCE VENCEU!", True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 160))

        # Exibe o tempo final formatado com 1 casa decimal e a contagem de mortes
        t_txt = fonte.render(f"Tempo: {tempo:.1f}s   Mortes: {mortes}", True, BRANCO)
        tela.blit(t_txt, (LARGURA // 2 - t_txt.get_width() // 2, 280))

        # Instruções para reiniciar ou sair
        r_txt = fonte.render("R para jogar de novo   ESC para sair", True, BRANCO)
        tela.blit(r_txt, (LARGURA // 2 - r_txt.get_width() // 2, 340))

        pygame.display.flip()
        clock.tick(FPS)


# ==================== LOOP PRINCIPAL DO JOGO ====================

def jogar():
    jogador = Jogador(60, 400)                         # Cria o jogador na posição inicial
    plataformas, perigos, meta = criar_fase()           # Carrega todas as plataformas, perigos e a meta
    camera_x = 0                                        # Câmera começa no início do mundo
    t = 0                                               # Contador de frames
    inicio = pygame.time.get_ticks()                    # Registra o tempo em ms no início da sessão
    FADE_IN_DUR = 48                                    # Duração do fade de entrada em frames
    fade_in = FADE_IN_DUR                               # Conta regressiva: começa em 48, vai até 0

    while True:
        # ---- Processamento de eventos ----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                # Espaço, seta para cima ou W ativam o pulo
                if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    jogador.pular()

                # R reinicia o jogo inteiro (chama jogar() recursivamente)
                if evento.key == pygame.K_r:
                    return jogar()

                # ESC sai do jogo (retorna para o fluxo principal)
                if evento.key == pygame.K_ESCAPE:
                    return

        # Captura todas as teclas pressionadas no momento (para movimento contínuo)
        teclas = pygame.key.get_pressed()

        # Atualiza posição das plataformas móveis
        for p in plataformas:
            if isinstance(p, PlataformaMovel):
                p.atualizar()

        # Atualiza o jogador e recebe o resultado do frame
        resultado = jogador.atualizar(teclas, plataformas, perigos, meta)

        if resultado == "vitoria":
            # Calcula o tempo total em segundos
            fim = (pygame.time.get_ticks() - inicio) / 1000.0

            # Exibe a tela de vitória; se o jogador quiser jogar de novo, reinicia
            if tela_vitoria(fim, jogador.mortes):
                return jogar()
            return   # Senão, encerra

        # ---- Câmera suave (segue o jogador com interpolação) ----
        # Alvo: deixa o jogador no 1/3 esquerdo da tela
        alvo_cam = jogador.rect.x - LARGURA // 3

        # Interpola a câmera em direção ao alvo (10% da distância por frame → movimento suave)
        camera_x += (alvo_cam - camera_x) * 0.1

        # Impede a câmera de ir antes do início do mundo
        if camera_x < 0:
            camera_x = 0

        # ---- Desenho do frame ----
        desenhar_fundo(tela, camera_x)

        # Desenha todas as plataformas
        for p in plataformas:
            p.desenhar(tela, camera_x)

        # Desenha todos os perigos
        for perigo in perigos:
            desenhar_perigo(tela, perigo, camera_x)

        # Desenha a meta (bandeira)
        desenhar_meta(tela, meta, camera_x, t)

        # Desenha o jogador e seus efeitos de partícula
        jogador.desenhar(tela, camera_x)

        # ---- HUD (Heads-Up Display — informações na tela) ----
        tempo_atual = (pygame.time.get_ticks() - inicio) / 1000.0  # Tempo decorrido em segundos
        hud1 = fonte.render(f"Tempo: {tempo_atual:.1f}s",         True, BRANCO)
        hud2 = fonte.render(f"Mortes: {jogador.mortes}",          True, BRANCO)
        hud3 = fonte.render(f"Pulos: {jogador.pulos_restantes}",  True, BRANCO)
        tela.blit(hud1, (16, 12))   # Tempo no canto superior esquerdo
        tela.blit(hud2, (16, 40))   # Mortes abaixo do tempo
        tela.blit(hud3, (16, 68))   # Pulos disponíveis abaixo das mortes

        # ---- Fade de entrada: tela preta que vai ficando transparente no início ----
        if fade_in > 0:
            fade_surf = pygame.Surface((LARGURA, ALTURA))
            fade_surf.fill((5, 5, 20))                                   # Cor preta azulada
            fade_surf.set_alpha(int(255 * fade_in / FADE_IN_DUR))        # Alpha decrescente a cada frame
            tela.blit(fade_surf, (0, 0))
            fade_in -= 1   # Decrementa o timer do fade

        t += 1
        pygame.display.flip()   # Envia o frame para a tela
        clock.tick(FPS)         # Mantém o jogo a 60 FPS


# ==================== PONTO DE ENTRADA DO PROGRAMA ====================

if __name__ == "__main__":
    # Este bloco só é executado quando o arquivo é rodado diretamente (não importado como módulo)
    tela_inicial()   # Exibe a tela inicial com fade; retorna quando o jogador pressiona uma tecla
    jogar()          # Inicia o loop principal do jogo
    pygame.quit()    # Encerra o pygame ao sair do loop do jogo
