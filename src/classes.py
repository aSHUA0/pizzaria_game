import pygame
import threading
import time
import random

class Cliente(threading.Thread):
    def __init__(self, id_cliente, rect, massa_aberta, pizza_semaforo, clientes_estado, on_finish, sabor_desejado):
        super().__init__()
        self.id = id_cliente
        self.rect = rect
        self.massa_aberta = massa_aberta
        self.pizza_semaforo = pizza_semaforo
        self.clientes_estado = clientes_estado
        self.running = True
        self.on_finish = on_finish
        self.sabor_desejado = sabor_desejado
        self.sabor_recebido = None
        self.tempo_inicio = time.time()

    def run(self):
        self.clientes_estado[self.id] = "esperando"

        while not self.detecta_pizza():
            time.sleep(1)
            if not self.running:
                return
            
        tempo_espera = time.time() - self.tempo_inicio
        resultado = "acerto" if self.sabor_recebido == self.sabor_desejado else "erro"

        self.pizza_semaforo.acquire()
        self.clientes_estado[self.id] = "comendo" if self.sabor_recebido == self.sabor_desejado else "erro"
        time.sleep(2)
        self.clientes_estado[self.id] = "idle"
        self.pizza_semaforo.release()

        if self.on_finish:
            self.on_finish(self.id, resultado, tempo_espera)

    def detecta_pizza(self):
        if self.massa_aberta.rect.colliderect(self.rect):
            self.sabor_recebido = self.massa_aberta.sabor
            return True
        return False
    
class ObjetoFisico:
    def __init__(self, x, y, largura, altura, cor, gravidade=0.01):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.vel_queda = 0
        self.caindo = False
        self.gravidade = gravidade
        self.cor = cor

    def aplicar_gravidade(self, chao):
        if self.caindo:
            self.vel_queda += self.gravidade
            self.rect.y += self.vel_queda
            if self.rect.bottom >= chao:
                self.rect.bottom = chao
                self.caindo = False
                self.vel_queda = 0

    def mover_para_mouse(self, mouse_pos, limite):
        if not limite.collidepoint(mouse_pos):
            self.caindo = True
            self.vel_queda = 0
        self.rect.center = mouse_pos

class Rolo(ObjetoFisico):
    def __init__(self, x, y, largura, altura, cor):
        super().__init__(x, y, largura, altura, cor, gravidade=0.01)
        self.massa_aberta = False

    def abrir_massa(self, mouse_pos, massa):
        self.rect.center = mouse_pos
        
        if self.massa_aberta:
            return False
            
        if pygame.mouse.get_pressed()[0] and self.rect.colliderect(massa.rect):
            self.massa_aberta = True
            return False
            
        return True

class Ingrediente(ObjetoFisico):
    def __init__(self, x, y, largura, altura, cor, sabor):
        super().__init__(x, y, largura, altura, cor, gravidade=0.01)
        self.sabor = sabor