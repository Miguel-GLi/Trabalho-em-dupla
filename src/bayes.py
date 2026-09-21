"""
bayes.py - Parte 4.3: P(infestado | sensor positivo) e derivados,
usando os parametros do sensor gerados pela matricula da dupla.
"""


def p_infestado_dado_positivo(prevalencia, sensibilidade, fpr):
    """Teorema de Bayes:
    P(inf|+) = P(+|inf) P(inf) / P(+)
             = sensibilidade * prevalencia /
               (sensibilidade * prevalencia + fpr * (1 - prevalencia))
    """
    numerador = sensibilidade * prevalencia
    denominador = numerador + fpr * (1 - prevalencia)
    return numerador / denominador


def relatorio_bayes(params):
    prev = params["prevalencia"]
    sens = params["sensibilidade"]
    fpr = params["taxa_falso_positivo"]
    talhoes_semana = params["talhoes_por_semana"]

    ppv = p_infestado_dado_positivo(prev, sens, fpr)
    taxa_falsos_entre_alertas = 1 - ppv  # fracao dos alertas positivos que sao falsos

    # (b) a cada 100 alertas, quantos sao falsos
    falsos_por_100 = round(taxa_falsos_entre_alertas * 100, 1)

    # (c) alertas totais esperados por semana e quantos sao falsos
    p_positivo = sens * prev + fpr * (1 - prev)
    alertas_por_semana = p_positivo * talhoes_semana
    falsos_por_semana = taxa_falsos_entre_alertas * alertas_por_semana
    horas_por_semana = falsos_por_semana * 12 / 60

    # (d) aumentando sensibilidade para 99,9%, mantendo o MESMO fpr
    sens_nova = 0.999
    ppv_novo = p_infestado_dado_positivo(prev, sens_nova, fpr)

    return {
        "prevalencia": prev,
        "sensibilidade": sens,
        "fpr": fpr,
        "talhoes_por_semana": talhoes_semana,
        "ppv": ppv,
        "falsos_por_100_alertas": falsos_por_100,
        "alertas_por_semana": alertas_por_semana,
        "falsos_por_semana": falsos_por_semana,
        "horas_por_semana_em_falsos": horas_por_semana,
        "ppv_com_sensibilidade_99_9": ppv_novo,
    }


if __name__ == "__main__":
    import sys
    from gerador_pomar import parametros_sensor

    m = int(sys.argv[1]) if len(sys.argv) > 1 else 24114028
    params = parametros_sensor(m)
    r = relatorio_bayes(params)

    print(f"matricula={m}")
    print(f"parametros do sensor: {params}")
    print()
    print(f"(a) P(infestado | positivo) = {r['ppv']:.4f}  "
          f"({r['ppv']*100:.2f}%)")
    print(f"(b) A cada 100 alertas, cerca de {r['falsos_por_100_alertas']} sao falsos.")
    print(f"(c) Alertas esperados/semana: {r['alertas_por_semana']:.1f}  "
          f"| falsos/semana: {r['falsos_por_semana']:.1f}  "
          f"| horas/semana perseguindo falsos: {r['horas_por_semana_em_falsos']:.1f}")
    print(f"(d) Com sensibilidade 99,9% (fpr mantida): "
          f"novo PPV = {r['ppv_com_sensibilidade_99_9']:.4f} "
          f"({r['ppv_com_sensibilidade_99_9']*100:.2f}%)")
