import random
import pygame


# ===== Configurações =====
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

vel_agua = 1.50
a_agua = 0.02

CEU = (190, 225, 250)
LARANJA = (235, 130, 35)
AZUL = (35, 135, 225)
PERSONAGEM = (110, 55, 170)
TEXTO = (25, 40, 65)
BRANCO = (255, 255, 255)


def criar_jogo():
    plataformas = [{
        "x": 125, "y": 620, "largura": 170,
    }]
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
        "velocidade_y": 0,
        "apoiado": True,
        "vidas": 3,
        "agua_y": altura + 80,
        "camera_y": 0,
        "checkpoint": 0,
        "plataformas": plataformas,
        "estado": "jogando",
    }


def atualizar_camera(jogo):
    topo_fase = altura - F_altura
    jogo["camera_y"] = max(topo_fase, min(0, jogo["y"] - 300))


def perder_vida(jogo):
    jogo["vidas"] -= 1

    if jogo["vidas"] == 0:
        jogo["estado"] = "perdeu"
    else:
        plataforma = jogo["plataformas"][jogo["checkpoint"]]
        jogo["x"] = plataforma["x"] + plataforma["largura"] / 2
        jogo["y"] = plataforma["y"] - raio
        jogo["velocidade_y"] = 0
        jogo["apoiado"] = True
        jogo["agua_y"] = plataforma["y"] + 240
        atualizar_camera(jogo)


def atualizar_jogo(jogo, direcao, pular):
    if jogo["estado"] != "jogando":
        return

    jogo["x"] += direcao * anda
    jogo["x"] = max(raio, min(compri - raio, jogo["x"]))

    if pular and jogo["apoiado"]:
        jogo["velocidade_y"] = pulo
        jogo["apoiado"] = False

    pe_anterior = jogo["y"] + raio
    jogo["velocidade_y"] += gra
    jogo["y"] += jogo["velocidade_y"]
    jogo["apoiado"] = False

    if jogo["velocidade_y"] >= 0:
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
                jogo["velocidade_y"] = 0
                jogo["apoiado"] = True
                jogo["checkpoint"] = max(jogo["checkpoint"], numero)
                break

    atualizar_camera(jogo)

    jogo["agua_y"] -= vel_agua + jogo["checkpoint"] * a_agua

    tocou_agua = jogo["y"] + raio >= jogo["agua_y"]
    if tocou_agua:
        perder_vida(jogo)


def escrever(tela, fonte, texto, x, y, cor=TEXTO):
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, (x, y))


def desenhar_jogo(tela, jogo, fonte, fonte_pequena, fonte_grande):
    camera = jogo["camera_y"]
    tela.fill(CEU)

    for plataforma in jogo["plataformas"]:
        y_tela = int(plataforma["y"] - camera)
        pygame.draw.rect(tela, LARANJA, (
            int(plataforma["x"]), y_tela, plataforma["largura"], 16
        ))

    pygame.draw.circle(tela, PERSONAGEM,
                       (int(jogo["x"]), int(jogo["y"] - camera)), raio)
    pygame.draw.circle(tela, BRANCO,
                       (int(jogo["x"]), int(jogo["y"] - camera)), raio, 2)

    agua_tela = max(0, int(jogo["agua_y"] - camera))
    if agua_tela < altura:
        pygame.draw.rect(tela, AZUL, (0, agua_tela, compri, altura - agua_tela))
        pygame.draw.line(tela, (150, 220, 255),
                         (0, agua_tela), (compri, agua_tela), 4)

    pygame.draw.rect(tela, BRANCO, (10, altura - 35, 85, 25))
    escrever(tela, fonte_pequena, f"Vidas: {jogo['vidas']}", 18, altura - 31)

    if jogo["estado"] != "jogando":
        pygame.draw.rect(tela, TEXTO, (20, 250, compri - 40, 180))

        titulo = "FIM DE JOGO"
        mensagem = "A enchente venceu desta vez."
        imagem = fonte_grande.render(titulo, True, BRANCO)
        tela.blit(imagem, ((compri - imagem.get_width()) // 2, 275))
        escrever(tela, fonte_pequena, mensagem, 45, 330, BRANCO)
        escrever(tela, fonte_pequena, "R: jogar de novo | Esc: sair", 45, 375, BRANCO)


def main():
    pygame.display.init()
    pygame.font.init()
    tela = pygame.display.set_mode((compri, altura))
    pygame.display.set_caption("Parkour da enchente")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 30)
    fonte_pequena = pygame.font.Font(None, 23)
    fonte_grande = pygame.font.Font(None, 42)
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
                elif evento.key == pygame.K_r and jogo["estado"] != "jogando":
                    jogo = criar_jogo()

        if not rodando:
            break

        teclas = pygame.key.get_pressed()
        direcao = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            direcao -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            direcao += 1

        atualizar_jogo(jogo, direcao, pular)
        desenhar_jogo(tela, jogo, fonte, fonte_pequena, fonte_grande)
        pygame.display.update()
        relogio.tick(vel)

    pygame.quit()


if __name__ == "__main__":
    main()