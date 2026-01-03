import networkx as nx
import random
from model.Node import Node
from model.Link import Link
from model.NetworkGraph import NetworkGraph

class TopologyGenerator:
    def generate(self, num_nodes=250, prob=0.4):
        graph = NetworkGraph()
        
        # NetworkX kullanarak rastgele topoloji iskeleti oluştur
        # Erdős-Rényi modeli (PDF Madde 2.1)
        G_temp = nx.erdos_renyi_graph(num_nodes, prob, seed=42)

        # Node'ları Model'e aktar
        for n_id in G_temp.nodes():
            # PDF Madde 2.2: Node Reliability [0.95 - 0.999]
            rel = random.uniform(0.95, 0.999)
            # PDF Madde 2.2: Processing Delay [0.5 ms - 2.0 ms]
            s_ms = random.uniform(0.5, 2.0)
            
            node = Node(n_id, reliability=rel, s_ms=s_ms)
            
            # Görselleştirme için rastgele koordinat
            node.x = random.uniform(10, 100)
            node.y = random.uniform(10, 100)
            graph.add_node(node)

        # Link'leri Model'e aktar
        for u, v in G_temp.edges():
            src = graph.get_node(u)
            dst = graph.get_node(v)
            
            # PDF Madde 2.3: Link Delay [3 ms - 15 ms]
            delay = random.uniform(3, 15)
            # PDF Madde 2.3: Bandwidth [100 Mbps - 1000 Mbps]
            bw = random.uniform(100, 1000)
            # PDF Madde 2.3: Link Reliability [0.95 - 0.999]
            rel = random.uniform(0.95, 0.999)

            link = Link(src, dst, delay, bw, rel)
            graph.add_link(link)
            
        return graph