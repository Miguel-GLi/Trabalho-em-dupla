"""
especialista.py - Mini sistema especialista para manejo de talhao, com
encadeamento para tras (backward chaining) e explicacao da cadeia de regras.

Regras (SE ... ENTAO ...)
--------------------------
R1: SE armadilha_positiva E umidade_alta E dias_desde_pulverizacao > 14
    ENTAO inspecionar_prioridade_alta
R2: SE armadilha_positiva E NAO umidade_alta
    ENTAO inspecionar_prioridade_media
R3: SE folhas_amareladas E umidade_alta
    ENTAO risco_fungico
R4: SE risco_fungico E dias_desde_pulverizacao > 21
    ENTAO inspecionar_prioridade_alta
R5: SE inspecionar_prioridade_alta E talhao_proximo_reservatorio
    ENTAO inspecionar_prioridade_alta_hoje
R6: SE inspecionar_prioridade_media E fila_inspecao_livre
    ENTAO agendar_inspecao_48h
R7: SE NAO armadilha_positiva E NAO folhas_amareladas
    ENTAO talhao_normal
R8: SE armadilha_positiva E dias_desde_pulverizacao <= 14
    ENTAO aguardar_efeito_pulverizacao
"""

REGRAS = [
    {"nome": "R1", "se": ["armadilha_positiva", "umidade_alta", "dias_desde_pulverizacao>14"],
     "entao": "inspecionar_prioridade_alta"},
    {"nome": "R2", "se": ["armadilha_positiva", "nao umidade_alta"],
     "entao": "inspecionar_prioridade_media"},
    {"nome": "R3", "se": ["folhas_amareladas", "umidade_alta"],
     "entao": "risco_fungico"},
    {"nome": "R4", "se": ["risco_fungico", "dias_desde_pulverizacao>21"],
     "entao": "inspecionar_prioridade_alta"},
    {"nome": "R5", "se": ["inspecionar_prioridade_alta", "talhao_proximo_reservatorio"],
     "entao": "inspecionar_prioridade_alta_hoje"},
    {"nome": "R6", "se": ["inspecionar_prioridade_media", "fila_inspecao_livre"],
     "entao": "agendar_inspecao_48h"},
    {"nome": "R7", "se": ["nao armadilha_positiva", "nao folhas_amareladas"],
     "entao": "talhao_normal"},
    {"nome": "R8", "se": ["armadilha_positiva", "dias_desde_pulverizacao<=14"],
     "entao": "aguardar_efeito_pulverizacao"},
]


def _fato_satisfeito(fato, base):
    """Avalia um fato/condicao contra a base de fatos, incluindo negacoes
    ('nao X') e comparacoes simples ('dias_desde_pulverizacao>14')."""
    if fato.startswith("nao "):
        return not _fato_satisfeito(fato[4:], base)
    for op in (">", "<=", "<", ">="):
        if op in fato:
            var, val = fato.split(op)
            if var not in base:
                return False
            try:
                return eval(f"{base[var]}{op}{val}")  # comparacao numerica simples
            except Exception:
                return False
    return bool(base.get(fato, False))


def encadeamento_para_tras(objetivo, base, regras=REGRAS, trilha=None, visitados=None):
    """Tenta provar 'objetivo' a partir da base de fatos, retornando
    (True/False, trilha_de_regras_usadas)."""
    if trilha is None:
        trilha = []
    if visitados is None:
        visitados = set()

    if _fato_satisfeito(objetivo, base):
        return True, trilha

    if objetivo in visitados:
        return False, trilha
    visitados.add(objetivo)

    for regra in regras:
        if regra["entao"] != objetivo:
            continue
        todas_ok = True
        subtrilha = []
        for premissa in regra["se"]:
            premissa_base = premissa
            for op in (">", "<=", "<", ">="):
                if op in premissa:
                    premissa_base = premissa.split(op)[0]
                    break
            if premissa_base.startswith("nao "):
                premissa_base = premissa_base[4:]

            if _fato_satisfeito(premissa, base):
                continue
            ok, sub = encadeamento_para_tras(premissa_base, base, regras, [], visitados)
            if not ok:
                todas_ok = False
                break
            subtrilha.extend(sub)
        if todas_ok:
            nova_trilha = trilha + subtrilha + [regra["nome"]]
            return True, nova_trilha
    return False, trilha


def explicar(objetivo, base):
    ok, trilha = encadeamento_para_tras(objetivo, base)
    print(f"Objetivo: {objetivo} -> {'PROVADO' if ok else 'NAO PROVADO'}")
    if ok:
        if trilha:
            print("Cadeia de regras usada (por que concluí isso):")
            for r in trilha:
                regra = next(x for x in REGRAS if x["nome"] == r)
                print(f"  {r}: SE {' E '.join(regra['se'])} ENTAO {regra['entao']}")
        else:
            print("  (fato ja estava diretamente na base)")
    return ok, trilha


if __name__ == "__main__":
    print("=== Caso 1: talhao com armadilha positiva, solo umido, ha 20 dias sem pulverizar")
    base1 = {"armadilha_positiva": True, "umidade_alta": True,
             "dias_desde_pulverizacao": 20, "talhao_proximo_reservatorio": True}
    explicar("inspecionar_prioridade_alta_hoje", base1)

    print("\n=== Caso 2: armadilha positiva, solo seco")
    base2 = {"armadilha_positiva": True, "umidade_alta": False,
             "fila_inspecao_livre": True}
    explicar("agendar_inspecao_48h", base2)

    print("\n=== Caso 3 (Parte 4.2 - quebrando a base): folhas amareladas por deficiencia "
          "de nutrientes, sem risco de praga, mas a base classifica como risco fungico")
    base3 = {"folhas_amareladas": True, "umidade_alta": True,
              "dias_desde_pulverizacao": 25}
    explicar("inspecionar_prioridade_alta", base3)
