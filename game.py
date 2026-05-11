import math
import sys

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

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Parkour Master")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24, bold=True)
fonte_grande = pygame.font.SysFont("arial", 56, bold=True)


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

    def resetar(self):
        self.rect.x, self.rect.y = self.spawn
        self.vel_x = 0
        self.vel_y = 0
        self.pulos_restantes = 2
        self.mortes += 1

    def atualizar(self, teclas, plataformas, perigos, meta):
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

    def desenhar(self, superficie, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        corpo = pygame.Rect(x, y, self.largura, self.altura)
        pygame.draw.rect(superficie, LARANJA, corpo, border_radius=6)
        pygame.draw.rect(superficie, PRETO, corpo, 2, border_radius=6)
        olho_x = x + (22 if self.olhando_direita else 6)
        pygame.draw.circle(superficie, BRANCO, (olho_x, y + 16), 4)
        pygame.draw.circle(superficie, PRETO, (olho_x + (1 if self.olhando_direita else -1), y + 16), 2)


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
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                return

        tela.fill(AZUL_ESCURO)
        titulo = fonte_grande.render("PARKOUR MASTER", True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 140))

        linhas = [
            "Use SETAS ou A/D para mover",
            "ESPACO ou W para pular (pulo duplo disponivel)",
            "Evite os espinhos e alcance a bandeira vermelha",
            "",
            "Pressione qualquer tecla para comecar",
        ]
        for i, linha in enumerate(linhas):
            txt = fonte.render(linha, True, BRANCO)
            tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 260 + i * 32))

        pygame.display.flip()
        clock.tick(FPS)


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
    fim = None

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

        t += 1
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    tela_inicial()
    jogar()
    pygame.quit()
