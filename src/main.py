import pygame
import threading
import random
import classes
from config import color, states, values

def cliente_finalizou(id_cliente, resultado, tempo_espera):
    global clientes, clientes_estado, bonus

    if resultado == "acerto":
        values.score += values.score_win
        if tempo_espera < 5:
            values.bonus = int(values.extra_time * (5 - tempo_espera))
            values.score += values.bonus
    elif resultado == "erro":
        values.score += values.score_loss

    # Remove o cliente com esse ID
    clientes = [c for c in clientes if c["id"] != id_cliente]
    clientes_estado.pop(id_cliente, None)

    # Reposiciona os clientes restantes
    for i, cliente in enumerate(clientes):
        cliente["id"] = i + 1
        cliente["rect"].x = cliente1_x + i * (values.largura_cliente + values.espaco_entre_clientes)

    # Atualiza os estados com os novos IDs
    novos_estados = {}
    for i, cliente in enumerate(clientes):
        novos_estados[cliente["id"]] = clientes_estado.get(cliente["id"], "idle")
    clientes_estado.clear()
    clientes_estado.update(novos_estados)


pygame.init()
WIDTH, HEIGHT = 1250, 900       #Tamanho tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))

from config import images
# Semaforo e threads
pizza_semaforo = threading.Semaphore(1)

# Sabores disponíveis
SABORES = ["calabresa", "marquerita", "cogumelo"]
CORES_SABORES = {
    "calabresa": color.CALABRESA_COLOR,
    "marquerita": color.QUEIJO_COLOR,
    "cogumelo": color.PALMITO_COLOR
}

# Inicialização dos clientes
cliente_y = HEIGHT - values.altura_mesa - values.altura_cliente
cliente1_x = 800

clientes = []
cliente_threads = []
num_clientes = 10
clientes_estado = {}

for i in range(num_clientes):
    id_cliente = i + 1
    x = cliente1_x + i * (values.largura_cliente + values.espaco_entre_clientes)
    rect = pygame.Rect(x, cliente_y, values.largura_cliente, values.altura_cliente)
    sabor_desejado = random.choice(SABORES)
    clientes_estado[id_cliente] = "idle"
    clientes.append({"id": id_cliente, "rect": rect, "sabor_desejado": sabor_desejado, "image": images.cliente_imgs})

# Objetos da cena
fundo = images.fundo.get_rect()
mesa = pygame.Rect(0, HEIGHT - values.altura_mesa, WIDTH, values.altura_mesa)
massa = classes.ObjetoFisico(50, 790, 100, 100, color.DOUGH_COLOR)
massa_aberta = classes.ObjetoFisico(50, 740, 200, 200, color.PIZZA_READY_COLOR)
massa_aberta.sabor = None  # Inicialmente sem sabor
rolo = classes.Rolo(50, 680, 200, 100, color.YELLOW)

# Ingredientes
ingredientes = [
    classes.Ingrediente(1100, 680, 100, 100, color.CALABRESA_COLOR, "calabresa"),
    classes.Ingrediente(1100, 750, 100, 100, color.QUEIJO_COLOR, "marquerita"),
    classes.Ingrediente(1100, 820, 100, 100, color.PALMITO_COLOR, "cogumelo")
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
    screen.blit(images.fundo, (0,0))
    
    # Objetos
    if states.mostrarMassa:
        screen.blit(images.massa, massa.rect)
    else:
        if massa_aberta.sabor == "calabresa":
            screen.blit(images.pizza_calabresa, massa_aberta.rect)
        elif massa_aberta.sabor == "marquerita":
            screen.blit(images.pizza_marquerita, massa_aberta.rect)
        elif massa_aberta.sabor == "cogumelo":
            screen.blit(images.pizza_cogumelo, massa_aberta.rect)
        else:    
            screen.blit(images.massa_aberta, massa_aberta.rect)
    
    screen.blit(images.rolo, rolo.rect)
    
    # Ingredientes
    for ingrediente in ingredientes:
        screen.blit(images.pote_imgs[ingrediente.sabor], ingrediente.rect)
    
    # Clientes
    for cliente in clientes:
        id_cliente = cliente["id"]
        rect = cliente["rect"]
        estado = clientes_estado.get(id_cliente, "idle")
        sabor_desejado = cliente["sabor_desejado"]

        screen.blit(images.cliente_imgs[estado], rect)

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

        
        # Indicador visual do sabor dentro do cliente
        cor_sabor = CORES_SABORES[sabor_desejado]
        
        # Textos informativos
        texto_id = font.render(f"Cliente {id_cliente}", True, color.BLACK)
        texto_estado = font.render(f"{estado}", True, color.BLACK)
        texto_score = font.render(f"Pontuação: {values.score}", True, color.BLACK)
        texto_score_loss = font.render("-50", True, color.RED)
        texto_score_win = font.render(f"+{values.score_win + values.bonus}", True, color.GREEN)

        # Posiciona os textos acima do cliente
        screen.blit(texto_id, (rect.x, rect.y - 75))
        screen.blit(texto_estado, (rect.x, rect.y - 50))
        
        #Mensagem de pontuação
        if estado == "comendo":
            screen.blit(texto_score_win, (rect.x, rect.y - 100))
        if estado == "erro":
            texto_erro = font.render("Sabor errado!", True, color.RED)
            screen.blit(texto_erro, (rect.x, rect.y - 100))
            screen.blit(texto_score_loss, (rect.x, rect.y - 125))

        if estado == "esperando":
            texto_sabor = font.render(f"Sabor: {sabor_desejado}", True, cor_sabor)
            screen.blit(texto_sabor, (rect.x, rect.y - 25))
        
    screen.blit(texto_score, (1000 , 25))

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
    
    
    pygame.display.flip()

pygame.quit()