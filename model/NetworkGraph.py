import networkx as nx

class NetworkGraph:
    def __init__(self):
        self.nodes = {}  # id -> Node nesnesi
        self.links = []  # Link nesneleri listesi
        self.demands = {} # Key: "SourceID-TargetID", Value: Bandwidth
        
        # Hesaplamalar ve çizim için yardımcı NetworkX yapısı
        self.nx_graph = nx.Graph() 

    def add_node(self, node):
        self.nodes[node.id] = node
        self.nx_graph.add_node(node.id, reliability=node.reliability, s_ms=node.s_ms ,pos=(node.x, node.y))

    def add_link(self, link):
        self.links.append(link)
        # NetworkX grafiğine de ekle (Algoritmalar için)
        self.nx_graph.add_edge(
            link.source.id, 
            link.target.id, 
            delay=link.delay, 
            bandwidth=link.bandwidth, 
            reliability=link.reliability,
            object=link # Link nesnesine graph üzerinden erişmek için
        )

    def add_demands(self, demands_map):
        self.demands = demands_map

    def get_node(self, node_id):
        return self.nodes.get(int(node_id))
    
    def get_links(self):
        return self.links

    def get_demands(self):
        return self.demands