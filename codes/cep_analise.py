"""Esse módulo é responsável por calcular parâmetros e detectar anomalias."""

import numpy as np
import pandas as pd


def calcular_parametros_cep(df):
    """Calcula limites de controle (3 Sigma e zona 2 Sigma), MR e índices de capacidade."""
    valores = df["diametro_mm"].to_numpy(dtype=float)
    n = len(valores)

    media = float(np.mean(valores))
    desvio_amostral = float(np.std(valores, ddof=1))

    # Amplitude Móvel (d2 = 1.128 para n=2 observações consecutivas)
    mr_series = df["amplitude_movel"].dropna()
    mr_barra = float(mr_series.mean()) if len(mr_series) > 0 else 0.0
    d2 = 1.128
    sigma_estimado = mr_barra / d2 if mr_barra > 0 else desvio_amostral

    # Limites baseados em sigma_estimado (padrão clássico de carta individual I)
    ucl = media + 3.0 * sigma_estimado
    lcl = media - 3.0 * sigma_estimado
    uwl_sup = media + 2.0 * sigma_estimado
    uwl_inf = media - 2.0 * sigma_estimado

    # Limites da carta de Amplitude Móvel (D4 = 3.267 para n=2; D3 = 0)
    ucl_mr = 3.267 * mr_barra
    lcl_mr = 0.0

    # Índices de capacidade (se houver limites de especificação LSL e USL)
    cp = np.nan
    cpk = np.nan
    if "lsl" in df.columns and "usl" in df.columns and sigma_estimado > 0:
        lsl = float(df["lsl"].iloc[0])
        usl = float(df["usl"].iloc[0])
        cp = (usl - lsl) / (6.0 * sigma_estimado)
        cpu = (usl - media) / (3.0 * sigma_estimado)
        cpl = (media - lsl) / (3.0 * sigma_estimado)
        cpk = min(cpu, cpl)

    return {
        "n_amostras": n,
        "media": media,
        "desvio_amostral": desvio_amostral,
        "sigma_estimado": sigma_estimado,
        "mr_barra": mr_barra,
        "ucl": ucl,
        "lcl": lcl,
        "uwl_sup": uwl_sup,
        "uwl_inf": uwl_inf,
        "ucl_mr": ucl_mr,
        "lcl_mr": lcl_mr,
        "cp": cp,
        "cpk": cpk,
    }


def detectar_causas_especiais(df, parametros):
    """Classifica cada amostra quanto a possíveis causas especiais de variação."""
    valores = df["diametro_mm"].to_numpy(dtype=float)
    media = parametros["media"]
    ucl = parametros["ucl"]
    lcl = parametros["lcl"]

    motivos_por_linha = [[] for _ in range(len(valores))]

    # Regra 1: Fora dos limites 3 Sigma (UCL / LCL)
    for i, val in enumerate(valores):
        if val > ucl:
            motivos_por_linha[i].append("Acima do UCL (3 Sigma)")
        elif val < lcl:
            motivos_por_linha[i].append("Abaixo do LCL (3 Sigma)")

    # Regra 2: 7 pontos consecutivos do mesmo lado da média
    lado = np.where(valores > media, 1, np.where(valores < media, -1, 0))
    contagem_lado = 1
    for i in range(1, len(lado)):
        if lado[i] != 0 and lado[i] == lado[i - 1]:
            contagem_lado += 1
        else:
            contagem_lado = 1

        if contagem_lado >= 7:
            inicio = i - contagem_lado + 1
            for j in range(inicio, i + 1):
                motivos_por_linha[j].append("Sequencia de 7+ pontos no mesmo lado da media")

    # Regra 3: 6 pontos consecutivos em tendência (crescente ou decrescente)
    diffs = np.diff(valores)
    direcao = np.where(diffs > 0, 1, np.where(diffs < 0, -1, 0))
    contagem_tend = 1
    for i in range(1, len(direcao)):
        if direcao[i] != 0 and direcao[i] == direcao[i - 1]:
            contagem_tend += 1
        else:
            contagem_tend = 1

        # direcao[k] refere-se à transição entre amostra k e k+1 (índice k+1)
        if contagem_tend >= 6:
            fim_amostra = i + 1
            inicio_amostra = fim_amostra - contagem_tend
            for j in range(inicio_amostra, fim_amostra + 1):
                motivos_por_linha[j].append("Tendencia de 6+ pontos consecutivos")

    df_resultado = df.copy()
    df_resultado["alertas"] = [
        " | ".join(sorted(list(set(m)))) if m else "Normal"
        for m in motivos_por_linha
    ]
    df_resultado["fora_de_controle"] = df_resultado["alertas"] != "Normal"
    return df_resultado