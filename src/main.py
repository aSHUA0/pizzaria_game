import pygame
import threading
import time
import classes
from config import color, states

def cliente_finalizou(id_cliente):
    global clientes, clientes_estado

    # Remove o cliente com esse ID
    clientes = [c for c in clientes if c["id"] != id_cliente]
    clientes_estado.pop(id_cliente, None)

    # Reposiciona os clientes restantes
    for i, cliente in enumerate(clientes):
        cliente["id"] = i + 1
        cliente["rect"].x = cliente1_x + i * (largura_cliente + espaco_entre_clientes)

    # Atualiza os estados com os novos IDs
    novos_estados = {}
    for i, cliente in enumerate(clientes):
        novos_estados[cliente["id"]] = clientes_estado.get(cliente["id"], "idle")
    clientes_estado.clear()
    clientes_estado.update(novos_estados)


pygame.init()
WIDTH, HEIGHT = 1250, 900       #Tamanho tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Configurações visuais
altura_mesa = 300
altura_cliente = 150
largura_cliente = 80
espaco_entre_clientes = 40
y = HEIGHT // 2
vel_queda = 0
gravidade = 0.01
chao = altura_mesa - 100

# Semaforo e threads
pizza_semaforo = threading.Semaphore(1)


# Inicialização dos clientes
cliente_y = HEIGHT - altura_mesa - altura_cliente
cliente1_x = 800

clientes = []
cliente_threads = []
num_clientes = 6
clientes_estado = {}

for i in range(num_clientes):
    id_cliente = i + 1
    x = cliente1_x + i * (largura_cliente + espaco_entre_clientes)
    rect = pygame.Rect(x, cliente_y, largura_cliente, altura_cliente)
    clientes_estado[id_cliente] = "idle"
    clientes.append({"id": id_cliente, "rect": rect})

# Objetos da cena
mesa = pygame.Rect(0, HEIGHT - altura_mesa, WIDTH, altura_mesa)
massa = classes.ObjetoFisico(50, 740, 100, 100, color.DOUGH_COLOR)
massa_aberta = classes.ObjetoFisico(150, 500, 100, 150, color.PIZZA_READY_COLOR)
rolo = classes.Rolo(50, 640, 100, 50, color.YELLOW)

# Fonte para texto
font = pygame.font.SysFont('Arial', 24)
semaphore_font = pygame.font.SysFont('Arial', 32, bold=True)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if massa.rect.collidepoint(pygame.mouse.get_pos()):
                states.movendoMassa = not states.movendoMassa
            elif rolo.rect.collidepoint(pygame.mouse.get_pos()):
                states.movendoRolo = not states.movendoRolo
            elif massa_aberta.rect.collidepoint(pygame.mouse.get_pos()):
                states.movendoMassaAberta = not states.movendoMassaAberta
            else:
                for cliente in clientes:
                    if cliente["rect"].collidepoint(pygame.mouse.get_pos()):
                        cliente_id = cliente["id"]
                        if clientes_estado[cliente_id] == "idle":
                            cliente_obj = classes.Cliente(
                            cliente_id,
                            cliente["rect"],
                            massa_aberta,
                            pizza_semaforo,
                            clientes_estado,
                            on_finish=cliente_finalizou
                        )
                        cliente_obj.start()


    # Movimento dos objetos
    if states.movendoMassa:
        massa.mover_para_mouse(pygame.mouse.get_pos(), mesa)
    
    if states.movendoMassaAberta:
        massa_aberta.mover_para_mouse(pygame.mouse.get_pos(), mesa)

    if states.movendoRolo:
        rolo.mover_para_mouse(pygame.mouse.get_pos(), mesa)
        states.mostrarMassa = rolo.abrir_massa(pygame.mouse.get_pos(), massa)

    # Física dos objetos
    topo_mesa = mesa.top + 150
    massa.aplicar_gravidade(topo_mesa)
    massa_aberta.aplicar_gravidade(topo_mesa)
    rolo.aplicar_gravidade(topo_mesa)
    
    # Verifica se a massa aberta foi entregue a algum cliente
    for cliente in clientes:
        if massa_aberta.rect.colliderect(cliente["rect"]) and clientes_estado.get(cliente["id"], "idle") == "esperando":
            clientes_estado[cliente["id"]] = "recebendo"
            states.pizza_pronta = False

    # Renderização
    screen.fill(color.WHITE)
    
    # Mesa
    pygame.draw.rect(screen, color.TABLE_COLOR, mesa)
    
    # Objetos
    if states.mostrarMassa:
        pygame.draw.rect(screen, color.DOUGH_COLOR, massa)
    else:
        pygame.draw.rect(screen, color.PIZZA_READY_COLOR if states.pizza_pronta else color.DOUGH_COLOR, massa_aberta)
    
    pygame.draw.rect(screen, color.ROLLER_COLOR, rolo)
    
    # Clientes
    for cliente in clientes:
        id_cliente = cliente["id"]
        rect = cliente["rect"]
        estado = clientes_estado.get(id_cliente, "idle")

        if estado == "comendo":
            cor = color.GREEN
        elif estado == "esperando":
            cor = color.YELLOW
        elif estado == "recebendo":
            cor = color.BLUE
        else:
            cor = color.BLACK

        pygame.draw.rect(screen, cor, rect)
        texto = font.render(f"Cliente {id_cliente}: {estado}", True, color.BLACK)
        screen.blit(texto, (rect.x, rect.y - 25))

    
    # Painel de informações do semáforo
    semaphore_value = pizza_semaforo._value
    semaphore_text = semaphore_font.render(f"SEMÁFORO: {semaphore_value}", True, 
                                         color.GREEN if semaphore_value > 0 else color.RED)
    screen.blit(semaphore_text, (50, 50))
    
    # Status da pizza
    pizza_status = "PRONTA" if states.pizza_pronta else "EM PREPARO"
    status_text = font.render(f"Pizza: {pizza_status}", True, color.BLACK)
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
        text = font.render(instruction, True, color.BLACK)
        screen.blit(text, (50, 130 + idx * 30))
    
    pygame.display.flip()

pygame.quit()