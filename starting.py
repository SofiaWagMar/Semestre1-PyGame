import random
import pygame

compri = 420
altura = 700
vel = 60

raio = 14
gra = 0.5
pulo = -12
anda = 4

T_plat = 25
D_plat = 85
F_altura = altura + (T_plat - 1) * D_plat

CEU = (190, 225, 250)
LARANJA = (235, 130, 35)
PERSONAGEM = (110, 55, 170)
BRANCO = (255, 255, 255)


def criar_jogo():
    plataformas = [
        {"x": 125, "y": 620, "largura": 170},
    ]
    centro = compri / 2

    for numero in range(1, T_plat):
        centro += random.choice([-95, -65, 65, 95])
        centro = max(70, min(compri - 70, centro))

        plataformas.append({
            "x": centro - 55,
            "y": 620 - numero * D_plat,
            "largura": 110,
        })

    return {
        "x": compri / 2,
        "y": plataformas[0]["y"] - raio,
        "anda_y": 0,
        "apoiado": True,
        "camera_y": 0,
        "checkpoint": 0,
        "plataformas": plataformas,
        "estado": "jogando",
    }


def atualizar_camera(jogo):
    topo_fase = altura - F_altura
    jogo["camera_y"] = max(topo_fase, min(0, jogo["y"] - 300))


def atualizar_jogo(jogo, direcao, pular):
    if jogo["estado"] != "jogando":
        return

    jogo["x"] += direcao * anda
    jogo["x"] = max(raio, min(compri - raio, jogo["x"]))

    if pular and jogo["apoiado"]:
        jogo["anda_y"] = pulo
        jogo["apoiado"] = False

    pe_anterior = jogo["y"] + raio
    jogo["anda_y"] += gra
    jogo["y"] += jogo["anda_y"]
    jogo["apoiado"] = False

    if jogo["anda_y"] >= 0:
        for numero in range(len(jogo["plataformas"]) - 1, -1, -1):
            plataforma = jogo["plataformas"][numero]

            sobre_plataforma = (
                jogo["x"] + raio > plataforma["x"]
                and jogo["x"] - raio < plataforma["x"] + plataforma["largura"]
            )

            cruzou_topo = (
                pe_anterior <= plataforma["y"]
                and jogo["y"] + raio >= plataforma["y"]
            )

            if sobre_plataforma and cruzou_topo:
                jogo["y"] = plataforma["y"] - raio
                jogo["anda_y"] = 0
                jogo["apoiado"] = True
                jogo["checkpoint"] = max(jogo["checkpoint"], numero)
                break

    atualizar_camera(jogo)


def desenhar_jogo(tela, jogo):
    camera = jogo["camera_y"]
    tela.fill(CEU)

    for plataforma in jogo["plataformas"]:
        y_tela = int(plataforma["y"] - camera)

        pygame.draw.rect(
            tela,
            LARANJA,
            (
                int(plataforma["x"]),
                y_tela,
                plataforma["largura"],
                16,
            ),
        )

    posicao = (int(jogo["x"]), int(jogo["y"] - camera))
    pygame.draw.circle(tela, PERSONAGEM, posicao, raio)
    pygame.draw.circle(tela, BRANCO, posicao, raio, 2)


def main():
    pygame.display.init()

    tela = pygame.display.set_mode((compri, altura))
    pygame.display.set_caption("Parkour da enchente")

    relogio = pygame.time.Clock()
    jogo = criar_jogo()
    rodando = True

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
        direcao = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            direcao -= 1

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            direcao += 1

        atualizar_jogo(jogo, direcao, pular)
        desenhar_jogo(tela, jogo)

        pygame.display.update()
        relogio.tick(vel)

    pygame.quit()


if __name__ == "__main__":
    main() 