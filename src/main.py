"""
main.py - Comando unico do projeto.

Uso:
    python src/main.py <matricula>

Gera, a partir do zero, com a matricula como semente:
    resultados/pomar.txt
    resultados/resultados.csv
    resultados/grafico.png
E imprime no terminal os numeros de Bayes (Parte 4.3) para colar no relatorio.
"""

import csv
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gerador_pomar import gerar_pomar, parametros_sensor
from buscas import bfs, dfs, ucs, a_estrela, h_zero, h_manhattan, h_manhattan_x4
from bayes import relatorio_bayes

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "resultados"


def salvar_pomar(grid, matricula, params_sensor):
    SAIDA.mkdir(exist_ok=True)
    with open(SAIDA / "pomar.txt", "w") as f:
        f.write(f"{matricula}\n")
        for linha in grid:
            f.write(" ".join(linha) + "\n")
        f.write(str(params_sensor) + "\n")


def medir(nome, func, *args):
    t0 = time.perf_counter()
    r = func(*args)
    tempo_ms = (time.perf_counter() - t0) * 1000
    r["tempo_ms"] = round(tempo_ms, 3)
    r["estrategia_ou_heuristica"] = nome
    return r


def main():
    matricula = int(sys.argv[1]) if len(sys.argv) > 1 else 24114028
    grid = gerar_pomar(matricula)
    params_sensor = parametros_sensor(matricula)

    salvar_pomar(grid, matricula, params_sensor)

    linhas = []
    linhas.append(("bfs", "-", *_campos(medir("BFS", bfs, grid))))
    linhas.append(("dfs", "-", *_campos(medir("DFS", dfs, grid))))
    linhas.append(("ucs", "-", *_campos(medir("UCS", ucs, grid))))
    linhas.append(("a_estrela", "h1_zero", *_campos(medir("A*-h1", a_estrela, grid, h_zero))))
    linhas.append(("a_estrela", "h2_manhattan", *_campos(medir("A*-h2", a_estrela, grid, h_manhattan))))
    linhas.append(("a_estrela", "h3_manhattan_x4", *_campos(medir("A*-h3", a_estrela, grid, h_manhattan_x4))))

    SAIDA.mkdir(exist_ok=True)
    with open(SAIDA / "resultados.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["estrategia", "heuristica", "custo", "passos",
                    "nos_expandidos", "fronteira_max", "tempo_ms"])
        for linha in linhas:
            w.writerow(linha)

    # grafico: nos expandidos x estrategia
    nomes = [l[0] if l[1] == "-" else f"{l[0]} ({l[1]})" for l in linhas]
    expandidos = [l[4] for l in linhas]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(nomes, expandidos, color="#3b7a3b")
    ax.set_xlabel("Estrategia / heuristica")
    ax.set_ylabel("Numero de nos expandidos")
    ax.set_title(f"Nos expandidos por estrategia - matricula {matricula}")
    plt.xticks(rotation=20, ha="right")
    for i, v in enumerate(expandidos):
        ax.text(i, v + max(expandidos) * 0.01, str(v), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(SAIDA / "grafico.png", dpi=150)
    plt.close(fig)

    print(f"Semente (matricula): {matricula}")
    print("resultados.csv, grafico.png e pomar.txt gerados em resultados/\n")

    print("=== Resumo busca (Parte 2 e 3) ===")
    print(f"{'estrategia':12s} {'heuristica':16s} {'custo':>6s} {'passos':>7s} "
          f"{'expandidos':>10s} {'fronteira_max':>13s}")
    for l in linhas:
        print(f"{l[0]:12s} {l[1]:16s} {l[2]:6d} {l[3]:7d} {l[4]:10d} {l[5]:13d}")

    print("\n=== Bayes (Parte 4.3) ===")
    r = relatorio_bayes(params_sensor)
    print(f"parametros do sensor: {params_sensor}")
    print(f"(a) P(infestado|positivo) = {r['ppv']:.4f} ({r['ppv']*100:.2f}%)")
    print(f"(b) a cada 100 alertas, ~{r['falsos_por_100_alertas']} sao falsos")
    print(f"(c) alertas/semana={r['alertas_por_semana']:.1f}  "
          f"falsos/semana={r['falsos_por_semana']:.1f}  "
          f"horas/semana em falsos={r['horas_por_semana_em_falsos']:.1f}")
    print(f"(d) sensibilidade 99.9%: novo PPV = "
          f"{r['ppv_com_sensibilidade_99_9']:.4f} "
          f"({r['ppv_com_sensibilidade_99_9']*100:.2f}%)")


def _campos(r):
    return (r["custo"], r["passos"], r["expandidos"], r["fronteira_max"], r["tempo_ms"])


if __name__ == "__main__":
    main()
