import math
import sys
import random

import pygame

pygame.init()

LARGURA, ALTURA = 960, 540
FPS = 60
GRAVIDADE = 0.8
FORCA_PULO = -15
VELOCIDADE = 6

BRANCO = (240, 240, 240)
PRETO = (20, 20, 30)
AZUL_CEU = (110, 180, 230)
AZUL_ESCURO = (40, 60, 100)
VERDE = (90, 200, 110)
VERDE_ESCURO = (50, 140, 70)
VERMELHO = (230, 80, 80)
AMARELO = (250, 210, 80)
LARANJA = (240, 140, 60)
CINZA = (120, 120, 130)
ROXO_NEON = (140, 0, 255)
CIANO = (0, 210, 255)
VERDE_NEON = (0, 255, 120)
ROSA_NEON = (255, 50, 180)

CORES_GLITCH = [CIANO, ROXO_NEON, VERDE_NEON, ROSA_NEON, AMARELO]
FORMULAS = ["π", "Σ", "√2", "∫", "∂", "∞", "x²", "λ", "Δ", "θ", "f(x)", "n!"]

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("πXEL RUN")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24, bold=True)
fonte_grande = pygame.font.SysFont("arial", 56, bold=True)
fonte_formula = pygame.font.SysFont("arial", 13, bold=True)


class Particula:
    def __init__(self, x, y, tipo):
        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo

        if tipo == "triangulo":
            self.vel_x = random.uniform(-1.2, 1.2)
            self.vel_y = random.uniform(-1.8, -0.4)
            self.vida = random.randint(16, 26)
            self.vida_max = self.vida
            self.tamanho = random.randint(4, 9)
            self.cor = random.choice(CORES_GLITCH)

        elif tipo == "formula":
            self.vel_x = random.uniform(-0.7, 0.7)
            self.vel_y = random.uniform(-2.8, -1.2)
            self.vida = random.randint(40, 65)
            self.vida_max = self.vida
            self.texto = random.choice(FORMULAS)
            self.cor = random.choice([CIANO, VERDE_NEON, AMARELO, BRANCO])

        elif tipo == "pixel":
            self.vel_x = random.uniform(-5, 5)
            self.vel_y = random.uniform(-5, 1)
            self.vida = random.randint(8, 22)
            self.vida_max = self.vida
            self.tamanho = random.randint(2, 5)
            self.cor = random.choice(CORES_GLITCH)

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vida -= 1
        if self.tipo == "pixel":
            self.vel_y += 0.4

    def desenhar(self, superficie, camera_x):
        alpha = self.vida / self.vida_max
        sx = int(self.x - camera_x)
        sy = int(self.y)
        cor = tuple(int(c * alpha) for c in self.cor)

        if self.tipo == "triangulo":
            s = self.tamanho
            pygame.draw.polygon(superficie, cor, [(sx, sy - s), (sx - s, sy + s), (sx + s, sy + s)])

        elif self.tipo == "formula":
            txt = fonte_formula.render(self.texto, True, cor)
            superficie.blit(txt, (sx, sy))

        elif self.tipo == "pixel":
            pygame.draw.rect(superficie, cor, (sx, sy, self.tamanho, self.tamanho))


class Jogador:
    def __init__(self, x, y):
        self.largura = 32
        self.altura = 48
        self.rect = pygame.Rect(x, y, self.largura, self.altura)
        self.vel_x = 0
        self.vel_y = 0
        self.no_chao = False
        self.pulos_restantes = 2
        self.spawn = (x, y)
        self.mortes = 0
        self.olhando_direita = True

        self.particulas = []
        self.t = 0
        self.glitch_timer = 0
        self.glitch_dx = 0

    def resetar(self):
        for _ in range(18):
            self.particulas.append(Particula(self.rect.centerx, self.rect.centery, "pixel"))
        self.rect.x, self.rect.y = self.spawn
        self.vel_x = 0
        self.vel_y = 0
        self.pulos_restantes = 2
        self.mortes += 1

    def atualizar(self, teclas, plataformas, perigos, meta):
        self.t += 1
        self.vel_x = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VELOCIDADE
            self.olhando_direita = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VELOCIDADE
            self.olhando_direita = True

        self.vel_y += GRAVIDADE
        if self.vel_y > 18:
            self.vel_y = 18

        self.rect.x += self.vel_x
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

        self.rect.y += self.vel_y
        self.no_chao = False
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.no_chao = True
                    self.pulos_restantes = 2
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

        # Trail de triângulos ao se mover
        if self.vel_x != 0 and self.t % 3 == 0:
            px = self.rect.centerx - (12 if self.olhando_direita else -12)
            py = self.rect.bottom - 10
            self.particulas.append(Particula(px, py, "triangulo"))

        # Glitch periódico + burst de pixels
        if self.t % 90 == 0 or (random.random() < 0.006):
            self.glitch_timer = random.randint(5, 12)
            self.glitch_dx = random.randint(-10, 10)
            for _ in range(12):
                self.particulas.append(Particula(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.centery + random.randint(-14, 14),
                    "pixel",
                ))

        if self.glitch_timer > 0:
            self.glitch_timer -= 1

        self.particulas = [p for p in self.particulas if p.vida > 0]
        for p in self.particulas:
            p.atualizar()

        for perigo in perigos:
            if self.rect.colliderect(perigo):
                self.resetar()
                return False

        if self.rect.top > ALTURA + 400:
            self.resetar()
            return False

        if self.rect.colliderect(meta):
            return "vitoria"

        return True

    def pular(self):
        if self.pulos_restantes > 0:
            self.vel_y = FORCA_PULO
            self.pulos_restantes -= 1
            # Fórmulas matemáticas aparecem ao pular
            for _ in range(5):
                self.particulas.append(Particula(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.centery + random.randint(-10, 10),
                    "formula",
                ))

    def _cor_ciclica(self, offset=0):
        t = self.t * 0.05
        r = int(127 + 127 * math.sin(t + offset))
        g = int(127 + 127 * math.sin(t + offset + 2.1))
        b = int(127 + 127 * math.sin(t + offset + 4.2))
        return (r, g, b)

    def desenhar(self, superficie, camera_x):
        # Partículas (atrás do personagem)
        for p in self.particulas:
            p.desenhar(superficie, camera_x)

        x = self.rect.x - camera_x
        y = self.rect.y
        W = self.largura   # 32
        H = self.altura    # 48
        cx = x + W // 2

        cor_vivo = self._cor_ciclica(0)
        cor_accent = self._cor_ciclica(2.1)

        # Cubos flutuando ao redor (Mestre da Geometria)
        for i in range(3):
            ang = self.t * 0.035 + i * (2 * math.pi / 3)
            bx = cx + int(math.cos(ang) * 26)
            by = y + H // 2 + int(math.sin(ang) * 16)
            cube_cor = CORES_GLITCH[i % len(CORES_GLITCH)]
            pygame.draw.rect(superficie, cube_cor, (bx - 4, by - 4, 8, 8))
            pygame.draw.rect(superficie, BRANCO, (bx - 4, by - 4, 8, 8), 1)

        # Glitch overlay (Glitch Player — faixa deslocada)
        if self.glitch_timer > 0:
            band_y = y + random.randint(4, H - 12)
            band_h = random.randint(4, 10)
            glitch_cor = random.choice(CORES_GLITCH)
            glitch_surf = pygame.Surface((W + 4, band_h), pygame.SRCALPHA)
            glitch_surf.fill((*glitch_cor, 140))
            superficie.blit(glitch_surf, (x + self.glitch_dx - 2, band_y))

        # ---- Desenhar personagem ----

        # Pernas (Mestre da Geometria — forma geométrica)
        pygame.draw.rect(superficie, (25, 15, 50), (x + 3, y + H - 11, 11, 11))
        pygame.draw.rect(superficie, (25, 15, 50), (x + W - 14, y + H - 11, 11, 11))
        pygame.draw.rect(superficie, cor_accent, (x + 5, y + H - 6, 7, 3))
        pygame.draw.rect(superficie, cor_accent, (x + W - 12, y + H - 6, 7, 3))

        # Corpo / moletom futurista (Hacker Matemático)
        pygame.draw.rect(superficie, (55, 15, 95), (x + 1, y + 15, W - 2, H - 26))

        # Diamante geométrico no peito (Mestre da Geometria)
        ds = 8
        pygame.draw.polygon(superficie, cor_vivo, [
            (cx, y + 23 - ds),
            (cx + ds, y + 23),
            (cx, y + 23 + ds),
            (cx - ds, y + 23),
        ])
        pygame.draw.polygon(superficie, BRANCO, [
            (cx, y + 23 - ds),
            (cx + ds, y + 23),
            (cx, y + 23 + ds),
            (cx - ds, y + 23),
        ], 1)

        # Bordas ciano do moletom (estilo tech)
        pygame.draw.line(superficie, CIANO, (x + 1, y + 15), (x + 1, y + H - 11), 2)
        pygame.draw.line(superficie, CIANO, (x + W - 1, y + 15), (x + W - 1, y + H - 11), 2)

        # Triângulos decorativos laterais do moletom
        pygame.draw.polygon(superficie, cor_accent, [
            (x + 6, y + H - 22), (x + 1, y + H - 14), (x + 11, y + H - 14)
        ])
        pygame.draw.polygon(superficie, cor_accent, [
            (x + W - 6, y + H - 22), (x + W - 11, y + H - 14), (x + W - 1, y + H - 14)
        ])

        # Hood lateral (fundo da capuz)
        pygame.draw.rect(superficie, (45, 12, 75), (x, y + 5, W, 12))

        # Cabeça (Hacker Matemático)
        pygame.draw.rect(superficie, (28, 28, 58), (x + 5, y + 2, 22, 13))

        # Pico da capuz (triângulo — Mestre da Geometria)
        pygame.draw.polygon(superficie, (45, 12, 75), [
            (cx, y - 7), (x + 7, y + 5), (x + W - 7, y + 5)
        ])

        # Redesenha cabeça por cima da capuz
        pygame.draw.rect(superficie, (28, 28, 58), (x + 5, y + 2, 22, 13))

        # Óculos digitais / visor (Hacker Matemático)
        pygame.draw.rect(superficie, CIANO, (x + 7, y + 6, 7, 4))
        pygame.draw.rect(superficie, CIANO, (x + 18, y + 6, 7, 4))
        # Cor interna ciclica dos óculos (efeito de tela digital)
        pygame.draw.rect(superficie, cor_vivo, (x + 8, y + 7, 5, 2))
        pygame.draw.rect(superficie, cor_vivo, (x + 19, y + 7, 5, 2))

        # Glitch corporal — partes do personagem em cores alternadas (Glitch Player)
        if self.glitch_timer > 3:
            glitch_body_cor = random.choice(CORES_GLITCH)
            slice_y = y + random.randint(0, H - 8)
            slice_h = random.randint(3, 7)
            pygame.draw.rect(superficie, glitch_body_cor,
                             (x + self.glitch_dx, slice_y, W, slice_h))

        # Pescoço
        pygame.draw.rect(superficie, (40, 18, 68), (x + 11, y + 15, 10, 4))


class Plataforma:
    def __init__(self, x, y, largura, altura, cor=VERDE):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor

    def desenhar(self, superficie, camera_x):
        r = self.rect.copy()
        r.x -= camera_x
        if r.right < 0 or r.left > LARGURA:
            return
        pygame.draw.rect(superficie, self.cor, r)
        topo = pygame.Rect(r.x, r.y, r.width, 6)
        pygame.draw.rect(superficie, VERDE_ESCURO if self.cor == VERDE else CINZA, topo)
        pygame.draw.rect(superficie, PRETO, r, 2)


class PlataformaMovel(Plataforma):
    def __init__(self, x, y, largura, altura, dx, dy, alcance):
        super().__init__(x, y, largura, altura, cor=AMARELO)
        self.origem = (x, y)
        self.dx = dx
        self.dy = dy
        self.alcance = alcance
        self.t = 0

    def atualizar(self):
        self.t += 1
        offset = math.sin(self.t * 0.02) * self.alcance
        self.rect.x = self.origem[0] + int(self.dx * offset)
        self.rect.y = self.origem[1] + int(self.dy * offset)


def criar_fase():
    plataformas = []
    perigos = []

    plataformas.append(Plataforma(0, 480, 400, 60))
    plataformas.append(Plataforma(500, 440, 120, 20))
    plataformas.append(Plataforma(700, 380, 120, 20))
    plataformas.append(Plataforma(900, 320, 120, 20))

    perigos.append(pygame.Rect(1050, 470, 200, 70))

    plataformas.append(Plataforma(1280, 400, 140, 20))
    plataformas.append(Plataforma(1500, 340, 100, 20))
    plataformas.append(PlataformaMovel(1700, 300, 100, 20, 0, 1, 80))
    plataformas.append(Plataforma(1920, 360, 120, 20))

    perigos.append(pygame.Rect(2080, 470, 300, 70))

    plataformas.append(Plataforma(2150, 280, 80, 20))
    plataformas.append(Plataforma(2300, 220, 80, 20))
    plataformas.append(Plataforma(2450, 280, 80, 20))
    plataformas.append(Plataforma(2600, 360, 120, 20))

    plataformas.append(Plataforma(2780, 440, 200, 100))
    perigos.append(pygame.Rect(2980, 510, 220, 30))

    plataformas.append(PlataformaMovel(3050, 380, 100, 20, 1, 0, 120))
    plataformas.append(Plataforma(3300, 360, 100, 20))
    plataformas.append(Plataforma(3480, 300, 100, 20))
    plataformas.append(Plataforma(3660, 240, 100, 20))

    plataformas.append(Plataforma(3850, 200, 80, 20))
    perigos.append(pygame.Rect(3950, 470, 200, 70))

    plataformas.append(Plataforma(4000, 180, 60, 20))
    plataformas.append(Plataforma(4140, 220, 60, 20))
    plataformas.append(Plataforma(4280, 260, 60, 20))
    plataformas.append(Plataforma(4420, 300, 60, 20))

    plataformas.append(Plataforma(4560, 350, 300, 20))
    plataformas.append(Plataforma(4900, 350, 200, 190, cor=VERDE_ESCURO))

    meta = pygame.Rect(4980, 270, 40, 80)

    return plataformas, perigos, meta


def desenhar_fundo(superficie, camera_x):
    for y in range(ALTURA):
        cor = (
            int(AZUL_CEU[0] - y * 0.1),
            int(AZUL_CEU[1] - y * 0.05),
            int(AZUL_CEU[2]),
        )
        pygame.draw.line(superficie, cor, (0, y), (LARGURA, y))

    for i in range(8):
        nx = (i * 700 - camera_x * 0.2) % (LARGURA + 200) - 100
        pygame.draw.ellipse(superficie, (220, 230, 245), (nx, 60 + (i % 3) * 40, 140, 50))
        pygame.draw.ellipse(superficie, (220, 230, 245), (nx + 30, 50 + (i % 3) * 40, 120, 50))

    for i in range(6):
        mx = (i * 400 - camera_x * 0.4) % (LARGURA + 300) - 150
        pygame.draw.polygon(superficie, AZUL_ESCURO, [
            (mx, 480),
            (mx + 150, 280),
            (mx + 300, 480),
        ])


def desenhar_perigo(superficie, rect, camera_x):
    r = rect.copy()
    r.x -= camera_x
    if r.right < 0 or r.left > LARGURA:
        return
    pygame.draw.rect(superficie, PRETO, r)
    n = max(1, r.width // 20)
    for i in range(n):
        x0 = r.x + i * (r.width / n)
        x1 = r.x + (i + 0.5) * (r.width / n)
        x2 = r.x + (i + 1) * (r.width / n)
        pygame.draw.polygon(superficie, VERMELHO, [
            (x0, r.y + 10),
            (x1, r.y - 12),
            (x2, r.y + 10),
        ])


def desenhar_meta(superficie, rect, camera_x, t):
    r = rect.copy()
    r.x -= camera_x
    pygame.draw.rect(superficie, PRETO, (r.x + r.width // 2 - 2, r.y - 80, 4, r.height + 80))
    onda = math.sin(t * 0.1) * 4
    bandeira = [
        (r.x + r.width // 2 + 2, r.y - 80),
        (r.x + r.width // 2 + 50 + onda, r.y - 65),
        (r.x + r.width // 2 + 2, r.y - 50),
    ]
    pygame.draw.polygon(superficie, VERMELHO, bandeira)


def tela_inicial():
    plataformas_bg, perigos_bg, meta_bg = criar_fase()
    camera_x = 0.0
    t = 0
    FADE_DUR = 52
    fade_timer = 0  # 0 = parado, >0 = fadeando para preto

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and fade_timer == 0:
                fade_timer = 1

        t += 1
        for p in plataformas_bg:
            if isinstance(p, PlataformaMovel):
                p.atualizar()

        # Câmera auto-scroll com loop suave
        camera_x += 1.4
        if camera_x > 4200:
            camera_x = 0.0

        # Mundo do jogo como fundo
        desenhar_fundo(tela, camera_x)
        for p in plataformas_bg:
            p.desenhar(tela, camera_x)
        for perigo in perigos_bg:
            desenhar_perigo(tela, perigo, camera_x)
        desenhar_meta(tela, meta_bg, camera_x, t)

        # Progresso do fade (0.0 = aguardando, 1.0 = preto total)
        fade_prog = (fade_timer / FADE_DUR) if fade_timer > 0 else 0.0

        # Overlay escuro sobre o jogo (fica mais escuro ao sair)
        overlay_alpha = int(150 + 105 * fade_prog)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((5, 5, 20, overlay_alpha))
        tela.blit(overlay, (0, 0))

        # Alpha dos elementos do título (somem durante o fade)
        elem_alpha = int(255 * (1.0 - fade_prog))

        # Glow do título (cópias deslocadas em laranja)
        for dx2, dy2 in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            glow = fonte_grande.render("πXEL RUN", True, LARANJA)
            glow.set_alpha(int(90 * (1.0 - fade_prog)))
            tela.blit(glow, (LARGURA // 2 - glow.get_width() // 2 + dx2, 155 + dy2))

        # Título principal
        titulo_surf = fonte_grande.render("πXEL RUN", True, AMARELO)
        titulo_surf.set_alpha(elem_alpha)
        tela.blit(titulo_surf, (LARGURA // 2 - titulo_surf.get_width() // 2, 155))

        # Subtítulo
        sub = fonte.render("um jogo de plataforma matemático", True, CIANO)
        sub.set_alpha(int(elem_alpha * 0.75))
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 228))

        # "Pressione qualquer tecla" com pulso
        pulse = int(190 + 65 * math.sin(t * 0.08))
        prompt = fonte.render("Pressione qualquer tecla para começar", True, (pulse, pulse, pulse))
        prompt.set_alpha(elem_alpha)
        tela.blit(prompt, (LARGURA // 2 - prompt.get_width() // 2, 330))

        # Controles (discretos)
        hint = fonte.render("WASD / Setas — mover   |   ESPAÇO — pulo duplo", True, CINZA)
        hint.set_alpha(int(elem_alpha * 0.65))
        tela.blit(hint, (LARGURA // 2 - hint.get_width() // 2, 420))

        pygame.display.flip()
        clock.tick(FPS)

        if fade_timer > 0:
            fade_timer += 1
            if fade_timer > FADE_DUR:
                return


def tela_vitoria(tempo, mortes):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    return False

        tela.fill(VERDE_ESCURO)
        titulo = fonte_grande.render("VOCE VENCEU!", True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 160))

        t_txt = fonte.render(f"Tempo: {tempo:.1f}s   Mortes: {mortes}", True, BRANCO)
        tela.blit(t_txt, (LARGURA // 2 - t_txt.get_width() // 2, 280))

        r_txt = fonte.render("R para jogar de novo   ESC para sair", True, BRANCO)
        tela.blit(r_txt, (LARGURA // 2 - r_txt.get_width() // 2, 340))

        pygame.display.flip()
        clock.tick(FPS)


def jogar():
    jogador = Jogador(60, 400)
    plataformas, perigos, meta = criar_fase()
    camera_x = 0
    t = 0
    inicio = pygame.time.get_ticks()
    FADE_IN_DUR = 48
    fade_in = FADE_IN_DUR  # conta regressiva: preto → transparente

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    jogador.pular()
                if evento.key == pygame.K_r:
                    return jogar()
                if evento.key == pygame.K_ESCAPE:
                    return

        teclas = pygame.key.get_pressed()

        for p in plataformas:
            if isinstance(p, PlataformaMovel):
                p.atualizar()

        resultado = jogador.atualizar(teclas, plataformas, perigos, meta)
        if resultado == "vitoria":
            fim = (pygame.time.get_ticks() - inicio) / 1000.0
            if tela_vitoria(fim, jogador.mortes):
                return jogar()
            return

        alvo_cam = jogador.rect.x - LARGURA // 3
        camera_x += (alvo_cam - camera_x) * 0.1
        if camera_x < 0:
            camera_x = 0

        desenhar_fundo(tela, camera_x)
        for p in plataformas:
            p.desenhar(tela, camera_x)
        for perigo in perigos:
            desenhar_perigo(tela, perigo, camera_x)
        desenhar_meta(tela, meta, camera_x, t)
        jogador.desenhar(tela, camera_x)

        tempo_atual = (pygame.time.get_ticks() - inicio) / 1000.0
        hud1 = fonte.render(f"Tempo: {tempo_atual:.1f}s", True, BRANCO)
        hud2 = fonte.render(f"Mortes: {jogador.mortes}", True, BRANCO)
        hud3 = fonte.render(f"Pulos: {jogador.pulos_restantes}", True, BRANCO)
        tela.blit(hud1, (16, 12))
        tela.blit(hud2, (16, 40))
        tela.blit(hud3, (16, 68))

        # Fade de entrada: preto → jogo
        if fade_in > 0:
            fade_surf = pygame.Surface((LARGURA, ALTURA))
            fade_surf.fill((5, 5, 20))
            fade_surf.set_alpha(int(255 * fade_in / FADE_IN_DUR))
            tela.blit(fade_surf, (0, 0))
            fade_in -= 1

        t += 1
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    tela_inicial()
    jogar()
    pygame.quit()
