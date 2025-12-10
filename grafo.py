class Sala:
    """Representa um vértice(sala) no grafo"""
    def __init__(self,id,x,y):
        self.id = id
        self.x = x
        self.y = y
        self.neighbor = [] #salas adjacentes
        self.visited = False
        self.has_treasure = False
        self.is_exit = False

    def add_neighbor(self,sala_id):
        if sala_id not in self.neighbor:
            self.neighbor.append(sala_id)
    
class Grafo:
    def __init__(self):
        self.salas = {}

    def add_room(self, sala_id, x, y):
        self.salas[sala_id] = Sala(sala_id, x, y)
        
    def get_neighbors(self, sala_id):
        return self.salas[sala_id].neighbor
    
    def add_edge(self,a,b):
        self.salas[a].add_neighbor(b)
        self.salas[b].add_neighbor(a)

# Cria uma instância global do grafo
grafo = Grafo()