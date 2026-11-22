import random
from pathlib import Path
import pygame

# ===== Confirgurações =====
compri = 420
altura = 700
vel = 60

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
LARANJA_ESCURO = (210, 105, 20)
LARANJA_CLARO = (255, 190, 100)
TEXTO = (25, 40, 65)
BRANCO = (255, 255, 255)


def criar_jogo(fase=1):
    total_plataformas = T_plat
    quantidade_frageis = (total_plataformas - 2) * fase // (fase + 2)
    frageis = random.sample(range(1, total_plataformas - 1), quantidade_frageis)

    plataformas = [{
        "x": 125,
        "y": 620,
        "largura": 170,
        "fragil": False,
        "pisada_em": None,
        "quebrada": False,
    }]

    centro = compri / 2

    for numero in range(1, total_plataformas):
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
            "fragil": numero in frageis,
            "pisada_em": None,
            "quebrada": False,
        })

    return {
        "fase": fase,
        "altura_fase": altura + (total_plataformas - 1) * D_plat,
        "vel_agua": vel_agua + (fase - 1) * 0.75,
        "a_agua": a_agua + (fase - 1) * 0.02,
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
    topo_fase = altura - jogo["altura_fase"]
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

    jogo["agua_y"] -= jogo["vel_agua"] + jogo["checkpoint"] * jogo["a_agua"]

    if jogo["y"] + raio >= jogo["agua_y"]:
        perder_vida(jogo)
    elif jogo["checkpoint"] == len(jogo["plataformas"]) - 1:
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


def desenhar_menu(tela, fonte, botoes, fundo_menu):
    tela.blit(fundo_menu, (0, 0))
    mouse = pygame.mouse.get_pos()

    for texto, retangulo in botoes.items():
        cor = (
            LARANJA_ESCURO
            if retangulo.collidepoint(mouse)
            else LARANJA
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
        "Suba pelas plataformas e escape da lava!", 200,
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
        "Você tem 3 vidas. Evite tocar na lava.", 380,
    )

    escrever_centralizado(
        tela, fonte_pequena,
        "R: avançar ou recomeçar da fase 1", 420,
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

        recorte = imagem.get_bounding_rect(min_alpha=8)

        if recorte.width == 0 or recorte.height == 0:
            raise ValueError(
                f"A imagem {caminho.name} está totalmente transparente."
            )

        imagem = imagem.subsurface(recorte).copy()

        
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


def carregar_lava(pasta):
    imagem = pygame.image.load(str(pasta / "lava.png")).convert_alpha()
    recorte = imagem.get_bounding_rect(min_alpha=8)

    if recorte.width == 0 or recorte.height == 0:
        raise ValueError("A imagem lava.png está totalmente transparente.")

    imagem = imagem.subsurface(recorte).copy()
    altura_textura = max(1, round(imagem.get_height() * compri / imagem.get_width()))
    topo = pygame.transform.smoothscale(imagem, (compri, altura_textura))

    inicio_corpo = topo.get_height() * 2 // 3
    corpo = topo.subsurface(
        (0, inicio_corpo, compri, topo.get_height() - inicio_corpo)
    ).copy().convert()

    return topo, corpo

def desenhar_lava(tela, y_lava, lava):
    if y_lava >= altura:
        return

    topo, corpo = lava
    altura_corpo = corpo.get_height()
    y_corpo = y_lava + topo.get_height()

    if y_corpo < 0:
        y_corpo += ((-y_corpo) // altura_corpo) * altura_corpo

    for y in range(y_corpo, altura, altura_corpo):
        tela.blit(corpo, (0, y))

    if y_lava + topo.get_height() > 0:
        tela.blit(topo, (0, y_lava))


def desenhar_jogo(
    tela, jogo, fonte, fonte_pequena, fonte_grande, fundo, sprites, lava
):
    camera = jogo["camera_y"]

    tela.blit(
        fundo,
        (0, int(altura - jogo["altura_fase"] - camera)),
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

    if not jogo["apoiado"]:
        pose = "pulo"
    else:
        pose = jogo["olhando"]

    imagem = sprites[pose]

    retangulo = imagem.get_rect(
        midbottom=(
            int(jogo["x"]),
            int(jogo["y"] - camera + raio),
        )
    )

    retangulo.left = max(
        0,
        min(compri - retangulo.width, retangulo.left),
    )

    tela.blit(imagem, retangulo)

    y_lava = int(jogo["agua_y"] - camera)
    desenhar_lava(tela, y_lava, lava)

    pygame.draw.rect(
        tela, BRANCO,
        (10, altura - 35, 200, 25),
    )

    escrever(
        tela, fonte_pequena,
        f"Vidas: {jogo['vidas']}   Fase: {jogo['fase']}",
        18, altura - 31,
    )

    if jogo["estado"] != "jogando":
        pygame.draw.rect(
            tela, TEXTO,
            (20, 250, compri - 40, 180),
        )

        if jogo["estado"] == "venceu":
            titulo = "VOCE ESCAPOU!"
            mensagem = f"Fase {jogo['fase']} concluida!"
            comando = "R: proxima fase | Esc: sair"
        else:
            titulo = "FIM DE JOGO"
            mensagem = "A lava te alcançou desta vez."
            comando = "R: voltar a fase 1 | Esc: sair"

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
            comando,
            45, 375, BRANCO,
        )


def main():
    pygame.display.init()
    pygame.font.init()

    tela = pygame.display.set_mode(
        (compri, altura)
    )

    pygame.display.set_caption(
        "Parkour da lava"
    )

    pasta = Path(__file__).resolve().parent

    
    fundo_menu = pygame.image.load(
        str(pasta / "imagem3.png")
    ).convert()
    fundo_menu = pygame.transform.smoothscale(
        fundo_menu, (compri, altura)
    )

    
    sprites = carregar_sprites(pasta)
    lava = carregar_lava(pasta)

    
    fundo_original = pygame.image.load(
        str(pasta / "imagem2.png")
    ).convert()

    fundo = pygame.transform.scale(
        fundo_original,
        (compri, F_altura),
    )

    relogio = pygame.time.Clock()

    fonte = pygame.font.Font(None, 30)
    fonte_pequena = pygame.font.Font(None, 23)
    fonte_grande = pygame.font.Font(None, 42)

    jogo = None
    tela_atual = "menu"

    botoes = {
        "Jogar": pygame.Rect(110, 480, 200, 65),
        "Sair": pygame.Rect(110, 570, 200, 65),
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
                        fase = 1
                        if jogo["estado"] == "venceu":
                            fase = jogo["fase"] + 1
                        jogo = criar_jogo(fase)
                        fundo = pygame.transform.scale(
                            fundo_original,
                            (compri, jogo["altura_fase"]),
                        )

        if not rodando:
            break

        if tela_atual == "menu":
            desenhar_menu(
                tela,
                fonte_grande,
                botoes,
                fundo_menu,
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
                lava,
            )

        pygame.display.update()
        relogio.tick(vel)

    pygame.quit()


if __name__ == "__main__":
    main()