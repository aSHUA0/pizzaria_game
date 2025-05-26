import pygame

pygame.init()
WIDTH, HEIGHT = 1250, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))

altura_mesa = 300
altura_cliente = 150
largura_cliente = 80
espaco_entre_clientes = 40
raio = 30
movendoMassa = False
movendoRolo = False
movendoMassaAberta = False
mostrarMassa = True


# Y fixo para todos os clientes (acima da mesa)
cliente_y = HEIGHT - altura_mesa - altura_cliente

# Posição inicial X do primeiro cliente
cliente1_x = 800  # escolha conforme sua tela e tamanho da mesa

# Criar 3 clientes lado a lado
clientes = []
num_clientes = 3
for i in range(num_clientes):
    x = cliente1_x + i * (largura_cliente + espaco_entre_clientes)
    clientes.append(pygame.Rect(x, cliente_y, largura_cliente, altura_cliente))

mesa = pygame.Rect(0, HEIGHT - altura_mesa, WIDTH, altura_mesa)
massa = pygame.Rect(100, 100, 100, 100)
massa_aberta = pygame.Rect(150, 100, 100, 150)
rolo = pygame.Rect(100, 500, 100, 50)

# Cor da mesa
cor_mesa = (100, 50, 20)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if massa.collidepoint(pygame.mouse.get_pos()):
                movendoMassa = not movendoMassa
            elif rolo.collidepoint(pygame.mouse.get_pos()):
                movendoRolo = not movendoRolo
            elif massa_aberta.collidepoint(pygame.mouse.get_pos()):
                movendoMassaAberta = not movendoMassaAberta

    if movendoMassa:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        massa.center = (mouse_x, mouse_y)
    
    if movendoMassaAberta:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        massa_aberta.center = (mouse_x, mouse_y)

    if movendoRolo:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rolo.center = (mouse_x, mouse_y)
        if massa.center == rolo.center:
            mostrarMassa = False

    screen.fill((255, 255, 255))  # fundo branco
    
    pygame.draw.rect(screen, cor_mesa, mesa)
    
    for i in range(len(clientes)):
        pygame.draw.rect(screen, (0, 0, 0), clientes[i])

    if mostrarMassa:
        pygame.draw.rect(screen, (0, 255, 0), massa)
    else:
        pygame.draw.rect(screen, (0, 255, 0), massa_aberta)


    pygame.draw.rect(screen, (255, 255, 0), rolo)


    pygame.display.flip()

pygame.quit()