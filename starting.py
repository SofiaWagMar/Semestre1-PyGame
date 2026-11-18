import pygame

pygame.display.init()

compri = 420
altura = 700
vel = 60

tela = pygame.display.set_mode((compri, altura))
pygame.display.set_caption("Parkour da enchente")

relogio = pygame.time.Clock()
rodando = True

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False

    if not rodando:
        break

    tela.fill((190, 225, 250))

    pygame.display.update()
    relogio.tick(vel)

pygame.quit()