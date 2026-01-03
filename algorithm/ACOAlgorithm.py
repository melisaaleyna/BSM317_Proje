import random
from algorithm.AlgorithmUtils import AlgorithmUtils

class ACOAlgorithm:
    def __init__(self, graph_obj, w1, w2, w3):
        self.graph = graph_obj
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.pheromone = {}
        # Feromonları Link nesneleri üzerinden değil ID tuple üzerinden tutuyoruz
        for link in self.graph.links:
            edge = tuple(sorted((link.source.id, link.target.id)))
            self.pheromone[edge] = 1.0

    def solve(self, S, D, ant_count=25, iterations=25):
        G = self.graph.nx_graph
        
        def fitness(path):
            d, r, b = AlgorithmUtils.calculate_metrics(self.graph, path)
            return self.w1*d + self.w2*r + self.w3*b

        def choose_next_node(current, visited):
            neighbors = [n for n in G.neighbors(current) if n not in visited]
            if not neighbors: return None
            weights = []
            for n in neighbors:
                edge = tuple(sorted((current, n)))
                tau = self.pheromone.get(edge, 1.0)
                d_val = G.edges[current, n]["delay"]
                eta = 1 / d_val if d_val > 0 else 10
                weights.append(tau * (eta ** 2))
            
            total = sum(weights)
            if total == 0: return random.choice(neighbors)
            return random.choices(neighbors, weights=[w/total for w in weights])[0]

        best_path = None
        best_cost = float("inf")

        for _ in range(iterations):
            paths = []
            for _ in range(ant_count):
                curr, visited, path = S, {S}, [S]
                while curr != D:
                    nxt = choose_next_node(curr, visited)
                    if nxt is None: break
                    path.append(nxt)
                    visited.add(nxt)
                    curr = nxt
                if path[-1] == D:
                    fixed = AlgorithmUtils.fix_path(self.graph, path)
                    if fixed: paths.append(fixed)
            
            # Buharlaşma
            for key in self.pheromone:
                self.pheromone[key] *= 0.8
            
            # Güncelleme
            for p in paths:
                c = fitness(p)
                for i in range(len(p)-1):
                    edge = tuple(sorted((p[i], p[i+1])))
                    if edge in self.pheromone:
                        self.pheromone[edge] += 1 / (c + 0.0001)
                
                if c < best_cost:
                    best_cost = c
                    best_path = p
                    
        return best_path