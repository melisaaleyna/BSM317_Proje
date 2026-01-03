from flask import Flask, render_template, request, jsonify
import networkx as nx
import math
import os
import time  # <--- EKLENDİ (Süre hesabı için)

# --- Senin Proje Dosyaların ---
from generate.TopologyGenerator import TopologyGenerator
from generate.ReadData import ReadData
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.ACOAlgorithm import ACOAlgorithm
from algorithm.AlgorithmUtils import AlgorithmUtils

app = Flask(__name__)

# Global değişken
network_graph = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_network():
    global network_graph
    try:
        data = request.json
        source_type = data.get('type', 'random')
        
        if source_type == 'csv':
            csv_path = os.path.join(BASE_DIR, "documents", "BSM307_317_Guz2025_TermProject_EdgeData.csv")
            if not os.path.exists(csv_path):
                return jsonify({'success': False, 'message': "CSV Dosyası Bulunamadı!"})
            
            original_cwd = os.getcwd()
            try:
                os.chdir(BASE_DIR)
                reader = ReadData()
                network_graph = reader.read()
            finally:
                os.chdir(original_cwd)
            
            pos = nx.spring_layout(network_graph.nx_graph, seed=42)
            msg = "CSV Verileri Yüklendi."

        else:
            gen = TopologyGenerator()
            for _ in range(10):
                network_graph = gen.generate(num_nodes=250)
                if nx.is_connected(network_graph.nx_graph):
                    break
            else:
                G = network_graph.nx_graph
                comps = list(nx.connected_components(G))
                for i in range(len(comps)-1):
                    G.add_edge(list(comps[i])[0], list(comps[i+1])[0], bandwidth=500, delay=5, reliability=0.99)
            
            pos = nx.spring_layout(network_graph.nx_graph, k=0.15, iterations=50, seed=42)
            msg = "Rastgele Topoloji Oluşturuldu (250 Node)."

        nodes = []
        for n in network_graph.nx_graph.nodes():
            node_obj = network_graph.get_node(n)
            title = f"Node: {n}\nProc: {getattr(node_obj, 's_ms', 0):.2f}ms\nRel: {getattr(node_obj, 'reliability', 0):.4f}"
            x_pos = pos[n][0] * 2500 
            y_pos = pos[n][1] * 2500
            nodes.append({'id': int(n), 'label': str(n), 'title': title, 'group': 'router', 'x': x_pos, 'y': y_pos})

        edges = []
        for u, v, data in network_graph.nx_graph.edges(data=True):
            title = f"BW: {data.get('bandwidth',0):.1f} Mbps\nDelay: {data.get('delay',0):.1f}ms"
            edges.append({'from': int(u), 'to': int(v), 'title': title})

        return jsonify({'success': True, 'message': msg, 'data': {'nodes': nodes, 'edges': edges}})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/solve', methods=['POST'])
def solve_path():
    global network_graph
    if not network_graph:
        return jsonify({'success': False, 'message': "Önce ağı oluşturun!"})

    try:
        data = request.json
        S = int(data['s'])
        D = int(data['d'])
        w1, w2, w3 = float(data['w1']), float(data['w2']), float(data['w3'])
        algo = data['algo']

        # --- ZAMAN BAŞLAT ---
        start_time = time.time()

        path = None
        if algo == 'ga':
            solver = GeneticAlgorithm(network_graph, w1, w2, w3)
            # Parametreleri isteğe göre ayarlayabilirsin
            path = solver.solve(S, D) 
        elif algo == 'aco':
            solver = ACOAlgorithm(network_graph, w1, w2, w3)
            path = solver.solve(S, D)

        # --- ZAMAN BİTİR ---
        end_time = time.time()
        duration = (end_time - start_time) * 1000 # ms cinsinden

        if not path:
            return jsonify({'success': False, 'message': "Yol bulunamadı!"})

        # Sonuçları Hesapla
        total_delay, rel_cost, bw_cost = AlgorithmUtils.calculate_metrics(network_graph, path)
        real_reliability = math.exp(-rel_cost)
        total_fitness = (w1 * total_delay) + (w2 * rel_cost * 100) + (w3 * bw_cost)

        # Detaylı Bilgiler (Ekran Görüntüsündeki gibi)
        bw_info = AlgorithmUtils.get_bandwidth(network_graph, path)
        req_bw_info = AlgorithmUtils.get_required_bandwidth(network_graph, path)

        metrics = {
            'path': path,
            'delay': f"{total_delay:.4f} ms",
            'reliability': f"{real_reliability:.6f}",
            'cost': f"{total_fitness:.4f}",
            'steps': len(path) - 1,
            # --- EKLENEN YENİ DETAYLAR ---
            'duration': f"{duration:.2f} ms",
            'rel_cost_log': f"{rel_cost:.4f}",
            'bw_cost_inv': f"{bw_cost:.4f}",
            'bw_detail': str(bw_info),
            'req_bw': str(req_bw_info)
        }

        return jsonify({'success': True, 'metrics': metrics})

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': f"Hata: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)