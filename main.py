import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import math

# --- Modülleri İçe Aktar ---
from generate.ReadData import ReadData
from generate.TopologyGenerator import TopologyGenerator
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.ACOAlgorithm import ACOAlgorithm  # ACO Eklendi
from algorithm.AlgorithmUtils import AlgorithmUtils

# Global değişken
network_graph = None

def load_graph():
    global network_graph
    try:
        source_type = graph_source_var.get()
        if source_type == "Random":
            gen = TopologyGenerator()
            network_graph = gen.generate(num_nodes=250)
            msg = "Rastgele Topology Oluşturuldu (250 Node)."
        else:
            reader = ReadData()
            network_graph = reader.read()
            msg = "CSV Verileri Yüklendi."
            
        # Ekrana çiz
        draw_graph()
        log_message(f"{msg}\nNode Sayısı: {len(network_graph.nodes)}\nLink Sayısı: {len(network_graph.links)}")
        
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def draw_graph(path=None):
    if network_graph is None: return
    
    plt.clf()
    G = network_graph.nx_graph
    pos = nx.spring_layout(G, seed=42)
    
    nx.draw(G, pos, node_size=20, node_color='lightblue', with_labels=False)
    
    if path:
        nx.draw_networkx_edges(G, pos, 
                               edgelist=list(zip(path, path[1:])), 
                               edge_color="red", width=2)
        
        if len(path) > 2:
            intermediate_nodes = path[1:-1]
            nx.draw_networkx_nodes(G, pos, nodelist=intermediate_nodes, 
                                   node_color="red", node_size=30)
            
        nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], 
                               node_color="green", node_size=80)
        
        nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], 
                               node_color="red", node_size=80)
        
    canvas.draw()

def log_message(msg):
    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, msg)
    result_text.config(state="disabled")

def calculate():
    if network_graph is None:
        messagebox.showwarning("Uyarı", "Önce Grafiği Yükleyin!")
        return
        
    try:
        # Girdileri Al
        try:
            S = int(entry_s.get())
            D = int(entry_d.get())
            w1 = float(entry_w1.get()) # Delay Ağırlığı
            w2 = float(entry_w2.get()) # Reliability Ağırlığı
            w3 = float(entry_w3.get()) # Bandwidth Ağırlığı
        except ValueError:
             messagebox.showerror("Hata", "Lütfen tüm alanlara sayısal değer girin.")
             return

        algo_name = algo_var.get()
        
        # Algoritma Çalıştırma
        start_time = time.time()
        path = None
        
        if algo_name == "GA (Genetik)":
            solver = GeneticAlgorithm(network_graph, w1, w2, w3)
            path = solver.solve(S, D)
        elif algo_name == "ACO (Karınca)":
            solver = ACOAlgorithm(network_graph, w1, w2, w3)
            path = solver.solve(S, D)
            
        duration = (time.time() - start_time) * 1000 # ms cinsinden
        
        if not path:
            log_message(f"{algo_name} ile {S}->{D} arasında yol bulunamadı.")
            return

        # Sonuç Hesaplama (AlgorithmUtils güncellendiği için burası doğru çalışacak)
        total_delay, rel_cost, bw_cost = AlgorithmUtils.calculate_metrics(network_graph, path)
        
        # Toplam Skor (Fitness)
        # Not: Reliability ve BW cost değerleri logaritmik/ters olduğu için
        # ağırlıklarla direkt çarpmak bazen dengesiz olabilir ama PDF'teki "Weighted Sum" formülü bu.
        total_fitness = (w1 * total_delay) + (w2 * rel_cost * 100) + (w3 * bw_cost)
        
        # Ekrana basılacak gerçek güvenilirlik değeri (Cost'tan geri dönüşüm)
        # Cost = -ln(R)  =>  R = e^(-Cost)
        real_reliability = math.exp(-rel_cost)
        
        bw_info = AlgorithmUtils.get_bandwidth(network_graph, path)
        
        sb = f">>> SONUÇ ({algo_name}) <<<\n"
        sb += f"Kaynak: {S} -> Hedef: {D}\n"
        sb += f"Adım Sayısı: {len(path)-1}\n"
        sb += f"Yol: {path}\n"
        sb += f"Çalışma Süresi: {duration:.2f} ms\n"
        sb += f"--------------------------------\n"
        sb += f"Toplam Gecikme (Delay): {total_delay:.4f} ms\n"
        sb += f"Toplam Güvenilirlik: {real_reliability:.6f}\n"
        sb += f"Güvenilirlik Maliyeti (-log): {rel_cost:.4f}\n"
        sb += f"Kaynak Maliyeti (1000/BW): {bw_cost:.4f}\n"
        sb += f"--------------------------------\n"
        sb += f"HESAPLANAN SKOR (Cost): {total_fitness:.4f}\n"
        sb += f"Detay: {bw_info}\n"
        sb += f"{AlgorithmUtils.get_required_bandwidth(network_graph, path)}\n"
        
        log_message(sb)
        draw_graph(path)

    except Exception as e:
        log_message(f"Beklenmeyen Hata: {e}")
        print(e)

# --- GUI BAŞLANGIÇ ---
window = tk.Tk()
window.title("BSM307 - Proje (GA & ACO)")
window.geometry("1200x750")

main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True)

# Sol Panel
left = tk.Frame(main_frame, width=350, bg="#f0f0f0")
left.pack(side="left", fill="y", padx=10, pady=10)
left.pack_propagate(False)

# Sağ Panel
right = tk.Frame(main_frame, bg="white")
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Kontroller
tk.Label(left, text="Ağ Kaynağı:", bg="#f0f0f0", font=("Arial", 11, "bold")).pack(anchor="w")
graph_source_var = tk.StringVar(value="Random")
tk.Radiobutton(left, text="Random (250 Node)", variable=graph_source_var, value="Random", bg="#f0f0f0").pack(anchor="w")
tk.Radiobutton(left, text="CSV Dosyası", variable=graph_source_var, value="CSV", bg="#f0f0f0").pack(anchor="w")
tk.Button(left, text="Ağı Yükle / Oluştur", command=load_graph, bg="green", fg="white").pack(fill="x", pady=5)

tk.Label(left, text="Kaynak Node ID (S):", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
entry_s = tk.Entry(left)
entry_s.pack(fill="x", pady=(0, 5))

tk.Label(left, text="Hedef Node ID (D):", bg="#f0f0f0").pack(anchor="w")
entry_d = tk.Entry(left)
entry_d.pack(fill="x", pady=(0, 5))

tk.Label(left, text="Algoritma:", bg="#f0f0f0").pack(anchor="w", pady=(5,0))
algo_var = tk.StringVar()
# SADECE GA VE ACO SEÇENEKLERİ
combo = ttk.Combobox(left, textvariable=algo_var, values=["GA (Genetik)", "ACO (Karınca)"])
combo.current(0)
combo.pack(fill="x")

tk.Label(left, text="Ağırlıklar (Delay, Reliability, BW):", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
# Varsayılan ağırlıklar PDF örneğine uygun
entry_w1 = tk.Entry(left); entry_w1.insert(0,"0.33"); entry_w1.pack(fill="x") # Delay
entry_w2 = tk.Entry(left); entry_w2.insert(0,"0.33"); entry_w2.pack(fill="x") # Reliability
entry_w3 = tk.Entry(left); entry_w3.insert(0,"0.34"); entry_w3.pack(fill="x") # Resource

tk.Button(left, text="HESAPLA", command=calculate, bg="blue", fg="white", font=("Arial", 12, "bold")).pack(fill="x", pady=20)

result_text = tk.Text(left, height=20, bg="#ddd", font=("Consolas", 9))
result_text.pack(fill="both", expand=True)

# Grafik
fig = plt.figure(figsize=(5,5))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack(fill="both", expand=True)

window.mainloop()