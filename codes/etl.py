"""Módulo de ETL (Extração, Transformação e Carga) para dados de CEP industrial.

Responsável por ler o arquivo CSV de medições da linha de usinagem, validar
as colunas exigidas, padronizar os tipos numéricos, calcular a amplitude
móvel (MR) entre medições consecutivas e gerar resumos por dimensão.
"""

import pandas as pd


def carregar_e_preparar_dados(caminho_csv):
    """Carrega os dados de medições industriais e prepara colunas auxiliares.

    Args:
        caminho_csv (str): Caminho do arquivo CSV com as medições do processo.

    Returns:
        pd.DataFrame: DataFrame ordenado por amostra, com a coluna
            ``diametro_mm`` em formato numérico e ``amplitude_movel``
            calculada entre observações consecutivas.
    """
    df = pd.read_csv(caminho_csv)

    colunas_obrigatorias = {"amostra", "turno", "maquina", "diametro_mm"}
    faltantes = colunas_obrigatorias - set(df.columns)
    if faltantes:
        raise ValueError(
            "Colunas obrigatórias ausentes no CSV: {}".format(sorted(list(faltantes)))
        )

    df = df.sort_values("amostra").reset_index(drop=True)
    df["diametro_mm"] = pd.to_numeric(df["diametro_mm"], errors="raise")
    df["amplitude_movel"] = df["diametro_mm"].diff().abs()

    return df


def resumir_por_dimensao(df, coluna_grupo):
    """Gera estatísticas descritivas agregadas por uma coluna categórica.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados de medição do processo.
        coluna_grupo (str): Nome da coluna usada para agrupamento (ex.:
            ``"turno"`` ou ``"maquina"``).

    Returns:
        pd.DataFrame: Tabela resumo com quantidade de amostras, média, desvio
            padrão, mínimo, máximo e amplitude total por grupo.
    """
    resumo = (
        df.groupby(coluna_grupo, as_index=False)["diametro_mm"]
        .agg(
            qtd_amostras="count",
            media="mean",
            desvio_padrao="std",
            minimo="min",
            maximo="max",
        )
    )
    resumo["amplitude_total"] = resumo["maximo"] - resumo["minimo"]
    return resumo
