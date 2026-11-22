import random
from pathlib import Path
import pygame

# ===== Configurações =====
compri = 420
altura = 700
vel = 60

# Tamanho visual da personagem.
ALTURA_PERSONAGEM = 64
LARGURA_MAX_PERSONAGEM = 56

raio = 14
gra = 0.5
pulo = -12
anda = 4

T_plat = 25
D_plat = 110
F_altura = altura + (T_plat - 1) * D_plat

T_quebra = 2000
vel_agua = 1.50
a_agua = 0.02

LARANJA = (235, 130, 35)
VERMELHO = (220, 65, 70)
AZUL = (35, 135, 225)
TEXTO = (25, 40, 65)
BRANCO = (255, 255, 255)


def criar_jogo():
    plataformas = [{
        "x": 125,
        "y": 620,
        "largura": 170,
        "fragil": False,
        "pisada_em": None,
        "quebrada": False,
    }]

    centro = compri / 2

    for numero in range(1, T_plat):
        largura = random.choice([80, 100, 125, 150])
        centros_possiveis = []

        for deslocamento in [-135, -115, 115, 135]:
            novo_centro = centro + deslocamento

            if largura / 2 + 18 <= novo_centro <= compri - largura / 2 - 18:
                centros_possiveis.append(novo_centro)

        centro = random.choice(centros_possiveis)

        plataformas.append({
            "x": centro - largura / 2,
            "y": 620 - numero * D_plat,
            "largura": largura,
            "fragil": numero % 3 == 2 and numero != T_plat - 1,
            "pisada_em": None,
            "quebrada": False,
        })

    return {
        "x": compri / 2,
        "y": plataformas[0]["y"] - raio,
        "velocidade_y": 0,
        "apoiado": True,
        "olhando": "direita",
        "plataforma_atual": 0,
        "vidas": 3,
        "agua_y": altura + 80,
        "camera_y": 0,
        "checkpoint": 0,
        "plataformas": plataformas,
        "estado": "jogando",
    }


def atualizar_camera(jogo):
    topo_fase = altura - F_altura
    jogo["camera_y"] = max(
        topo_fase,
        min(0, jogo["y"] - 300),
    )


def perder_vida(jogo):
    jogo["vidas"] -= 1

    if jogo["vidas"] == 0:
        jogo["estado"] = "perdeu"
    else:
        for plataforma in jogo["plataformas"]:
            plataforma["pisada_em"] = None
            plataforma["quebrada"] = False

        plataforma = jogo["plataformas"][jogo["checkpoint"]]

        jogo["x"] = plataforma["x"] + plataforma["largura"] / 2
        jogo["y"] = plataforma["y"] - raio
        jogo["velocidade_y"] = 0
        jogo["apoiado"] = True
        jogo["plataforma_atual"] = jogo["checkpoint"]
        jogo["agua_y"] = plataforma["y"] + 240

        atualizar_camera(jogo)


def atualizar_jogo(jogo, direcao, pular, agora=None):
    if jogo["estado"] != "jogando":
        return

    if agora is None:
        agora = pygame.time.get_ticks()

    for numero in range(len(jogo["plataformas"])):
        plataforma = jogo["plataformas"][numero]

        if plataforma["fragil"] and plataforma["pisada_em"] is not None:
            if agora - plataforma["pisada_em"] >= T_quebra:
                plataforma["quebrada"] = True

                if jogo["plataforma_atual"] == numero:
                    jogo["apoiado"] = False
                    jogo["plataforma_atual"] = None

    # Guarda o último lado usado.
    if direcao < 0:
        jogo["olhando"] = "esquerda"
    elif direcao > 0:
        jogo["olhando"] = "direita"

    jogo["x"] += direcao * anda
    jogo["x"] = max(raio, min(compri - raio, jogo["x"]))

    if pular and jogo["apoiado"]:
        jogo["velocidade_y"] = pulo
        jogo["apoiado"] = False

    pe_anterior = jogo["y"] + raio

    jogo["velocidade_y"] += gra
    jogo["y"] += jogo["velocidade_y"]
    jogo["apoiado"] = False
    jogo["plataforma_atual"] = None

    if jogo["velocidade_y"] >= 0:
        for numero in range(len(jogo["plataformas"]) - 1, -1, -1):
            plataforma = jogo["plataformas"][numero]

            if plataforma["quebrada"]:
                continue

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
                jogo["plataforma_atual"] = numero
                jogo["checkpoint"] = max(
                    jogo["checkpoint"],
                    numero,
                )

                if plataforma["fragil"] and plataforma["pisada_em"] is None:
                    plataforma["pisada_em"] = agora

                break

    atualizar_camera(jogo)

    jogo["agua_y"] -= vel_agua + jogo["checkpoint"] * a_agua

    if jogo["y"] + raio >= jogo["agua_y"]:
        perder_vida(jogo)
    elif jogo["checkpoint"] == T_plat - 1:
        jogo["estado"] = "venceu"


def escrever(tela, fonte, texto, x, y, cor=TEXTO):
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, (x, y))


def escrever_centralizado(tela, fonte, texto, y, cor=TEXTO):
    imagem = fonte.render(texto, True, cor)

    tela.blit(
        imagem,
        ((compri - imagem.get_width()) // 2, y),
    )


def desenhar_menu(tela, fonte, botoes):
    tela.fill(BRANCO)
    mouse = pygame.mouse.get_pos()

    for texto, retangulo in botoes.items():
        cor = (
            (220, 220, 220)
            if retangulo.collidepoint(mouse)
            else (245, 245, 245)
        )

        pygame.draw.rect(tela, cor, retangulo)
        pygame.draw.rect(tela, TEXTO, retangulo, 2)

        imagem = fonte.render(texto, True, TEXTO)

        tela.blit(
            imagem,
            imagem.get_rect(center=retangulo.center),
        )


def desenhar_instrucoes(tela, fonte, fonte_pequena, fonte_grande):
    tela.fill(BRANCO)

    escrever_centralizado(
        tela, fonte_grande,
        "Como jogar", 130,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "Suba pelas plataformas e escape da enchente!", 200,
    )

    escrever_centralizado(
        tela, fonte,
        "A / D ou setas: mover", 270,
    )

    escrever_centralizado(
        tela, fonte,
        "Espaço ou seta para cima: pular", 315,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "Você tem 3 vidas. Evite tocar na água.", 380,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "R: recomeçar após ganhar ou perder", 420,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "Esc: sair do jogo", 455,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "Vermelhas: quebram 2 segundos após pisar!", 495,
    )

    escrever_centralizado(
        tela, fonte,
        "Pressione ESPAÇO para começar", 545,
    )


def carregar_sprites(pasta):
    sprites = {}

    for pose in ("direita", "esquerda", "pulo"):
        caminho = pasta / f"escaladora_{pose}.png"

        imagem = pygame.image.load(
            str(caminho)
        ).convert_alpha()

        # Remove as margens transparentes.
        recorte = imagem.get_bounding_rect(min_alpha=8)

        if recorte.width == 0 or recorte.height == 0:
            raise ValueError(
                f"A imagem {caminho.name} está totalmente transparente."
            )

        imagem = imagem.subsurface(recorte).copy()

        # Aumenta a personagem mantendo a proporção.
        escala = min(
            ALTURA_PERSONAGEM / imagem.get_height(),
            LARGURA_MAX_PERSONAGEM / imagem.get_width(),
        )

        tamanho = (
            max(1, round(imagem.get_width() * escala)),
            max(1, round(imagem.get_height() * escala)),
        )

        sprites[pose] = pygame.transform.smoothscale(
            imagem,
            tamanho,
        )

    return sprites


def desenhar_jogo(
    tela, jogo, fonte, fonte_pequena, fonte_grande, fundo, sprites
):
    camera = jogo["camera_y"]

    tela.blit(
        fundo,
        (0, int(altura - F_altura - camera)),
    )

    for plataforma in jogo["plataformas"]:
        if plataforma["quebrada"]:
            continue

        y_tela = int(plataforma["y"] - camera)
        cor = VERMELHO if plataforma["fragil"] else LARANJA

        pygame.draw.rect(
            tela, cor,
            (
                int(plataforma["x"]),
                y_tela,
                plataforma["largura"],
                16,
            ),
        )

        if plataforma["fragil"]:
            centro_x = int(
                plataforma["x"] + plataforma["largura"] / 2
            )

            pygame.draw.lines(
                tela, TEXTO, False,
                [
                    (centro_x + 3, y_tela),
                    (centro_x - 3, y_tela + 6),
                    (centro_x + 3, y_tela + 10),
                    (centro_x - 3, y_tela + 15),
                ],
                2,
            )

            if plataforma["pisada_em"] is not None:
                tempo_passado = (
                    pygame.time.get_ticks()
                    - plataforma["pisada_em"]
                )

                restante = max(
                    0,
                    1 - tempo_passado / T_quebra,
                )

                pygame.draw.rect(
                    tela, BRANCO,
                    (
                        int(plataforma["x"]),
                        y_tela + 17,
                        int(plataforma["largura"] * restante),
                        3,
                    ),
                )

    ultima = jogo["plataformas"][-1]
    bandeira_x = int(ultima["x"] + ultima["largura"] / 2)
    bandeira_y = int(ultima["y"] - camera)

    pygame.draw.line(
        tela, TEXTO,
        (bandeira_x, bandeira_y),
        (bandeira_x, bandeira_y - 55),
        3,
    )

    pygame.draw.rect(
        tela, (40, 165, 95),
        (bandeira_x, bandeira_y - 55, 32, 20),
    )

    # Usa a pose de pulo durante todo o tempo no ar.
    if not jogo["apoiado"]:
        pose = "pulo"
    else:
        pose = jogo["olhando"]

    imagem = sprites[pose]

    # Mantém os pés alinhados à plataforma.
    retangulo = imagem.get_rect(
        midbottom=(
            int(jogo["x"]),
            int(jogo["y"] - camera + raio),
        )
    )

    # Evita cortar a personagem nas laterais da janela.
    retangulo.left = max(
        0,
        min(compri - retangulo.width, retangulo.left),
    )

    tela.blit(imagem, retangulo)

    agua_tela = max(
        0,
        int(jogo["agua_y"] - camera),
    )

    if agua_tela < altura:
        pygame.draw.rect(
            tela, AZUL,
            (0, agua_tela, compri, altura - agua_tela),
        )

        pygame.draw.line(
            tela, (150, 220, 255),
            (0, agua_tela),
            (compri, agua_tela),
            4,
        )

    pygame.draw.rect(
        tela, BRANCO,
        (10, altura - 35, 85, 25),
    )

    escrever(
        tela, fonte_pequena,
        f"Vidas: {jogo['vidas']}",
        18, altura - 31,
    )

    if jogo["estado"] != "jogando":
        pygame.draw.rect(
            tela, TEXTO,
            (20, 250, compri - 40, 180),
        )

        if jogo["estado"] == "venceu":
            titulo = "VOCE ESCAPOU!"
            mensagem = "Voce chegou ao lugar seguro."
        else:
            titulo = "FIM DE JOGO"
            mensagem = "A enchente venceu desta vez."

        imagem = fonte_grande.render(
            titulo, True, BRANCO,
        )

        tela.blit(
            imagem,
            ((compri - imagem.get_width()) // 2, 275),
        )

        escrever(
            tela, fonte_pequena,
            mensagem, 45, 330, BRANCO,
        )

        escrever(
            tela, fonte_pequena,
            "R: jogar de novo | Esc: sair",
            45, 375, BRANCO,
        )


def main():
    pygame.display.init()
    pygame.font.init()

    tela = pygame.display.set_mode(
        (compri, altura)
    )

    pygame.display.set_caption(
        "Parkour da enchente"
    )

    pasta = Path(__file__).resolve().parent

    # Carrega as imagens da personagem.
    sprites = carregar_sprites(pasta)

    # Carrega a imagem de fundo.
    fundo = pygame.image.load(
        str(pasta / "imagem.png")
    ).convert()

    fundo = pygame.transform.scale(
        fundo,
        (compri, F_altura),
    )

    relogio = pygame.time.Clock()

    fonte = pygame.font.Font(None, 30)
    fonte_pequena = pygame.font.Font(None, 23)
    fonte_grande = pygame.font.Font(None, 42)

    jogo = None
    tela_atual = "menu"

    botoes = {
        "Jogar": pygame.Rect(110, 265, 200, 65),
        "Sair": pygame.Rect(110, 365, 200, 65),
    }

    rodando = True

    while rodando:
        pular = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif (
                evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
            ):
                if tela_atual == "menu":
                    if botoes["Jogar"].collidepoint(evento.pos):
                        tela_atual = "instrucoes"

                    elif botoes["Sair"].collidepoint(evento.pos):
                        rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

                elif (
                    tela_atual == "instrucoes"
                    and evento.key == pygame.K_SPACE
                ):
                    jogo = criar_jogo()
                    tela_atual = "jogo"

                elif tela_atual == "jogo":
                    if evento.key in (
                        pygame.K_SPACE,
                        pygame.K_UP,
                    ):
                        pular = True

                    elif (
                        evento.key == pygame.K_r
                        and jogo["estado"] != "jogando"
                    ):
                        jogo = criar_jogo()

        if not rodando:
            break

        if tela_atual == "menu":
            desenhar_menu(
                tela,
                fonte_grande,
                botoes,
            )

        elif tela_atual == "instrucoes":
            desenhar_instrucoes(
                tela,
                fonte,
                fonte_pequena,
                fonte_grande,
            )

        else:
            teclas = pygame.key.get_pressed()
            direcao = 0

            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                direcao -= 1

            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                direcao += 1

            atualizar_jogo(
                jogo,
                direcao,
                pular,
            )

            desenhar_jogo(
                tela,
                jogo,
                fonte,
                fonte_pequena,
                fonte_grande,
                fundo,
                sprites,
            )

        pygame.display.update()
        relogio.tick(vel)

    pygame.quit()


if __name__ == "__main__":
    main()