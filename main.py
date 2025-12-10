import pygame
import os
from grafo import grafo




grafo.add_room(0, 100,100)
grafo.add_room(1,200,100)
grafo.add_room(2,300,200)
grafo.add_room(3,400,300)
grafo.add_room(4,500,400)
grafo.add_room(5,600,500)
grafo.add_edge(0,1)
grafo.add_edge(0,2)
grafo.add_edge(1,2)
grafo.add_edge(2,3)
grafo.add_edge(2,5)
grafo.add_edge(2,3)
grafo.add_edge(3,4)
grafo.add_edge(4,5)

#DEBUG
print("Mapa do grafo: ")
for sala_id, sala in grafo.salas.items():
    print(sala_id, "->", sala.neighbor)


pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

running = True

x = 0
while running:
    screen.fill((0, 0, 0))  # Limpa a tela com fundo preto
    
    x += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
 
    clock.tick(75)  # 60 FPS

pygame.quit()