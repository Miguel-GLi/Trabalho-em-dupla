from collections import deque
import heapq
import itertools

VIZINHOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def custo_celula(grid, i, j):
    v = grid[i][j]
    if v == "#":
        return None
    if v == ".":
        return 1
    if v == "~":
        return 4
    raise ValueError(f"simbolo desconhecido no pomar: {v!r}")


def vizinhos_validos(grid, i, j):
    n = len(grid)
    for di, dj in VIZINHOS:
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < n:
            c = custo_celula(grid, ni, nj)
            if c is not None:
                yield (ni, nj), c


def reconstruir_caminho(veio_de, objetivo):
    caminho = [objetivo]
    while caminho[-1] in veio_de:
        caminho.append(veio_de[caminho[-1]])
    caminho.reverse()
    return caminho


def bfs(grid):
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    if inicio == objetivo:
        return {"custo": 0, "passos": 0, "expandidos": 0, "fronteira_max": 0,
                "caminho": [inicio]}

    fronteira = deque([inicio])
    visitado = {inicio}
    veio_de = {}
    custo_ate = {inicio: 0}
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        atual = fronteira.popleft()
        expandidos += 1
        for viz, c in vizinhos_validos(grid, *atual):
            if viz not in visitado:
                visitado.add(viz)
                veio_de[viz] = atual
                custo_ate[viz] = custo_ate[atual] + c
                if viz == objetivo:  # teste de objetivo na geracao
                    caminho = reconstruir_caminho(veio_de, objetivo)
                    return {"custo": custo_ate[viz], "passos": len(caminho) - 1,
                            "expandidos": expandidos, "fronteira_max": fronteira_max,
                            "caminho": caminho}
                fronteira.append(viz)
                fronteira_max = max(fronteira_max, len(fronteira))
    return None


def dfs(grid):
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    pilha = [inicio]
    visitado = {inicio}
    veio_de = {}
    custo_ate = {inicio: 0}
    expandidos = 0
    fronteira_max = 1

    while pilha:
        fronteira_max = max(fronteira_max, len(pilha))
        atual = pilha.pop()
        expandidos += 1
        if atual == objetivo:  # teste de objetivo na expansao
            caminho = reconstruir_caminho(veio_de, objetivo)
            return {"custo": custo_ate[atual], "passos": len(caminho) - 1,
                    "expandidos": expandidos, "fronteira_max": fronteira_max,
                    "caminho": caminho}
        for viz, c in vizinhos_validos(grid, *atual):
            if viz not in visitado:
                visitado.add(viz)
                veio_de[viz] = atual
                custo_ate[viz] = custo_ate[atual] + c
                pilha.append(viz)
        fronteira_max = max(fronteira_max, len(pilha))
    return None


_contador = itertools.count()


def ucs(grid):
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    fronteira = [(0, next(_contador), inicio)]
    veio_de = {}
    custo_ate = {inicio: 0}
    fechado = set()
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        custo, _, atual = heapq.heappop(fronteira)
        if atual in fechado:
            continue
        fechado.add(atual)
        expandidos += 1
        if atual == objetivo:
            caminho = reconstruir_caminho(veio_de, objetivo)
            return {"custo": custo_ate[atual], "passos": len(caminho) - 1,
                    "expandidos": expandidos, "fronteira_max": fronteira_max,
                    "caminho": caminho}
        for viz, c in vizinhos_validos(grid, *atual):
            if viz in fechado:
                continue
            novo_custo = custo_ate[atual] + c
            if viz not in custo_ate or novo_custo < custo_ate[viz]:
                custo_ate[viz] = novo_custo
                veio_de[viz] = atual
                heapq.heappush(fronteira, (novo_custo, next(_contador), viz))
        fronteira_max = max(fronteira_max, len(fronteira))
    return None


def h_zero(pos, objetivo):
    return 0


def h_manhattan(pos, objetivo):
    return abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])


def h_manhattan_x4(pos, objetivo):
    return 4 * h_manhattan(pos, objetivo)


def a_estrela(grid, heuristica):
    n = len(grid)
    inicio, objetivo = (0, 0), (n - 1, n - 1)

    g0 = 0
    f0 = g0 + heuristica(inicio, objetivo)
    fronteira = [(f0, next(_contador), inicio)]
    veio_de = {}
    custo_ate = {inicio: 0}
    fechado = set()
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        f, _, atual = heapq.heappop(fronteira)
        if atual in fechado:
            continue
        fechado.add(atual)
        expandidos += 1
        if atual == objetivo:
            caminho = reconstruir_caminho(veio_de, objetivo)
            return {"custo": custo_ate[atual], "passos": len(caminho) - 1,
                    "expandidos": expandidos, "fronteira_max": fronteira_max,
                    "caminho": caminho}
        for viz, c in vizinhos_validos(grid, *atual):
            if viz in fechado:
                continue
            novo_custo = custo_ate[atual] + c
            if viz not in custo_ate or novo_custo < custo_ate[viz]:
                custo_ate[viz] = novo_custo
                veio_de[viz] = atual
                f_viz = novo_custo + heuristica(viz, objetivo)
                heapq.heappush(fronteira, (f_viz, next(_contador), viz))
        fronteira_max = max(fronteira_max, len(fronteira))
    return None


if __name__ == "__main__":
    import sys
    from gerador_pomar import gerar_pomar

    m = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    grid = gerar_pomar(m)

    r_bfs = bfs(grid)
    r_dfs = dfs(grid)
    r_ucs = ucs(grid)
    r_h1 = a_estrela(grid, h_zero)
    r_h2 = a_estrela(grid, h_manhattan)
    r_h3 = a_estrela(grid, h_manhattan_x4)

    print(f"matricula={m}")
    print(f"BFS : custo={r_bfs['custo']:3d}  passos={r_bfs['passos']:3d}  "
          f"expandidos={r_bfs['expandidos']:4d}  fronteira_max={r_bfs['fronteira_max']:4d}")
    print(f"DFS : custo={r_dfs['custo']:3d}  passos={r_dfs['passos']:3d}  "
          f"expandidos={r_dfs['expandidos']:4d}  fronteira_max={r_dfs['fronteira_max']:4d}")
    print(f"UCS : custo={r_ucs['custo']:3d}  passos={r_ucs['passos']:3d}  "
          f"expandidos={r_ucs['expandidos']:4d}  fronteira_max={r_ucs['fronteira_max']:4d}")
    print(f"A*h1: custo={r_h1['custo']:3d}  passos={r_h1['passos']:3d}  "
          f"expandidos={r_h1['expandidos']:4d}  fronteira_max={r_h1['fronteira_max']:4d}")
    print(f"A*h2: custo={r_h2['custo']:3d}  passos={r_h2['passos']:3d}  "
          f"expandidos={r_h2['expandidos']:4d}  fronteira_max={r_h2['fronteira_max']:4d}")
    print(f"A*h3: custo={r_h3['custo']:3d}  passos={r_h3['passos']:3d}  "
          f"expandidos={r_h3['expandidos']:4d}  fronteira_max={r_h3['fronteira_max']:4d}")
