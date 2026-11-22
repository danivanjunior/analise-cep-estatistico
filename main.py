import os

from codes.cep_analise import calcular_parametros_cep, detectar_causas_especiais
from codes.etl import carregar_e_preparar_dados, resumir_por_dimensao
from codes.visualizacoes import criar_grafico_cep, criar_grafico_por_turno


def exibir_relatorio(parametros, df_analisado, resumo_turno):
    """Imprime o resumo executivo do CEP usando .format()."""
    print("RELATORIO DE CONTROLE ESTATISTICO DE PROCESSO (CEP)\n")
    print("Total de amostras avaliadas : {}".format(parametros["n_amostras"]))
    print("Media do processo (X_barra) : {:.4f} mm".format(parametros["media"]))
    print(
        "Amplitude Movel media (MR)  : {:.4f} mm".format(parametros["mr_barra"])
    )
    print(
        "Sigma estimado (MR / 1.128) : {:.4f} mm".format(
            parametros["sigma_estimado"]
        )
    )
    print(
        "Desvio padrao amostral (s)  : {:.4f} mm".format(
            parametros["desvio_amostral"]
        )
    )
    print("UCL (Limite Superior 3s)    : {:.4f} mm".format(parametros["ucl"]))
    print("LCL (Limite Inferior 3s)    : {:.4f} mm".format(parametros["lcl"]))

    if parametros["cp"] == parametros["cp"]:
        print(
            "Indices de Capacidade       : Cp = {:.2f} | Cpk = {:.2f}".format(
                parametros["cp"], parametros["cpk"]
            )
        )

    print("\n")
    print("RESUMO POR TURNO:")
    for _, linha in resumo_turno.iterrows():
        print(
            "  Turno {:6s} | n={:2d} | Media={:.3f} mm | DP={:.3f} mm".format(
                str(linha["turno"]),
                int(linha["qtd_amostras"]),
                float(linha["media"]),
                float(linha["desvio_padrao"]),
            )
        )

    print("\n")
    anomalias = df_analisado[df_analisado["fora_de_controle"]]
    if not anomalias.empty:
        print(
            "ALERTA: {} amostra(s) com indicio de causa especial:".format(
                len(anomalias)
            )
        )
        for _, row in anomalias.iterrows():
            print(
                "  - Amostra {:2d} ({} - {}): {:.3f} mm -> {}".format(
                    int(row["amostra"]),
                    str(row["turno"]),
                    str(row["maquina"]),
                    float(row["diametro_mm"]),
                    str(row["alertas"]),
                )
            )
    else:
        print("OK: Processo sem indicios de causa especial pelas regras atuais.")
    print("\n")


def main():
    caminho_csv = os.path.join("data", "dados_usinagem_cep.csv")
    df = carregar_e_preparar_dados(caminho_csv)

    parametros = calcular_parametros_cep(df)
    df_analisado = detectar_causas_especiais(df, parametros)
    resumo_turno = resumir_por_dimensao(df_analisado, "turno")

    exibir_relatorio(parametros, df_analisado, resumo_turno)

    os.makedirs("outputs", exist_ok=True)
    caminho_saida = os.path.join("outputs", "resultado_cep.csv")
    df_analisado.to_csv(caminho_saida, index=False)
    print("Arquivo consolidado salvo em: {}".format(caminho_saida))

    fig_cep = criar_grafico_cep(df_analisado, parametros)
    fig_turno = criar_grafico_por_turno(df_analisado)

    fig_cep.show()
    fig_turno.show()


if __name__ == "__main__":
    main()