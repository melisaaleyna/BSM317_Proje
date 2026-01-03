import os
from model.Node import Node
from model.Link import Link
from model.NetworkGraph import NetworkGraph

class ReadData:
    def __init__(self):
        # Dosya yollarını buraya güncelleyin
       self.NODE_PATH = r"documents\BSM307_317_Guz2025_TermProject_NodeData.csv"
       self.LINK_PATH = r"documents\BSM307_317_Guz2025_TermProject_EdgeData.csv"
       self.DEMAND_PATH = r"documents\BSM307_317_Guz2025_TermProject_DemandData.csv"

    def read(self):
        graph = NetworkGraph()
        
        if not (os.path.exists(self.NODE_PATH) and os.path.exists(self.LINK_PATH)):
            raise FileNotFoundError("CSV dosyaları bulunamadı.")

        # --- NODES ---
        with open(self.NODE_PATH, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            for line in lines[1:]: # Başlığı atla
                if not line.strip(): continue
                
                vals = line.strip().split(';')
                # CSV formatına göre indexleri kontrol edin
                n_id = int(vals[0].strip())
                s_ms = float(vals[1].replace(",", "."))
                # X ve Y koordinatları CSV'de yoksa rastgele atanabilir veya 0 geçilir
                rel = float(vals[2].replace(",", ".")) if len(vals) > 2 else 0
                
                node = Node(n_id, reliability=rel,s_ms=s_ms)
                graph.add_node(node)

        # --- LINKS ---
        with open(self.LINK_PATH, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            for line in lines[1:]:
                if not line.strip(): continue
                vals = line.strip().split(';')
                
                src_id = int(vals[0])
                dst_id = int(vals[1])
                bw = float(vals[2].replace(",", "."))
                delay = float(vals[3].replace(",", "."))
                rel = float(vals[4].replace(",", "."))

                source_node = graph.get_node(src_id)
                target_node = graph.get_node(dst_id)

                if source_node and target_node:
                    total_delay = delay + source_node.s_ms
                    link = Link(source_node, target_node, total_delay, bw, rel)
                    graph.add_link(link)

        # --- DEMANDS ---
        if os.path.exists(self.DEMAND_PATH):
            demands = {}
            with open(self.DEMAND_PATH, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                for line in lines[1:]:
                    if not line.strip(): continue
                    vals = line.strip().split(';')
                    key = vals[0].strip() + vals[1].strip()
                    val = int(vals[2].strip())
                    demands[key] = val
            graph.add_demands(demands)

        return graph