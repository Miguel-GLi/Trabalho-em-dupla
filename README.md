# Caatinga.AI - Sprint 1

**Disciplina:** Inteligência Artificial — Prof. Ronierison Maciel — UniRios — 2026.2

**Dupla:**
- Miguel Gomes de Lima — matrícula 241.14.028
- Lucas Gomes Santos — matrícula 241.14.074

**Matrícula usada como semente:** `24114028` (integrante mais velho da dupla)
> ⚠️ Confirme se `24114028` é a matrícula correta antes de gerar a versão final —
> este número foi digitado no chat como `241.14.028` e os pontos foram
> interpretados como separadores de milhar.

## O que este projeto faz

O Caatinga.AI é um agente que planeja rotas em um pomar de manga de 12×12
talhões, comparando estratégias de busca cega (BFS, DFS, UCS) e informada
(A* com três heurísticas). Além disso, o projeto modela a escolha de quais
talhões inspecionar sob restrição de bateria (busca local), um mini sistema
especialista para decisão de manejo (encadeamento para trás) e o cálculo
bayesiano de confiabilidade do sensor óptico de pragas.

## Como rodar

- Python 3.10+
- Instalação:
  ```bash
  pip install -r requirements.txt
  ```
- Execução (gera `resultados/pomar.txt`, `resultados/resultados.csv` e
  `resultados/grafico.png` do zero):
  ```bash
  python src/main.py 24114028
  ```
- Demais partes, individualmente:
  ```bash
  python src/busca_local.py 24114028     # Parte 3.4 (subida de encosta / têmpera simulada)
  python src/especialista.py             # Parte 4.1/4.2 (sistema especialista)
  python src/bayes.py 24114028           # Parte 4.3 (Bayes)
  python src/bonus_dfs.py                # Bônus Liga de IA (contraexemplo DFS)
  ```

## Tabela-resumo dos resultados (matrícula 24114028)

| Estratégia    | Heurística       | Custo | Passos | Nós expandidos | Fronteira máx. | Ótima em custo? |
|---------------|------------------|------:|-------:|----------------:|----------------:|:----------------:|
| BFS           | —                |    46 |     22 |             119 |              13 | Não |
| DFS           | —                |    75 |     42 |              48 |              34 | Não |
| UCS           | —                |    36 |     24 |             116 |              12 | Sim |
| A*            | h1 = 0           |    36 |     24 |             116 |              12 | Sim |
| A*            | h2 = Manhattan   |    36 |     24 |              75 |              20 | Sim |
| A*            | h3 = 4×Manhattan |    40 |     22 |              25 |              16 | Não (h3 não é admissível) |

Detalhes, provas e discussão de cada número estão em [`RELATORIO.md`](RELATORIO.md).

## Ordem de expansão dos vizinhos

Norte, Sul, Oeste, Leste (`N, S, O, L`) — fixa em todas as estratégias
(ver `src/buscas.py`, lista `VIZINHOS`).

O A* implementado **não reabre nós** (usa conjunto de fechados clássico).
Isso é seguro para h1 e h2, que são consistentes; para h3 (não admissível),
a busca não trava, mas pode devolver rota sub-ótima — é exatamente o que a
Parte 3.3 do relatório discute.

## Mapa do repositório

| Arquivo | O que resolve |
|---|---|
| `src/gerador_pomar.py` | Gerador do pomar e dos parâmetros do sensor (intacto, não alterado) |
| `src/buscas.py` | BFS, DFS, UCS e A* com os quatro contadores instrumentados |
| `src/busca_local.py` | Subida de encosta e têmpera simulada para escolha de K talhões (Parte 3.4) |
| `src/especialista.py` | Sistema especialista com encadeamento para trás (Parte 4.1/4.2) |
| `src/bayes.py` | Cálculos bayesianos de confiabilidade do sensor (Parte 4.3) |
| `src/bonus_dfs.py` | Contraexemplo construído (Liga de IA — bônus) |
| `src/main.py` | Comando único: gera `pomar.txt`, `resultados.csv` e `grafico.png` |
| `RELATORIO.md` | Relatório completo com todas as tabelas e discussões (Partes 1 a 5) |
| `ANEXO_IA.md` | Anexo obrigatório de uso de IA (Parte 6) |

## Limitações conhecidas

- A busca local (Parte 3.4) usa uma função-objetivo definida pela dupla
  (risco por tipo de terreno menos custo de deslocamento aproximado por
  tour guloso) — não há "gabarito" único para essa modelagem; a escolha
  está justificada em `RELATORIO.md`.
- O teste de escalabilidade (Parte 2.4) foi feito neste ambiente de
  desenvolvimento; o ponto de falha exato (n em que ocorre) pode variar
  alguns milhares de talhões conforme a máquina usada na correção,
  porque depende da memória RAM disponível.
- Os nomes e matrículas da dupla no cabeçalho deste README e do
  `RELATORIO.md` estão como placeholder e precisam ser preenchidos antes
  da entrega.
