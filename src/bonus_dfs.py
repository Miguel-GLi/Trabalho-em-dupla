"""
bonus_dfs.py - Liga de IA (+0,3): contraexemplo construido a mao onde a DFS
(com a ordem de vizinhos N,S,O,L declarada em buscas.py) devolve uma rota
com custo mais que o dobro do otimo.

Construcao: dois "corredores" em L ligando (0,0) a (7,7), disjuntos exceto
nas pontas, cercando um bloco interno todo bloqueado:
  - Corredor "de cima" (linha 0 + coluna 7): todo em solo encharcado (~,
    custo 4) -- e' o primeiro que a DFS visita, porque a ordem de
    expansao N,S,O,L favorece "Leste" antes de "Sul" (ver buscas.py).
  - Corredor "de baixo" (coluna 0 + linha 7): todo em carreador firme
    (., custo 1) -- e' o caminho realmente barato, que a DFS nunca chega
    a tentar porque a busca termina assim que acha o objetivo pelo
    corredor de cima.

Como os dois corredores tem o mesmo numero de passos (14, a distancia de
Manhattan minima entre os cantos), a UCS encontra o corredor de baixo como
otimo (custo 14) enquanto a DFS devolve o corredor de cima (custo 53) --
mais de 2x o valor otimo.
"""

from buscas import bfs, dfs, ucs


def grade_contraexemplo(n=8):
    g = [["#"] * n for _ in range(n)]
    g[0][0] = "."
    for j in range(1, n):
        g[0][j] = "~"            # corredor de cima: linha 0 (caro)
    for i in range(1, n - 1):
        g[i][n - 1] = "~"        # corredor de cima: coluna n-1 (caro)
    g[n - 1][n - 1] = "."
    for i in range(1, n):
        g[i][0] = "."             # corredor de baixo: coluna 0 (barato)
    for j in range(1, n - 1):
        g[n - 1][j] = "."         # corredor de baixo: linha n-1 (barato)
    return g


if __name__ == "__main__":
    g = grade_contraexemplo()
    print("Grade (8x8):")
    for linha in g:
        print(" ".join(linha))

    r_dfs = dfs(g)
    r_ucs = ucs(g)
    razao = r_dfs["custo"] / r_ucs["custo"]

    print(f"\nRota da DFS  : custo={r_dfs['custo']}  passos={r_dfs['passos']}")
    print(f"  caminho: {r_dfs['caminho']}")
    print(f"Rota otima (UCS): custo={r_ucs['custo']}  passos={r_ucs['passos']}")
    print(f"  caminho: {r_ucs['caminho']}")
    print(f"\nRazao custo_DFS / custo_otimo = {razao:.2f}x "
          f"({'>' if razao > 2 else '<='} 2x)")
