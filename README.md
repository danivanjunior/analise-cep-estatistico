# Controle Estatístico de Processo (CEP / SPC) — Usinagem CNC

Repositório destinado a monitorar o diâmetro de eixos de precisão em aço inox usinados em linha CNC, aplicando Controle Estatístico de Processo (CEP / SPC), regras de detecção de causas especiais e visualizações interativas com Python e Plotly.

## O problema

Eu criei este projeto pensando em uma linha de usinagem CNC de eixos de precisão em aço inox, onde o diâmetro alvo é **10,00 mm** e a tolerância de engenharia fica entre **9,70 mm** e **10,30 mm**. Durante os turnos, o desgaste natural da ferramenta de corte, mudanças de temperatura do fluido refrigerante e trocas de lote de matéria-prima costumam causar subidas ou quedas graduais nas medidas, além de picos fora do padrão.

O maior gargalo acontece quando um desvio só é percebido lá na inspeção final do lote: nesse ponto, o material já virou sucata ou exige retrabalho, o que encarece a produção e atrasa entregas. Queria sair de um acompanhamento manual e atrasado para um fluxo que lesse as medições, calculasse os limites estatísticos do processo, apontasse padrões suspeitos cedo e gerasse gráficos claros para ajudar na tomada de decisão.

## Resultados e impacto no negócio

Com este projeto, organizei a análise em etapas simples e reutilizáveis, indo da leitura do CSV até a geração de gráficos interativos e de um arquivo consolidado com os alertas:

- **Detecção antecipada de desvios:** além de checar pontos fora dos limites de 3 Sigma (`UCL` e `LCL`), o código identifica tendências contínuas e deslocamentos em relação à média, ajudando a notar desgaste de ferramenta ou variação de processo antes que o lote inteiro seja comprometido.
- **Visão por turno e máquina:** os resumos e gráficos comparam o comportamento das medições entre turnos e máquinas CNC, facilitando entender onde o processo está mais estável ou onde há maior dispersão.
- **Apoio prático para a qualidade:** os gráficos interativos em Plotly e a tabela de saída (`outputs/resultado_cep.csv`) dão visibilidade rápida para ajustes preventivos, reduzindo o risco de sucata, retrabalho e atrasos na linha.

| amostra | timestamp | turno | maquina | diametro_mm | lsl | usl | amplitude_movel | alertas | fora_de_controle |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **1** | 2026-11-20 06:10:00 | Manha | CNC-01 | 10.02 | 9.70 | 10.30 | — | Normal | **False** |
| **11** | 2026-11-20 11:10:00 | Manha | CNC-01 | **10.36** | 9.70 | 10.30 | 0.18 | Acima do UCL (3 Sigma)  | **True** |
| **17** | 2026-11-20 16:10:00 | Tarde | CNC-01 | **9.62** | 9.70 | 10.30 | 0.38 | Abaixo do LCL (3 Sigma)  | **True** |
| **25** | 2026-11-21 00:10:00 | Noite | CNC-02 | **10.10** | 9.70 | 10.30 | 0.01 | Sequencia de 7+ pontos no mesmo lado da media  | **True** |
| **30** | 2026-11-21 02:40:00 | Noite | CNC-02 | 9.99 | 9.70 | 10.30 | 0.02 | Normal  | **False** |

