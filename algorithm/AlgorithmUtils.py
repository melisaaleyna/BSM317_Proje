import networkx as nx
import math
import random

class AlgorithmUtils:

    @staticmethod
    def fix_path(graph_obj, node_id_list):
        """
        EKSİK OLAN PARÇA BU:
        Genetik algoritma yolları böldüğünde arada boşluk kalırsa,
        bu fonksiyon iki nokta arasını 'en kısa yol' ile doldurur.
        """
        G = graph_obj.nx_graph
        final_path = []
        for i in range(len(node_id_list) - 1):
            u, v = node_id_list[i], node_id_list[i + 1]
            try:
                # Bağlantı yoksa veya kopuksa
                if not nx.has_path(G, u, v):
                    return None
                # Aradaki boşluğu doldur
                p = nx.shortest_path(G, u, v, weight="delay")
            except nx.NetworkXNoPath:
                return None
            
            if i == 0:
                final_path.extend(p)
            else:
                # Önceki parçanın sonu ile yenisinin başı aynı olmasın diye
                final_path.extend(p[1:])
        return final_path

    @staticmethod
    def create_a_path(graph_obj, src, dst):
        """
        Genetik Algoritma için başlangıç popülasyonu üretir.
        Körlemesine değil, akıllı rastgelelik kullanır.
        """
        G = graph_obj.nx_graph
        try:
            # %70 İhtimalle çeşitlilik kat (Ara durak seç)
            if random.random() < 0.7:
                nodes = list(G.nodes())
                # 10 kere dene, uygun bir ara düğüm bul
                for _ in range(10):
                    mid_node = random.choice(nodes)
                    if mid_node != src and mid_node != dst:
                        if nx.has_path(G, src, mid_node) and nx.has_path(G, mid_node, dst):
                            p1 = nx.shortest_path(G, src, mid_node, weight="delay")
                            p2 = nx.shortest_path(G, mid_node, dst, weight="delay")
                            return p1[:-1] + p2 

            # %30 İhtimalle veya başarısız olursa direkt en kısayı ver
            if nx.has_path(G, src, dst):
                weight_type = "bandwidth" if random.random() < 0.3 else "delay"
                return nx.shortest_path(G, src, dst, weight=weight_type)
                
        except Exception:
            return None
        return None

    @staticmethod
    def calculate_metrics(graph_obj, path_ids):
        """
        PDF Madde 3: Metrik Hesaplamaları
        """
        if not path_ids: return float('inf'), float('inf'), float('inf')

        G = graph_obj.nx_graph
        total_delay = 0
        reliability_cost = 0.0 
        bandwidth_cost = 0.0

        # 1. Kenarlar (Links)
        for i in range(len(path_ids) - 1):
            u, v = path_ids[i], path_ids[i + 1]
            
            if G.has_edge(u, v):
                data = G.edges[u, v]
                delay = data.get("delay", 0)
                bw = data.get("bandwidth", 100)
                rel = data.get("reliability", 0.99)
            else:
                 continue

            total_delay += delay
            reliability_cost += -math.log(rel + 1e-12)
            bandwidth_cost += (1000.0 / (bw + 1e-9))

        # 2. Ara Düğümler (S ve D hariç işlem süresi)
        if len(path_ids) > 2:
            intermediate_nodes = path_ids[1:-1]
            for node_id in intermediate_nodes:
                node = graph_obj.get_node(node_id)
                if node:
                    total_delay += getattr(node, 's_ms', 0)
                    reliability_cost += -math.log(getattr(node, 'reliability', 0.99) + 1e-12)
        
        # Uç Düğümlerin Güvenilirliği
        start_node = graph_obj.get_node(path_ids[0])
        end_node = graph_obj.get_node(path_ids[-1])
        if start_node: reliability_cost += -math.log(getattr(start_node, 'reliability', 0.99) + 1e-12)
        if end_node: reliability_cost += -math.log(getattr(end_node, 'reliability', 0.99) + 1e-12)

        return total_delay, reliability_cost, bandwidth_cost

    @staticmethod
    def get_bandwidth(graph_obj, path_ids):
        if not path_ids: return "0"
        path_bw = []    
        for i in range(len(path_ids) - 1):
             bw = AlgorithmUtils.get_link_a_to_b(graph_obj, path_ids[i], path_ids[i + 1])
             path_bw.append(f"{bw:.1f}")
        return f"Path BWs: {path_bw}"

    @staticmethod
    def get_required_bandwidth(graph_obj, path_ids):
        if not path_ids: return 0
        
        source_id = str(path_ids[0]).strip()
        target_id = str(path_ids[-1]).strip()
        
        required_bw = 0
        key = source_id + target_id
        
        if hasattr(graph_obj, 'demands') and key in graph_obj.demands:
            required_bw = graph_obj.demands[key]
            
        return f"Required BW: {required_bw}"

    @staticmethod
    def get_link_a_to_b(graph_obj, a_node, b_node): 
        for link in graph_obj.links: 
            if ((link.source.id == a_node and link.target.id == b_node) or 
                (link.source.id == b_node and link.target.id == a_node)): 
                return link.bandwidth
        return 1.0