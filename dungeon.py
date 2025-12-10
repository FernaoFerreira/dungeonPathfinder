"""
DUNGEON PATHFINDER - Protótipo Completo
Jogo educacional de grafos com BFS, DFS e Dijkstra

COMO JOGAR:
- Clique nas salas VIZINHAS para se mover
- Colete tesouros (estrelas amarelas)
- Pressione M para ativar o mapa mágico (mostra caminho BFS)
- Fuja do inimigo vermelho (usa DFS)
- Chegue na sala de saída (dourada) para vencer
- ESC para sair

CONCEITOS IMPLEMENTADOS:
- Grafo com lista de adjacências
- BFS (sistema de mapa)
- DFS (IA do inimigo)
- Dijkstra (preparado para custos)
"""

import pygame
import sys
from collections import deque
import random
import math

# ==================== CONFIGURAÇÕES ====================
LARGURA_TELA = 1280
ALTURA_TELA = 720
FPS = 60

# Cores
COR_FUNDO = (20, 20, 30)
COR_SALA = (200, 200, 200)
COR_SALA_ATUAL = (100, 255, 100)
COR_SALA_VISITADA = (100, 100, 100)
COR_CORREDOR = (150, 150, 150)
COR_SAIDA = (255, 215, 0)
COR_CAMINHO_BFS = (255, 165, 0)
COR_INIMIGO = (255, 50, 50)
COR_TESOURO = (255, 215, 0)

# Grafo
RAIO_SALA = 35
ESPESSURA_CORREDOR = 4


# ==================== CLASSES DE GRAFO ====================
class Sala:
    """Representa um vértice (sala) no grafo"""
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vizinhos = []
        self.visitada = False
        self.tem_tesouro = False
        self.e_saida = False
        self.custo = 1  # Para Dijkstra futuro
    
    def adicionar_vizinho(self, sala_id):
        if sala_id not in self.vizinhos:
            self.vizinhos.append(sala_id)


class Grafo:
    """Grafo não-direcionado representando a dungeon"""
    def __init__(self):
        self.salas = {}
    
    def adicionar_sala(self, id, x, y):
        self.salas[id] = Sala(id, x, y)
    
    def adicionar_corredor(self, sala1_id, sala2_id):
        if sala1_id in self.salas and sala2_id in self.salas:
            self.salas[sala1_id].adicionar_vizinho(sala2_id)
            self.salas[sala2_id].adicionar_vizinho(sala1_id)
    
    def obter_vizinhos(self, sala_id):
        if sala_id in self.salas:
            return self.salas[sala_id].vizinhos
        return []
    
    def obter_sala(self, sala_id):
        return self.salas.get(sala_id)


# ==================== ALGORITMOS ====================
def bfs(grafo, inicio, destino):
    """
    Busca em Largura - encontra caminho mais curto
    Retorna: lista de IDs do caminho ou None
    """
    if inicio == destino:
        return [inicio]
    
    fila = deque([inicio])
    visitados = {inicio}
    pais = {inicio: None}
    
    while fila:
        atual = fila.popleft()
        
        if atual == destino:
            # Reconstruir caminho
            caminho = []
            while atual is not None:
                caminho.insert(0, atual)
                atual = pais[atual]
            return caminho
        
        for vizinho in grafo.obter_vizinhos(atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                pais[vizinho] = atual
                fila.append(vizinho)
    
    return None


def dfs(grafo, inicio, destino):
    """
    Busca em Profundidade - encontra UM caminho (não necessariamente o mais curto)
    Retorna: lista de IDs do caminho ou None
    """
    if inicio == destino:
        return [inicio]
    
    pilha = [inicio]
    visitados = set()
    pais = {inicio: None}
    
    while pilha:
        atual = pilha.pop()
        
        if atual not in visitados:
            visitados.add(atual)
            
            if atual == destino:
                # Reconstruir caminho
                caminho = []
                while atual is not None:
                    caminho.insert(0, atual)
                    atual = pais[atual]
                return caminho
            
            # Adiciona vizinhos na pilha (ordem reversa para visitação mais natural)
            vizinhos = grafo.obter_vizinhos(atual)
            random.shuffle(vizinhos)  # Aleatoriedade para comportamento menos previsível
            for vizinho in vizinhos:
                if vizinho not in visitados:
                    pais[vizinho] = atual
                    pilha.append(vizinho)
    
    return None


# ==================== ENTIDADES ====================
class Jogador:
    """Jogador controlado pelo usuário"""
    def __init__(self, sala_inicial):
        self.sala_atual = sala_inicial
        self.pontuacao = 0
    
    def mover_para(self, sala_id, grafo):
        """Move o jogador para uma sala vizinha"""
        if sala_id in grafo.obter_vizinhos(self.sala_atual):
            self.sala_atual = sala_id
            sala = grafo.obter_sala(sala_id)
            sala.visitada = True
            
            # Coletar tesouro
            if sala.tem_tesouro:
                self.pontuacao += 10
                sala.tem_tesouro = False
            
            return True
        return False


class Inimigo:
    """Inimigo que persegue o jogador usando DFS"""
    def __init__(self, sala_inicial):
        self.sala_atual = sala_inicial
        self.caminho = []
        self.tempo_recalculo = 0
        self.intervalo_recalculo = 1.0  # segundos
        self.velocidade = 0.5  # salas por segundo

        self.tempo_movimento = 0 #guarda tempo acumulado
    
    def atualizar(self, dt, grafo, jogador):
        """Atualiza IA do inimigo"""
        self.tempo_recalculo += dt
        self.tempo_movimento += dt

        tempo_por_sala = 1/self.velocidade
        
        # Recalcular caminho periodicamente
        if self.tempo_recalculo >= self.intervalo_recalculo:
            self.caminho = dfs(grafo, self.sala_atual, jogador.sala_atual)
            if self.caminho and len(self.caminho) > 1:
                self.caminho.pop(0)  # Remove posição atual
            self.tempo_recalculo = 0
        
        # Mover para próxima sala do caminho
        if self.tempo_movimento >= tempo_por_sala and len(self.caminho) > 1:
            self.sala_atual = self.caminho.pop(0)
            self.tempo_movimento = 0
        


class SistemaMapa:
    """Sistema de mapa mágico que mostra caminho BFS"""
    def __init__(self):
        self.ativo = False
        self.caminho = []
    
    def ativar(self, grafo, sala_origem, sala_destino):
        self.ativo = True
        self.caminho = bfs(grafo, sala_origem, sala_destino)
    
    def desativar(self):
        self.ativo = False
        self.caminho = []


# ==================== GERAÇÃO DE DUNGEON ====================
def gerar_dungeon_exemplo():
    """Gera um grafo de exemplo para teste"""
    grafo = Grafo()
    
    # Layout em grid 4x3
    posicoes = [
        (200, 150), (400, 150), (600, 150), (800, 150),
        (200, 350), (400, 350), (600, 350), (800, 350),
        (200, 550), (400, 550), (600, 550), (800, 550)
    ]
    
    # Adicionar salas
    for i, (x, y) in enumerate(posicoes):
        grafo.adicionar_sala(i, x, y)
    
    # Conectar salas (criar grafo interessante)
    conexoes = [
        (0, 1), (1, 2), (2, 3),  # Linha superior
        (4, 5), (5, 6), (6, 7),  # Linha do meio
        (8, 9), (9, 10), (10, 11),  # Linha inferior
        (0, 4), (1, 5), (2, 6), (3, 7),  # Verticais
        (4, 8), (5, 9), (6, 10), (7, 11),  # Verticais
        (1, 4), (2, 5), (6, 9), (7, 10),  # Diagonais
    ]
    
    for s1, s2 in conexoes:
        grafo.adicionar_corredor(s1, s2)
    
    # Marcar saída (canto inferior direito)
    grafo.obter_sala(11).e_saida = True
    
    # Adicionar tesouros aleatórios
    tesouros = random.sample(range(1, 11), 4)  # 4 tesouros aleatórios
    for t in tesouros:
        grafo.obter_sala(t).tem_tesouro = True
    
    return grafo


# ==================== RENDERIZAÇÃO ====================
def desenhar_grafo(surface, grafo, jogador, inimigo, sistema_mapa):
    """Desenha o grafo completo na tela"""
    
    # 1. Desenhar corredores (arestas)
    for sala_id, sala in grafo.salas.items():
        for vizinho_id in sala.vizinhos:
            if sala_id < vizinho_id:  # Desenha cada aresta uma vez
                vizinho = grafo.obter_sala(vizinho_id)
                
                cor = COR_CORREDOR
                espessura = ESPESSURA_CORREDOR
                
                # Destacar caminho BFS se mapa ativo
                if sistema_mapa.ativo and sistema_mapa.caminho:
                    if (sala_id in sistema_mapa.caminho and 
                        vizinho_id in sistema_mapa.caminho and
                        abs(sistema_mapa.caminho.index(sala_id) - 
                            sistema_mapa.caminho.index(vizinho_id)) == 1):
                        cor = COR_CAMINHO_BFS
                        espessura = ESPESSURA_CORREDOR + 2
                
                pygame.draw.line(surface, cor, (sala.x, sala.y), 
                               (vizinho.x, vizinho.y), espessura)
    
    # 2. Desenhar salas (vértices)
    for sala_id, sala in grafo.salas.items():
        cor = COR_SALA
        
        if sala.e_saida:
            cor = COR_SAIDA
        elif sala.visitada:
            cor = COR_SALA_VISITADA
        
        if sala_id == jogador.sala_atual:
            cor = COR_SALA_ATUAL
        
        # Círculo principal
        pygame.draw.circle(surface, cor, (sala.x, sala.y), RAIO_SALA)
        pygame.draw.circle(surface, (0, 0, 0), (sala.x, sala.y), RAIO_SALA, 2)
        
        # ID da sala (debug)
        font = pygame.font.Font(None, 20)
        texto = font.render(str(sala.id), True, (0, 0, 0))
        texto_rect = texto.get_rect(center=(sala.x, sala.y - 10))
        surface.blit(texto, texto_rect)
        
        # Tesouro
        if sala.tem_tesouro:
            desenhar_tesouro(surface, sala.x, sala.y)
    
    # 3. Desenhar inimigo
    sala_inimigo = grafo.obter_sala(inimigo.sala_atual)
    pygame.draw.circle(surface, COR_INIMIGO, 
                      (sala_inimigo.x, sala_inimigo.y), RAIO_SALA // 2)
    
    # 4. Desenhar jogador
    sala_jogador = grafo.obter_sala(jogador.sala_atual)
    pygame.draw.circle(surface, (50, 150, 255), 
                      (sala_jogador.x, sala_jogador.y), RAIO_SALA // 2)


def desenhar_tesouro(surface, x, y):
    """Desenha um tesouro (estrela)"""
    pontos = []
    for i in range(5):
        angulo = math.pi * 2 * i / 5 - math.pi / 2
        px = x + math.cos(angulo) * 12
        py = y + math.sin(angulo) * 12
        pontos.append((px, py))
        
        angulo_interno = math.pi * 2 * (i + 0.5) / 5 - math.pi / 2
        px = x + math.cos(angulo_interno) * 6
        py = y + math.sin(angulo_interno) * 6
        pontos.append((px, py))
    
    pygame.draw.polygon(surface, COR_TESOURO, pontos)


def desenhar_hud(surface, jogador, sistema_mapa):
    """Desenha interface (pontuação, instruções)"""
    font = pygame.font.Font(None, 36)
    font_pequena = pygame.font.Font(None, 24)
    
    # Pontuação
    texto_pontos = font.render(f"Pontos: {jogador.pontuacao}", True, (255, 255, 255))
    surface.blit(texto_pontos, (10, 10))
    
    # Status do mapa
    status_mapa = "Mapa: ATIVO (BFS)" if sistema_mapa.ativo else "Mapa: INATIVO"
    cor_mapa = COR_CAMINHO_BFS if sistema_mapa.ativo else (150, 150, 150)
    texto_mapa = font_pequena.render(status_mapa, True, cor_mapa)
    surface.blit(texto_mapa, (10, 50))
    
    # Instruções
    instrucoes = [
        "Clique nas salas vizinhas para mover",
        "M = Ativar Mapa Mágico (BFS)",
        "Fuja do círculo vermelho (DFS)",
        "Alcance a sala dourada para vencer!"
    ]
    
    y_offset = ALTURA_TELA - 120
    for i, texto in enumerate(instrucoes):
        render = font_pequena.render(texto, True, (200, 200, 200))
        surface.blit(render, (10, y_offset + i * 25))


def obter_sala_clicada(pos, grafo):
    """Retorna ID da sala clicada ou None"""
    x, y = pos
    for sala_id, sala in grafo.salas.items():
        dist = math.sqrt((sala.x - x)**2 + (sala.y - y)**2)
        if dist <= RAIO_SALA:
            return sala_id
    return None


# ==================== JOGO PRINCIPAL ====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Dungeon Pathfinder - Protótipo")
    clock = pygame.time.Clock()
    
    # Inicialização
    grafo = gerar_dungeon_exemplo()
    jogador = Jogador(0)
    inimigo = Inimigo(11)  # Começa no canto oposto
    sistema_mapa = SistemaMapa()
    
    grafo.obter_sala(0).visitada = True
    
    estado = "JOGANDO"  # JOGANDO, VITORIA, DERROTA
    
    # Game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time em segundos
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Ativar/desativar mapa com M
                elif event.key == pygame.K_m and estado == "JOGANDO":
                    if not sistema_mapa.ativo:
                        sala_saida = 11
                        sistema_mapa.ativar(grafo, jogador.sala_atual, sala_saida)
                    else:
                        sistema_mapa.desativar()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and estado == "JOGANDO":
                sala_clicada = obter_sala_clicada(event.pos, grafo)
                if sala_clicada is not None:
                    jogador.mover_para(sala_clicada, grafo)
        
        # Lógica do jogo
        if estado == "JOGANDO":
            # Atualizar inimigo
            inimigo.atualizar(dt, grafo, jogador)
            
            # Verificar captura
            if inimigo.sala_atual == jogador.sala_atual:
                estado = "DERROTA"
            
            # Verificar vitória
            sala_atual = grafo.obter_sala(jogador.sala_atual)
            if sala_atual.e_saida:
                estado = "VITORIA"
        
        # Renderização
        screen.fill(COR_FUNDO)
        
        if estado == "JOGANDO":
            desenhar_grafo(screen, grafo, jogador, inimigo, sistema_mapa)
            desenhar_hud(screen, jogador, sistema_mapa)
        
        elif estado == "VITORIA":
            font_grande = pygame.font.Font(None, 72)
            texto = font_grande.render("VITÓRIA!", True, (0, 255, 0))
            texto_rect = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2))
            screen.blit(texto, texto_rect)
            
            font = pygame.font.Font(None, 36)
            pontos = font.render(f"Pontuação Final: {jogador.pontuacao}", True, (255, 255, 255))
            pontos_rect = pontos.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 60))
            screen.blit(pontos, pontos_rect)
        
        elif estado == "DERROTA":
            font_grande = pygame.font.Font(None, 72)
            texto = font_grande.render("CAPTURADO!", True, (255, 0, 0))
            texto_rect = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2))
            screen.blit(texto, texto_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()