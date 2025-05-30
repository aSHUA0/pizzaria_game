import pygame
import threading
import time

pygame.init()
WIDTH, HEIGHT = 1250, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
TABLE_COLOR = (100, 50, 20)
DOUGH_COLOR = (0, 255, 0)
ROLLER_COLOR = (255, 255, 0)
PIZZA_READY_COLOR = (255, 100, 100)

# Configurações visuais
altura_mesa = 300
altura_cliente = 150
largura_cliente = 80
espaco_entre_clientes = 40
y = HEIGHT // 2
vel_queda = 0
gravidade = 0.01
chao = altura_mesa - 100

# Estados dos objetos
queda_rolo = False
queda_massa = False
queda_massaAberta = False
movendoMassa = False
movendoRolo = False
movendoMassaAberta = False
mostrarMassa = True
pizza_pronta = False

# Semaforo e threads
pizza_semaforo = threading.Semaphore(1)
cliente_esperando = None  # Cliente que está esperando pela pizza
cliente_comendo = None    # Cliente que está comendo

def cliente_aguarda_pizza(id_cliente):
    global cliente_esperando, cliente_comendo
    
    clientes_estado[id_cliente] = "esperando"
    cliente_esperando = id_cliente
    
    # Aguarda até que a pizza esteja pronta e entregue
    while not pizza_pronta or not any(cliente.colliderect(massa_aberta) for cliente in clientes):
        time.sleep(0.1)
    
    pizza_semaforo.acquire()
    clientes_estado[id_cliente] = "comendo"
    cliente_comendo = id_cliente
    cliente_esperando = None
    
    # Tempo para "comer" a pizza
    time.sleep(2)
    
    clientes_estado[id_cliente] = "idle"
    cliente_comendo = None
    pizza_semaforo.release()

# Inicialização dos clientes
cliente_y = HEIGHT - altura_mesa - altura_cliente
cliente1_x = 800

clientes = []
num_clientes = 3
clientes_estado = {i + 1: "idle" for i in range(num_clientes)}
for i in range(num_clientes):
    x = cliente1_x + i * (largura_cliente + espaco_entre_clientes)
    clientes.append(pygame.Rect(x, cliente_y, largura_cliente, altura_cliente))

# Objetos da cena
mesa = pygame.Rect(0, HEIGHT - altura_mesa, WIDTH, altura_mesa)
massa = pygame.Rect(50, 740, 100, 100)
massa_aberta = pygame.Rect(150, 500, 100, 150)
rolo = pygame.Rect(50, 640, 100, 50)

# Fonte para texto
font = pygame.font.SysFont('Arial', 24)
semaphore_font = pygame.font.SysFont('Arial', 32, bold=True)

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
            elif any(cliente.collidepoint(pygame.mouse.get_pos()) for cliente in clientes):
                # Inicia thread para cliente esperar pela pizza
                cliente_id = [i+1 for i, c in enumerate(clientes) if c.collidepoint(pygame.mouse.get_pos())][0]
                if clientes_estado[cliente_id] == "idle":
                    threading.Thread(target=cliente_aguarda_pizza, args=(cliente_id,)).start()

    # Movimento dos objetos
    if movendoMassa:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if not mesa.collidepoint((mouse_x, mouse_y)):
            queda_massa = True
            vel_queda = 0
        massa.center = (mouse_x, mouse_y)
    
    if movendoMassaAberta:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if not mesa.collidepoint((mouse_x, mouse_y)):
            queda_massaAberta = True
            vel_queda = 0
        massa_aberta.center = (mouse_x, mouse_y)

    if movendoRolo:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if not mesa.collidepoint((mouse_x, mouse_y)):
            queda_rolo = True
            vel_queda = 0
        rolo.center = (mouse_x, mouse_y)
        if massa.colliderect(rolo):
            mostrarMassa = False
            pizza_pronta = True

    # Física dos objetos
    topo_mesa = mesa.top + 150
    if queda_massa:
        vel_queda += gravidade
        massa.y += vel_queda
        if massa.bottom >= topo_mesa:
            massa.bottom = topo_mesa
            queda_massa = False
            vel_queda = 0
        
    if queda_rolo:
        vel_queda += gravidade
        rolo.y += vel_queda
        if rolo.bottom >= topo_mesa:
            rolo.bottom = topo_mesa
            queda_rolo = False
            vel_queda = 0
    
    if queda_massaAberta:
        vel_queda += gravidade
        massa_aberta.y += vel_queda
        if massa_aberta.bottom >= topo_mesa:
            massa_aberta.bottom = topo_mesa
            queda_massaAberta = False
            vel_queda = 0

    # Verifica se a massa aberta foi entregue a algum cliente
    for i, cliente in enumerate(clientes):
        if massa_aberta.colliderect(cliente):
            clientes_estado[i+1] = "recebendo"
            # Marca a pizza como entregue
            pizza_pronta = False

    # Renderização
    screen.fill(WHITE)
    
    # Mesa
    pygame.draw.rect(screen, TABLE_COLOR, mesa)
    
    # Objetos
    if mostrarMassa:
        pygame.draw.rect(screen, DOUGH_COLOR, massa)
    else:
        pygame.draw.rect(screen, PIZZA_READY_COLOR if pizza_pronta else DOUGH_COLOR, massa_aberta)
    
    pygame.draw.rect(screen, ROLLER_COLOR, rolo)
    
    # Clientes
    for i in range(len(clientes)):
        id_cliente = i + 1
        estado = clientes_estado[id_cliente]

        # Cor baseada no estado
        if estado == "comendo":
            cor = GREEN
        elif estado == "esperando":
            cor = YELLOW
        elif estado == "recebendo":
            cor = BLUE
        else:
            cor = BLACK

        pygame.draw.rect(screen, cor, clientes[i])
        
        # Texto do estado
        texto = font.render(f"Cliente {id_cliente}: {estado}", True, BLACK)
        screen.blit(texto, (clientes[i].x, clientes[i].y - 25))
    
    # Painel de informações do semáforo
    semaphore_value = pizza_semaforo._value
    semaphore_text = semaphore_font.render(f"SEMÁFORO: {semaphore_value}", True, 
                                         GREEN if semaphore_value > 0 else RED)
    screen.blit(semaphore_text, (50, 50))
    
    # Status da pizza
    pizza_status = "PRONTA" if pizza_pronta else "EM PREPARO"
    status_text = font.render(f"Pizza: {pizza_status}", True, BLACK)
    screen.blit(status_text, (50, 90))
    
    # Instruções
    instructions = [
        "Clique nos clientes para pedir pizza",
        "Arraste a massa e o rolo para preparar a pizza",
        "Leve a massa aberta até o cliente para entregar",
        "Semaforo verde: recurso disponível",
        "Semaforo vermelho: recurso em uso"
    ]
    
    for idx, instruction in enumerate(instructions):
        text = font.render(instruction, True, BLACK)
        screen.blit(text, (50, 130 + idx * 30))
    
    pygame.display.flip()

pygame.quit()