import os
import pygame
from config import values

caminho_imagem = os.path.join("..","pizzaria_game","assets")

#Imagens de pizza
pizza_calabresa = pygame.image.load(f'{caminho_imagem}\\Pizza\\calabresa.png').convert_alpha()
pizza_cogumelo = pygame.image.load(f'{caminho_imagem}\\Pizza\\cogumelo.png').convert_alpha()
pizza_marquerita = pygame.image.load(f'{caminho_imagem}\\Pizza\\marquerita.png').convert_alpha()
massa_aberta = pygame.image.load(f'{caminho_imagem}\\Pizza\\massa_aberta.png').convert_alpha()
massa = pygame.image.load(f'{caminho_imagem}\\Pizza\\massa.png').convert_alpha()

massa = pygame.transform.scale(massa, (100,100))
massa_aberta = pygame.transform.scale(massa_aberta, (200,200))
pizza_calabresa = pygame.transform.scale(pizza_calabresa, (200,200))
pizza_cogumelo = pygame.transform.scale(pizza_cogumelo, (200,200))
pizza_marquerita = pygame.transform.scale(pizza_marquerita, (200,200))

#Cliente

cliente_imgs = {
    "idle": pygame.image.load(f'{caminho_imagem}\\Cliente\\cliente.png').convert_alpha(),
    "esperando": pygame.image.load(f'{caminho_imagem}\\Cliente\\cliente_esperando.png').convert_alpha(),
    "comendo": pygame.image.load(f'{caminho_imagem}\\Cliente\\cliente_comendo.png').convert_alpha(),
    "erro": pygame.image.load(f'{caminho_imagem}\\Cliente\\cliente_puto.png').convert_alpha(),
    "recebendo": pygame.image.load(f'{caminho_imagem}\\Cliente\\cliente_recebendo.png').convert_alpha()
}

# Escale todas as imagens
for estado, img in cliente_imgs.items():
    cliente_imgs[estado] = pygame.transform.scale(img, (values.largura_cliente, values.altura_cliente))

pote_imgs = {
    "calabresa" : pygame.image.load(f'{caminho_imagem}\\Ingredientes\\pote_calabresa.png').convert_alpha(),
    "marquerita" : pygame.image.load(f'{caminho_imagem}\\Ingredientes\\pote_marquerita.png').convert_alpha(),
    "cogumelo" : pygame.image.load(f'{caminho_imagem}\\Ingredientes\\pote_cogumelo.png').convert_alpha()
}

# Escale todas as imagens
for ingrediente, img in pote_imgs.items():
    pote_imgs[ingrediente] = pygame.transform.scale(img, (values.largura_pote, values.altura_pote))

fundo = pygame.image.load(f'{caminho_imagem}\\Ingredientes\\fundo.png').convert_alpha()
rolo = pygame.image.load(f'{caminho_imagem}\\Ingredientes\\rolo.png').convert_alpha()

rolo = pygame.transform.scale(rolo, (200, 100))
fundo = pygame.transform.scale(fundo, (1250, 900))
