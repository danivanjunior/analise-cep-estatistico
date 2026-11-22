"""Esse módulo é responsável por gerar as visualizações gráficas."""

import plotly.express as px
import plotly.graph_objects as go


def criar_grafico_cep(df_analisado, parametros):
    """Cria a Carta de Controle Individual (I) com limites 3 Sigma e alertas."""
    fig = go.Figure()

    # Série principal de medições
    fig.add_trace(
        go.Scatter(
            x=df_analisado["amostra"],
            y=df_analisado["diametro_mm"],
            mode="lines+markers",
            name="Diâmetro Medido (mm)",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=7),
            hovertemplate=(
                "Amostra: %{x}<br>"
                "Diâmetro: %{y:.3f} mm<br>"
                "<extra></extra>"
            ),
        )
    )

    # Linha da Média
    fig.add_trace(
        go.Scatter(
            x=df_analisado["amostra"],
            y=[parametros["media"]] * len(df_analisado),
            mode="lines",
            name="Média ({:.3f})".format(parametros["media"]),
            line=dict(color="#2ca02c", width=2),
        )
    )

    # Limite Superior de Controle (UCL)
    fig.add_trace(
        go.Scatter(
            x=df_analisado["amostra"],
            y=[parametros["ucl"]] * len(df_analisado),
            mode="lines",
            name="UCL ({:.3f})".format(parametros["ucl"]),
            line=dict(color="#d62728", width=2, dash="dash"),
        )
    )

    # Limite Inferior de Controle (LCL)
    fig.add_trace(
        go.Scatter(
            x=df_analisado["amostra"],
            y=[parametros["lcl"]] * len(df_analisado),
            mode="lines",
            name="LCL ({:.3f})".format(parametros["lcl"]),
            line=dict(color="#d62728", width=2, dash="dash"),
        )
    )

    # Limites de Especificação de Engenharia (se existirem)
    if "usl" in df_analisado.columns and "lsl" in df_analisado.columns:
        usl_val = float(df_analisado["usl"].iloc[0])
        lsl_val = float(df_analisado["lsl"].iloc[0])
        fig.add_hline(
            y=usl_val,
            line_dash="dot",
            line_color="#7f7f7f",
            annotation_text="USL ({:.2f})".format(usl_val),
            annotation_position="top left",
        )
        fig.add_hline(
            y=lsl_val,
            line_dash="dot",
            line_color="#7f7f7f",
            annotation_text="LSL ({:.2f})".format(lsl_val),
            annotation_position="bottom left",
        )

    # Destaque para amostras com causas especiais
    anomalias = df_analisado[df_analisado["fora_de_controle"]]
    if not anomalias.empty:
        textos_hover = [
            "Amostra: {}<br>Diâmetro: {:.3f} mm<br>Alerta: {}".format(
                int(row["amostra"]), float(row["diametro_mm"]), row["alertas"]
            )
            for _, row in anomalias.iterrows()
        ]
        fig.add_trace(
            go.Scatter(
                x=anomalias["amostra"],
                y=anomalias["diametro_mm"],
                mode="markers",
                name="Causa Especial / Alerta",
                marker=dict(
                    color="#ff7f0e",
                    size=13,
                    symbol="diamond",
                    line=dict(color="black", width=1.5),
                ),
                text=textos_hover,
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        title="Carta de Controle CEP (Valores Individuais) — Diâmetro de Eixo (mm)",
        xaxis_title="Número da Amostra",
        yaxis_title="Diâmetro (mm)",
        template="plotly_white",
        hovermode="closest",
    )
    return fig


def criar_grafico_por_turno(df_analisado):
    """Gráfico simples com Plotly Express para comparar dispersão por turno."""
    fig = px.box(
        df_analisado,
        x="turno",
        y="diametro_mm",
        color="maquina",
        points="all",
        title="Distribuição do Diâmetro por Turno e Máquina",
        labels={
            "turno": "Turno de Produção",
            "diametro_mm": "Diâmetro Medido (mm)",
            "maquina": "Máquina CNC",
        },
    )
    fig.update_layout(template="plotly_white")
    return fig