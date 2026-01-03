import pandas as pd
import numpy as np
import time
import math
import random

from generate.ReadData import ReadData
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.ACOAlgorithm import ACOAlgorithm
from algorithm.AlgorithmUtils import AlgorithmUtils


def run_benchmarks(seed_value=42):
    """
    deney düzeneği
    - 20 (S, D, B) senaryosu
    - 2 algoritma (GA, ACO)
    - 5 tekrar
    - ortalama, std, en iyi, en kötü
    - başarısız senaryolar 
    """

    # Tekrarlanabilirlik
    random.seed(seed_value)
    np.random.seed(seed_value)

    try:
        reader = ReadData()
        graph = reader.read()
        demand_df = pd.read_csv(
            "BSM307_317_Guz2025_TermProject_DemandData.csv", sep=";"
        )
    except Exception as e:
        print(f"hata  veri yüklenemedi : {e}")
        return

    results = []

    total_scenarios = 20
    repeats = 5

    W_DELAY = 0.5
    W_REL = 0.3
    W_RES = 0.2

    print(f"Deney başlatıldı: {total_scenarios} senaryo × 2 algoritma × {repeats} tekrar")

    for idx, row in demand_df.head(total_scenarios).iterrows():
        S = int(row["src"])
        D = int(row["dst"])
        B_req = float(row["demand_mbps"])

        print(f"[{idx+1}/{total_scenarios}] Senaryo {S}->{D} (B={B_req} Mbps)")

        for algo_name, SolverClass in [
            ("GA", GeneticAlgorithm),
            ("ACO", ACOAlgorithm),
        ]:

            costs = []
            delays = []
            reliability_costs = []
            resource_costs = []
            times = []

            invalid_count = 0

            for r in range(repeats):
                start = time.time()

                solver = SolverClass(
                    graph,
                    w1=W_DELAY,
                    w2=W_REL,
                    w3=W_RES,
                )

                path = solver.solve(S, D)
                end = time.time()

                if not path:
                    invalid_count += 1
                    continue

                # bandwidth kısıtı
                feasible = True
                for i in range(len(path) - 1):
                    bw = graph.nx_graph.edges[path[i], path[i + 1]]["bandwidth"]
                    if bw < B_req:
                        feasible = False
                        break

                if not feasible:
                    invalid_count += 1
                    continue

                # metrikler
                total_delay, rel_cost, res_cost = AlgorithmUtils.calculate_metrics(
                    graph, path
                )

                total_cost = (
                    W_DELAY * total_delay
                    + W_REL * rel_cost
                    + W_RES * res_cost
                )

                costs.append(total_cost)
                delays.append(total_delay)
                reliability_costs.append(rel_cost)
                resource_costs.append(res_cost)
                times.append((end - start) * 1000)

            if len(costs) > 0:
                results.append(
                    {
                        "Senaryo": f"{S}->{D}",
                        "Talep_B_Mbps": B_req,
                        "Algoritma": algo_name,
                        "Tekrar_Sayisi": repeats,
                        "Gecerli_Deneme": len(costs),
                        "Basarisiz_Deneme": invalid_count,
                        "Ort_Maliyet": np.mean(costs),
                        "Std_Maliyet": np.std(costs),
                        "En_Iyi_Maliyet": np.min(costs),
                        "En_Kotu_Maliyet": np.max(costs),
                        "Ort_Gecikme_ms": np.mean(delays),
                        "Ort_ReliabilityCost": np.mean(reliability_costs),
                        "Ort_ResourceCost": np.mean(resource_costs),
                        "Ort_Sure_ms": np.mean(times),
                    }
                )
            else:
                results.append(
                    {
                        "Senaryo": f"{S}->{D}",
                        "Talep_B_Mbps": B_req,
                        "Algoritma": algo_name,
                        "Hata": "Tüm tekrarlar bant genişliği veya yol kısıtı nedeniyle başarısız",
                        "Basarisiz_Deneme": invalid_count,
                    }
                )

    df = pd.DataFrame(results)
    df.to_csv("Deney_Raporu.csv", index=False, encoding="utf-8-sig")
    print("\n deney tamamlandı. Rapor oluşturuldu.")

if __name__ == "__main__":
    run_benchmarks()
