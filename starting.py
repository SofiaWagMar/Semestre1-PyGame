import pygame

pygame.display.init()

compri = 420
altura = 700
vel = 60

tela = pygame.display.set_mode((compri, altura))
pygame.display.set_caption("Parkour da enchente")

relogio = pygame.time.Clock()
rodando = True

raio = 14
anda = 4
gra = 0.5
pulo = -12

x = compri / 2
y = 620 - raio

velocidade_y = 0
apoiado = True

while rodando:
    pular = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False

            elif evento.key in (pygame.K_SPACE, pygame.K_UP):
                pular = True

    if not rodando:
        break

    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        x -= anda

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        x += anda

    x = max(raio, min(compri - raio, x))

    if pular and apoiado:
        velocidade_y = pulo
        apoiado = False

    velocidade_y += gra
    y += velocidade_y

    # mudar dps!
    if y + raio >= 620:
        y = 620 - raio
        velocidade_y = 0
        apoiado = True

    tela.fill((190, 225, 250))

    pygame.draw.rect(
        tela,
        (235, 130, 35),
        (0, 620, compri, 16),
    )

    pygame.draw.circle(
        tela,
        (110, 55, 170),
        (int(x), int(y)),
        raio,
    )

    pygame.display.update()
    relogio.tick(vel)

pygame.quit()

import pygame

pygame.display.init()

WIDTH = 420
HEIGHT = 700
FPS = 60

tela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parkour da enchente")

relogio = pygame.time.Clock()
rodando = True

RAIO = 14
VELOCIDADE = 4
GRAVIDADE = 0.5
FORCA_PULO = -12

x = WIDTH / 2
y = 620 - RAIO

velocidade_y = 0
apoiado = True

plataformas = [
    {"x": 125, "y": 620, "largura": 170},
    {"x": 40, "y": 535, "largura": 110},
    {"x": 200, "y": 450, "largura": 110},
    {"x": 70, "y": 365, "largura": 110},
    {"x": 210, "y": 280, "largura": 110},
]

while rodando:
    pular = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False

            elif evento.key in (pygame.K_SPACE, pygame.K_UP):
                pular = True

    if not rodando:
        break

    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        x -= VELOCIDADE

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        x += VELOCIDADE

    x = max(RAIO, min(WIDTH - RAIO, x))

    if pular and apoiado:
        velocidade_y = FORCA_PULO
        apoiado = False

    pe_anterior = y + RAIO

    velocidade_y += GRAVIDADE
    y += velocidade_y
    apoiado = False

    # Só pousa nas plataformas enquanto está descendo.
    if velocidade_y >= 0:
        for numero in range(len(plataformas) - 1, -1, -1):
            plataforma = plataformas[numero]

            sobre_plataforma = (
                x + RAIO > plataforma["x"]
                and x - RAIO < plataforma["x"] + plataforma["largura"]
            )

            cruzou_topo = (
                pe_anterior <= plataforma["y"] <= y + RAIO
            )

            if sobre_plataforma and cruzou_topo:
                y = plataforma["y"] - RAIO
                velocidade_y = 0
                apoiado = True
                break

    # Ainda não existem vidas: cair para fora reinicia a posição.
    if y - RAIO > HEIGHT:
        x = WIDTH / 2
        y = 620 - RAIO
        velocidade_y = 0
        apoiado = True

    tela.fill((190, 225, 250))

    for plataforma in plataformas:
        pygame.draw.rect(
            tela,
            (235, 130, 35),
            (
                plataforma["x"],
                plataforma["y"],
                plataforma["largura"],
                16,
            ),
        )

    pygame.draw.circle(
        tela,
        (110, 55, 170),
        (int(x), int(y)),
        RAIO,
    )

    pygame.display.update()
    relogio.tick(FPS)

pygame.quit()