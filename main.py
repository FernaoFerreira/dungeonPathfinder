import pygame
import os

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

running = True
# Tenta encontrar a imagem no diretório atual
img_path = 'G1ToJVWWwAAAZIU.jpg'
if not os.path.exists(img_path):
    print(f"Erro: Arquivo '{img_path}' não encontrado em {os.getcwd()}")
    print(f"Arquivos no diretório: {os.listdir('.')}")
else:
    potato_img = pygame.image.load(img_path).convert()
    potato_img = pygame.transform.scale(potato_img, (100, 100))  # Ajuste para o tamanho desejado

x = 0
while running:
    screen.fill((0, 0, 0))  # Limpa a tela com fundo preto
    screen.blit(potato_img, (x, 30))
    
    x += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.flip()
    clock.tick(75)  # 60 FPS

pygame.quit()