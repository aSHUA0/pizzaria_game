import pygame
import threading
import random
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

# Sabores disponíveis
SABORES = ["calabresa", "queijo", "palmito"]
CORES_SABORES = {
    "calabresa": color.CALABRESA_COLOR,
    "queijo": color.QUEIJO_COLOR,
    "palmito": color.PALMITO_COLOR
}

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
    sabor_desejado = random.choice(SABORES)
    clientes_estado[id_cliente] = "idle"
    clientes.append({"id": id_cliente, "rect": rect, "sabor_desejado": sabor_desejado})

# Objetos da cena
mesa = pygame.Rect(0, HEIGHT - altura_mesa, WIDTH, altura_mesa)
massa = classes.ObjetoFisico(50, 740, 100, 100, color.DOUGH_COLOR)
massa_aberta = classes.ObjetoFisico(150, 500, 100, 150, color.PIZZA_READY_COLOR)
massa_aberta.sabor = None  # Inicialmente sem sabor
rolo = classes.Rolo(50, 640, 100, 50, color.YELLOW)

# Ingredientes
ingredientes = [
    classes.Ingrediente(200, 740, 80, 30, color.CALABRESA_COLOR, "calabresa"),
    classes.Ingrediente(300, 740, 80, 30, color.QUEIJO_COLOR, "queijo"),
    classes.Ingrediente(400, 740, 80, 30, color.PALMITO_COLOR, "palmito")
]

# Fonte para texto
font = pygame.font.SysFont('Arial', 24)
semaphore_font = pygame.font.SysFont('Arial', 32, bold=True)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Verifica clique nos ingredientes
            for ingrediente in ingredientes:
                if ingrediente.rect.collidepoint(mouse_pos):
                    states.sabor_selecionado = ingrediente.sabor
                    states.movendo_ingrediente = True
            
            # Verifica clique na massa aberta para adicionar sabor
            if massa_aberta.rect.collidepoint(mouse_pos) and states.sabor_selecionado:
                massa_aberta.sabor = states.sabor_selecionado
                massa_aberta.cor = CORES_SABORES[states.sabor_selecionado]
                states.sabor_selecionado = None
                states.pizza_pronta = True
            
            if massa.rect.collidepoint(mouse_pos):
                states.movendoMassa = not states.movendoMassa
            elif rolo.rect.collidepoint(mouse_pos):
                states.movendoRolo = not states.movendoRolo
            elif massa_aberta.rect.collidepoint(mouse_pos):
                states.movendoMassaAberta = not states.movendoMassaAberta
            else:
                for cliente in clientes:
                    if cliente["rect"].collidepoint(mouse_pos):
                        cliente_id = cliente["id"]
                        if clientes_estado[cliente_id] == "idle":
                            cliente_obj = classes.Cliente(
                                cliente_id,
                                cliente["rect"],
                                massa_aberta,
                                pizza_semaforo,
                                clientes_estado,
                                on_finish=cliente_finalizou,
                                sabor_desejado=cliente["sabor_desejado"]
                            )
                            cliente_obj.start()

        if event.type == pygame.MOUSEBUTTONUP:
            states.movendo_ingrediente = False

    # Movimento dos objetos
    if states.movendoMassa:
        massa.mover_para_mouse(pygame.mouse.get_pos(), mesa)
    
    if states.movendoMassaAberta:
        massa_aberta.mover_para_mouse(pygame.mouse.get_pos(), mesa)

    if states.movendoRolo:
        rolo.mover_para_mouse(pygame.mouse.get_pos(), mesa)
        states.mostrarMassa = rolo.abrir_massa(pygame.mouse.get_pos(), massa)

    if states.movendo_ingrediente and states.sabor_selecionado:
        for ingrediente in ingredientes:
            if ingrediente.sabor == states.sabor_selecionado:
                ingrediente.mover_para_mouse(pygame.mouse.get_pos(), mesa)

    # Física dos objetos
    topo_mesa = mesa.top + 150
    massa.aplicar_gravidade(topo_mesa)
    massa_aberta.aplicar_gravidade(topo_mesa)
    rolo.aplicar_gravidade(topo_mesa)
    for ingrediente in ingredientes:
        ingrediente.aplicar_gravidade(topo_mesa)
    
    # Renderização
    screen.fill(color.WHITE)
    
    # Mesa
    pygame.draw.rect(screen, color.TABLE_COLOR, mesa)
    
    # Objetos
    if states.mostrarMassa:
        pygame.draw.rect(screen, color.DOUGH_COLOR, massa)
    else:
        pygame.draw.rect(screen, massa_aberta.cor, massa_aberta)
    
    pygame.draw.rect(screen, color.ROLLER_COLOR, rolo)
    
    # Ingredientes
    for ingrediente in ingredientes:
        pygame.draw.rect(screen, ingrediente.cor, ingrediente.rect)
        texto = font.render(ingrediente.sabor.capitalize(), True, color.BLACK)
        screen.blit(texto, (ingrediente.rect.x, ingrediente.rect.y - 25))
    
    # Clientes
    for cliente in clientes:
        id_cliente = cliente["id"]
        rect = cliente["rect"]
        estado = clientes_estado.get(id_cliente, "idle")
        sabor_desejado = cliente["sabor_desejado"]

        # Cor do cliente baseada no estado
        if estado == "comendo":
            cor = color.GREEN
        elif estado == "esperando":
            cor = color.YELLOW
        elif estado == "recebendo":
            cor = color.BLUE
        elif estado == "erro":
            cor = color.RED
        else:
            cor = color.BLACK

        pygame.draw.rect(screen, cor, rect)
        
        # Indicador visual do sabor dentro do cliente
        cor_sabor = CORES_SABORES[sabor_desejado]
        indicador_sabor = pygame.Rect(rect.x + 5, rect.y + 5, rect.width - 10, 15)
        pygame.draw.rect(screen, cor_sabor, indicador_sabor)
        
        # Textos informativos
        texto_id = font.render(f"Cliente {id_cliente}", True, color.BLACK)
        texto_estado = font.render(f"{estado}", True, color.BLACK)
        texto_sabor = font.render(f"Sabor: {sabor_desejado}", True, cor_sabor)
        
        # Posiciona os textos acima do cliente
        screen.blit(texto_id, (rect.x, rect.y - 75))
        screen.blit(texto_estado, (rect.x, rect.y - 50))
        screen.blit(texto_sabor, (rect.x, rect.y - 25))
        
        # Mensagem de erro se aplicável
        if estado == "erro":
            texto_erro = font.render("Sabor errado!", True, color.RED)
            screen.blit(texto_erro, (rect.x, rect.y - 100))
    
    # Sabor selecionado
    if states.sabor_selecionado:
        texto_sabor = font.render(f"Sabor selecionado: {states.sabor_selecionado}", True, color.BLACK)
        screen.blit(texto_sabor, (50, 300))
    
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
        "Clique em um ingrediente e depois na massa para adicionar sabor",
        "Leve a pizza pronta até o cliente para entregar",
        "Semaforo verde: recurso disponível",
        "Semaforo vermelho: recurso em uso",
        "Errar o sabor resulta em cliente insatisfeito!"
    ]
    
    for idx, instruction in enumerate(instructions):
        text = font.render(instruction, True, color.BLACK)
        screen.blit(text, (50, 130 + idx * 30))
    
    pygame.display.flip()

pygame.quit()