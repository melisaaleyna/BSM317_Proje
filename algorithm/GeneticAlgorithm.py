import random
import numpy as np
from algorithm.AlgorithmUtils import AlgorithmUtils


class GeneticAlgorithm:
    def __init__(self, graph_obj, w1, w2, w3):
        self.graph = graph_obj
        self.w1 = w1  # Delay
        self.w2 = w2  # Reliability
        self.w3 = w3  # Bandwidth


    def fitness_function(self, path):

        if not path: return float('inf')
        # AlgorithmUtils.calculate_metrics hata fırlatmaması için yolun geçerliliğini kontrol eder
        d, r_cost, b_cost = AlgorithmUtils.calculate_metrics(self.graph, path)

        # Eğer yolda kopukluk varsa (calculate_metrics içindeki kontrolden döner)
        # yüksek maliyet vererek elenmesini sağlarız
        return (self.w1 * d) + (self.w2 * r_cost) + (self.w3 * b_cost)

    def crossover(self, parent, S, D):
        
        if len(parent) < 3: return parent.copy()

        mid_idx = len(parent) // 2
        mid_node = parent[mid_idx]

        if random.random() < 0.5:
            # Başı sabit tut, mid_node'dan hedefe yeni yol bul
            new_tail = AlgorithmUtils.create_a_path(self.graph,mid_node, D)
            if new_tail:
                # parent[:mid_idx] (0'dan mid-1'e kadar) + new_tail (mid'den D'ye kadar)
                return parent[:mid_idx] + new_tail
        else:
            # Sonu sabit tut, kaynaktan mid_node'a yeni yol bul
            new_head = AlgorithmUtils.create_a_path(self.graph,S, mid_node)
            if new_head:
                # new_head (S'den mid'e kadar) + parent[mid_idx+1:] (mid+1'den sona kadar)
                return new_head + parent[mid_idx + 1:]

        return parent.copy()

    def mutate(self, parent):

        if len(parent) <= 3: return parent

        child = parent.copy()
        idx = random.randint(1, len(child) - 2)

        # Seçilen rastgele bir noktadan hedefe yeni bir rota çiz
        new_segment = AlgorithmUtils.create_a_path(self.graph,child[idx], child[-1])
        if new_segment:
            return child[:idx] + new_segment
        return child

    def solve(self, S, D, pop_size=100, generations=100):
        # 1. Başlangıç Popülasyonu 
        population = []
        for _ in range(pop_size): 
            p = AlgorithmUtils.create_a_path(self.graph,S, D)
            if p and p not in population:
                population.append(p)
            if len(population) >= pop_size: break

        if not population: return None

        best_path = None
        best_fitness = float('inf')

        for gen in range(generations):
            # Fitness skorlarını hesapla
            scores = [self.fitness_function(p) for p in population]

            # En iyiyi güncelle
            min_idx = np.argmin(scores)
            if scores[min_idx] < best_fitness:
                best_fitness = scores[min_idx]
                best_path = population[min_idx]

            # Yeni nesil (Elitizm %10)
            new_pop = []
            elites = np.argsort(scores)[:max(1, int(pop_size * 0.1))]
            for e in elites:
                new_pop.append(population[e])

            while len(new_pop) < pop_size:
                # Tournament Selection
                idx1, idx2 = random.sample(range(len(population)), 2)
                p1 = population[idx1] if scores[idx1] < scores[idx2] else population[idx2]

                # Crossover & Mutation
                child = self.crossover(p1, S, D) if random.random() < 0.8 else p1.copy()
                child = self.mutate(child) if random.random() < 0.3 else child

                new_pop.append(child)

            population = new_pop

        return best_path