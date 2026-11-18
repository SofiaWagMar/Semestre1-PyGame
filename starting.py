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

x = compri / 2
y = 620 - raio

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False

    if not rodando:
        break

    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        x -= anda

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        x += anda

    # Impede que o personagem saia pelas laterais.
    x = max(raio, min(compri - raio, x))

    tela.fill((190, 225, 250))

    pygame.draw.circle(
        tela,
        (110, 55, 170),
        (int(x), int(y)),
        raio,
    )

    pygame.display.update()
    relogio.tick(vel)

pygame.quit()