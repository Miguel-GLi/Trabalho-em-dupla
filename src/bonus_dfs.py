from buscas import bfs, dfs, ucs


def grade_contraexemplo(n=8):
    g = [["#"] * n for _ in range(n)]
    g[0][0] = "."
    for j in range(1, n):
        g[0][j] = "~"
    for i in range(1, n - 1):
        g[i][n - 1] = "~"
    g[n - 1][n - 1] = "."
    for i in range(1, n):
        g[i][0] = "."
    for j in range(1, n - 1):
        g[n - 1][j] = "."
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
