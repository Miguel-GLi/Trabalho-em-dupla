"""
busca_local.py - Escolha de K talhoes para inspecao com bateria limitada.

Modelagem do problema de busca local
-------------------------------------
Estado: um conjunto de K talhoes livres (nao bloqueados) do pomar,
        representado como uma tupla ordenada de K coordenadas (i, j).

Vizinhanca: trocar (swap) UM talhao do estado atual por UM talhao livre que
        nao esta no estado. De um estado com K talhoes saem ate
        K * (livres - K) vizinhos.

Funcao objetivo (o que o agente maximiza):
        objetivo(estado) = soma_risco(estado) - ALPHA * custo_percurso(estado)

        - soma_risco: cada talhao tem um risco de praga associado ao tipo de
          terreno (solo encharcado retem umidade e favorece pragas, entao
          pesa mais que carreador firme): risco('~') = 3, risco('.') = 1.
        - custo_percurso: custo aproximado (Manhattan) de um passeio guloso
          do portao (0,0) por todos os talhoes do estado, na ordem do vizinho
          mais proximo a cada passo -- proxy do gasto de bateria/tempo para
          visitar os K talhoes escolhidos nas 6 horas disponiveis.
        - ALPHA pondera o quanto o deslocamento "pesa" contra o risco
          inspecionado; ALPHA maior favorece talhoes proximos entre si.

O objetivo é escolher os K talhões que maximizam risco coberto por unidade
de deslocamento gasto -- ou seja, o melhor uso das 6 horas de bateria.
"""

import math
import random

ALPHA = 0.5
K_PADRAO = 15


def risco(grid, i, j):
    v = grid[i][j]
    if v == "~":
        return 3
    if v == ".":
        return 1
    return 0  # bloqueado nunca deveria estar aqui


def talhoes_livres(grid):
    n = len(grid)
    return [(i, j) for i in range(n) for j in range(n) if grid[i][j] != "#"]


def custo_percurso_guloso(estado, origem=(0, 0)):
    """Aproxima o custo de visitar todos os talhoes do estado: tour guloso
    do vizinho mais proximo (distancia Manhattan), comecando no portao."""
    restantes = list(estado)
    atual = origem
    custo = 0
    while restantes:
        prox = min(restantes, key=lambda p: abs(p[0] - atual[0]) + abs(p[1] - atual[1]))
        custo += abs(prox[0] - atual[0]) + abs(prox[1] - atual[1])
        atual = prox
        restantes.remove(prox)
    return custo


def objetivo(grid, estado):
    soma_risco = sum(risco(grid, i, j) for i, j in estado)
    custo = custo_percurso_guloso(estado)
    return soma_risco - ALPHA * custo


def estado_inicial(livres, k, rng):
    return tuple(rng.sample(livres, k))


def vizinhos_swap(estado, livres, rng, amostra=None):
    """Gera vizinhos por troca de 1 talhao. Se 'amostra' for dado, sorteia
    apenas essa quantidade de vizinhos (usado na tempera simulada)."""
    fora = [p for p in livres if p not in estado]
    vizinhos = []
    candidatos = list(estado)
    if amostra:
        pares = [(rng.choice(candidatos), rng.choice(fora)) for _ in range(amostra)]
    else:
        pares = [(dentro, fnovo) for dentro in candidatos for fnovo in fora]
    for dentro, novo in pares:
        novo_estado = tuple(p for p in estado if p != dentro) + (novo,)
        vizinhos.append(novo_estado)
    return vizinhos


def subida_de_encosta(grid, livres, k, rng):
    estado = estado_inicial(livres, k, rng)
    valor = objetivo(grid, estado)
    while True:
        vizinhos = vizinhos_swap(estado, livres, rng)
        melhor_vizinho, melhor_valor = None, valor
        for viz in vizinhos:
            v = objetivo(grid, viz)
            if v > melhor_valor:
                melhor_vizinho, melhor_valor = viz, v
        if melhor_vizinho is None:  # nenhum vizinho melhora -> otimo local
            return melhor_valor if melhor_vizinho else valor
        estado, valor = melhor_vizinho, melhor_valor


def tempera_simulada(grid, livres, k, rng, t0=10.0, resfriamento=0.995, iteracoes=800):
    estado = estado_inicial(livres, k, rng)
    valor = objetivo(grid, estado)
    melhor_valor = valor
    t = t0
    for _ in range(iteracoes):
        candidatos = vizinhos_swap(estado, livres, rng, amostra=1)
        if not candidatos:
            break
        vizinho = candidatos[0]
        v = objetivo(grid, vizinho)
        delta = v - valor
        # Aceita sempre que melhora; aceita PIORA com probabilidade
        # exp(delta / t) -- e' essa aceitacao proposital de piora que
        # permite escapar de otimos locais (Aula 04).
        if delta > 0 or rng.random() < math.exp(delta / t):
            estado, valor = vizinho, v
            melhor_valor = max(melhor_valor, valor)
        t *= resfriamento
        if t < 1e-3:
            break
    return melhor_valor


def estatisticas(valores):
    media = sum(valores) / len(valores)
    var = sum((v - media) ** 2 for v in valores) / len(valores)
    return media, math.sqrt(var), max(valores)


def rodar_experimento(grid, k=K_PADRAO, execucoes=30, semente_base=42):
    livres = talhoes_livres(grid)
    hc_valores, sa_valores = [], []
    for r in range(execucoes):
        rng = random.Random(semente_base + r)
        hc_valores.append(subida_de_encosta(grid, livres, k, rng))
        rng2 = random.Random(semente_base + 1000 + r)
        sa_valores.append(tempera_simulada(grid, livres, k, rng2))
    return {
        "subida_de_encosta": estatisticas(hc_valores),
        "tempera_simulada": estatisticas(sa_valores),
        "hc_valores": hc_valores,
        "sa_valores": sa_valores,
    }


if __name__ == "__main__":
    import sys
    from gerador_pomar import gerar_pomar

    m = int(sys.argv[1]) if len(sys.argv) > 1 else 24114028
    grid = gerar_pomar(m)
    res = rodar_experimento(grid)

    for nome in ("subida_de_encosta", "tempera_simulada"):
        media, desvio, melhor = res[nome]
        print(f"{nome:20s}: media={media:7.2f}  desvio={desvio:6.2f}  melhor={melhor:7.2f}")
