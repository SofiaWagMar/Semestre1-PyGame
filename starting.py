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