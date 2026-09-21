# Relatório — Caatinga.AI (Sprint 1)

**Matrícula-semente:** 24114028 · **Pomar:** 12×12 · **Ordem de expansão dos vizinhos:** Norte, Sul, Oeste, Leste (N, S, O, L), fixa em todas as estratégias.

---

## Parte 1 — O agente antes do código

### 1.1 Ficha PEAS

| Componente | Descrição |
|---|---|
| **Performance (P)** | Custo total do caminho percorrido, em unidades de talhão-custo (soma dos custos de entrada), **mais** o número de talhões suspeitos deixados sem inspecionar dentro da janela de 6 horas de bateria. Métrica composta e mensurável: `P = custo_da_rota + λ · talhões_suspeitos_não_inspecionados`. |
| **Environment (E)** | O pomar 12×12 (grade de talhões `.`, `~`, `#`), o portão (0,0), o ponto de coleta (11,11) e os talhões suspeitos apontados pelo sensor óptico. |
| **Actuators (A)** | Os quatro movimentos ortogonais (mover Norte/Sul/Leste/Oeste); o disparo do sinalizador que marca um talhão como "suspeito" para inspeção humana. |
| **Sensors (S)** | O sensor óptico de detecção de pragas (com sensibilidade e taxa de falso positivo conhecidas) e a leitura do tipo de talhão vizinho (carreador, solo encharcado, bloqueado) antes de se mover para ele. |

### 1.2 Classificação do ambiente (seis dimensões)

| Dimensão | Classificação | Frase do cenário que sustenta |
|---|---|---|
| Observável | **Totalmente observável** (discutível) | O enunciado descreve a grade inteira como conhecida ("O pomar é uma grade de 12×12 talhões... Cada talhão é de um dos três tipos"), sugerindo mapa completo dado de antemão. |
| Determinístico | **Determinístico** para o deslocamento; **estocástico** para a detecção | O custo de entrar em um talhão é fixo pela tabela; já o sensor tem sensibilidade e taxa de falso positivo, isto é, uma mesma condição real pode gerar leituras diferentes. |
| Episódico | **Sequencial** | A decisão de por onde seguir agora afeta as opções (e o custo) dos passos seguintes — não há independência entre "episódios" de movimento. |
| Estático | **Estático** (discutível) | Nada no enunciado indica que o pomar muda enquanto o agente se move; mas pragas e solo encharcado podem mudar com o tempo real de inspeção, o que tornaria o ambiente dinâmico se o percurso for longo. |
| Discreto | **Discreto** | Estados (talhões), ações (4 direções) e o tempo (passos) são todos contáveis/enumeráveis. |
| Agente único | **Agente único** | Só há um agente descrito percorrendo o pomar; não há outros agentes competindo ou cooperando no cenário. |

**As duas dimensões discutíveis:** *Observável* e *Estático*.
- Para **Observável**, falta o enunciado dizer explicitamente se o agente conhece o mapa completo *antes* de começar (busca offline, o que fizemos) ou se ele só enxerga os talhões vizinhos ao se mover (busca online/parcialmente observável). Assumimos a primeira leitura porque a Parte 2 pede a formulação clássica de busca com grafo conhecido.
- Para **Estático**, falta saber quanto tempo o agente leva para atravessar o pomar em relação à velocidade com que solo encharcado ou pragas mudam de estado. Se a travessia dura minutos e o ambiente muda em dias, é estático o suficiente; se pragas se espalham durante o próprio percurso, é dinâmico.

### 1.3 Tipo de agente

**Agente baseado em utilidade.** Ele não apenas persegue um objetivo binário (chegar ao ponto de coleta), mas precisa comparar rotas com *diferentes custos* (carreador vs. solo encharcado) e, na Parte 3.4, decidir quais talhões inspecionar sob restrição de bateria — uma escolha que exige medir o valor relativo de alternativas (uma função de utilidade), não apenas testar se um estado é ou não objetivo. Um agente baseado em objetivos simples resolveria "chegar ao destino"; aqui a nota da atividade inteira gira em torno de *quão bom* é o caminho, o que só faz sentido com uma função de utilidade explícita.

### 1.4 Métrica perversa

**Métrica proposta (perversa):** "minimizar o número de talhões marcados como suspeitos por semana" — parece razoável para o cliente (menos alertas = sensor "mais preciso").

**Comportamento ruim que o agente aprenderia:** se o agente (ou o time que ajusta o limiar do sensor) for avaliado só por essa métrica, a forma mais fácil de otimizá-la é **subir o limiar de disparo do sensor até quase nunca marcar nada** — inclusive talhões realmente infestados, especialmente nas bordas do pomar onde o custo de deslocamento até o talhão é maior. O comportamento concreto: o agente passaria a ignorar sinais fracos justamente nos talhões `~` (solo encharcado), que são também os mais caros de visitar — juntando os dois incentivos (menos alerta + menos deslocamento caro), o agente aprenderia a "não olhar" para a região mais cara e mais suscetível a pragas do pomar.

**Correção:** trocar a métrica por algo como "custo total esperado de manejo" = custo de falsos negativos não tratados (praga que se espalhou) + custo de deslocamento + custo de falsos positivos investigados à toa — nunca otimizar apenas o número de alertas isoladamente.

---

## Parte 2 — Formulação e busca cega

### 2.1 Componentes do problema de busca

| Componente | Definição para o Caatinga.AI |
|---|---|
| Estado inicial | `(0, 0)` — o portão |
| Ações | `{Norte, Sul, Oeste, Leste}`, válidas se a célula vizinha existe na grade e não é `#` |
| Modelo de transição | `resultado((i,j), a)` move para a célula ortogonal correspondente, se ela não for bloqueada |
| Teste de objetivo | `estado == (11, 11)` |
| Custo do caminho | Soma dos custos de entrada nas células visitadas (`1` para `.`, `4` para `~`; o talhão inicial não conta) |

**Número de estados:** o espaço de estados é o conjunto de talhões **não bloqueados** da grade (um talhão bloqueado nunca é um estado alcançável, porque a ação de entrar nele é inválida). Para a semente 24114028: grade 12×12 = 144 talhões, dos quais **23 são bloqueados (`#`)**, restando **121 estados possíveis**.

### 2.2 Tabela de resultados (BFS, DFS, UCS)

| Estratégia | Custo da rota | Nº de passos | Nós expandidos | Fronteira máx. | Rota é ótima em custo? |
|---|---:|---:|---:|---:|:---:|
| BFS | 46 | 22 | 119 | 13 | Não |
| DFS | 75 | 42 | 48 | 34 | Não |
| UCS | 36 | 24 | 116 | 12 | **Sim** |

(Reproduzível com `python src/buscas.py 24114028`.)

### 2.3 Por que a BFS custou mais caro com menos passos

Não é um bug: a BFS foi projetada para achar a rota com o **menor número de passos**, e ela cumpre exatamente isso — 22 passos contra os 24 da UCS. A hipótese da Aula 03 violada é a de que **BFS só é ótima em custo quando todos os passos têm o mesmo custo (custo uniforme por aresta)**. No nosso pomar, entrar num talhão custa `1` ou `4`, então o caminho com menos arestas não é necessariamente o mais barato: a BFS encontrou um atalho de 22 talhões que passa por mais células de solo encharcado (`~`, custo 4), enquanto a UCS aceitou dois passos a mais para evitar essas células caras e minimizar o custo total.

### 2.4 Escalabilidade — aumentando n até a falha

Aumentamos `n` (mantendo a mesma lógica de geração, mesma semente) e medimos tempo de execução de BFS, DFS e UCS:

| n | BFS | DFS | UCS |
|---:|---:|---:|---:|
| 12 | 0,00 s | 0,00 s | 0,00 s |
| 100 | 0,02 s | 0,00 s | 0,02 s |
| 600 | 0,78 s | 0,60 s | 1,10 s |
| 1.000 | 2,63 s | 2,13 s | 3,58 s |
| 2.000 | 11,68 s | 0,12 s* | 16,70 s |
| 3.000 | 27,45 s | — | 41,88 s |
| **4.000** | **processo morto (`Killed`, código 137)** | — | — |

\* Em `n=2000` a DFS terminou muito rápido (0,12 s) porque, por sorte da semente, o primeiro caminho encontrado pela ordem N,S,O,L era curto — isso não indica que a DFS "escale melhor": em outras sementes/tamanhos ela também explode.

**Onde e como falhou:** em `n = 4000` (16 milhões de talhões) o processo foi **morto pelo sistema operacional por estouro de memória** (não foi estouro de pilha nem timeout de 60 s — a UCS em `n=3000` ainda rodava em 42 s, abaixo do limite). O motivo é que nossa implementação faz **busca em grafo** (mantém um conjunto de visitados/fechados e os dicionários `custo_ate` e `veio_de` para evitar reexpandir estados) — isso evita o laço infinito citado na armadilha nº 1, mas custa **espaço O(n²)**, pois o número de estados é proporcional ao número de talhões. Com `n=4000`, o espaço de estados chega a ~16 milhões, e cada estado ocupa múltiplas estruturas de dados Python (tuplas, entradas de heap, contadores) da ordem de algumas centenas de bytes — a soma passa da memória disponível no ambiente de execução.

**Relação com a fórmula da Aula 03:** para busca em árvore, a complexidade de espaço é `O(b^d)`; aqui, como fazemos busca em **grafo** com fator de ramificação `b=4` fixo mas grafo finito e cíclico, a cota relevante não é exponencial em `d`, e sim **O(|V|) = O(n²)** (número de vértices do grafo), porque o conjunto de fechados/visitados nunca guarda mais que um estado por talhão. Isso explica por que a falha ocorreu por memória (crescimento quadrático em `n`) e não por explosão exponencial de profundidade.

---

## Parte 3 — Busca informada

### 3.1 Tabela A* com as três heurísticas

| Heurística | Custo da rota | Nós expandidos | Admissível? |
|---|---:|---:|:---:|
| h1 = 0 | 36 | 116 | Sim (trivialmente) |
| h2 = Manhattan | 36 | 75 | **Sim** (prova em 3.2) |
| h3 = 4×Manhattan | 40 | 25 | **Não** (contraexemplo em 3.2) |

### 3.2 Prova/contraexemplo de admissibilidade

**h2 é admissível:** o custo mínimo possível para entrar em qualquer talhão do pomar é `1` (carreador firme, `.`). A distância de Manhattan `h2(n)` conta o número mínimo de movimentos ortogonais até o objetivo, ignorando bloqueios. Como cada movimento custa **no mínimo** 1, o custo real de qualquer caminho até o objetivo é sempre `≥ 1 × (nº mínimo de movimentos) = h2(n)`. Logo `h2(n) ≤ h*(n)` para todo estado `n`, que é exatamente a definição de heurística admissível.

**h3 superestima (não é admissível):** tomando o estado `(0,0)` (o próprio portão) do nosso pomar (semente 24114028): a distância de Manhattan até `(11,11)` é `22`, então `h3(0,0) = 4 × 22 = 88`. O custo real mínimo até o objetivo (calculado por Dijkstra a partir do objetivo) é `36`. Como `88 > 36`, `h3` superestima o custo restante nesse talhão — viola `h(n) ≤ h*(n)` e portanto **não é admissível**.

### 3.3 Comparando h3 com a UCS

Neste pomar, `custo(h3) = 40 > custo(UCS) = 36` — **ficou maior**, então:

- **Perda percentual:** `(40 − 36) / 36 ≈ 11,1%` de rota mais cara que a ótima.
- **Nós "comprados" com essa perda:** UCS expandiu 116 nós; h3 expandiu apenas 25 — uma redução de **91 nós (≈ 78% a menos)** pelo preço de 11,1% de rota mais cara.

**Isso prova que h3 é admissível?** Não — encontrar, por acaso, um caso em que o custo bate ou fica só um pouco pior não prova admissibilidade nem consistência. Admissibilidade é uma propriedade que precisa valer **para todo estado do espaço de busca**, provada (ou refutada) em geral, como fizemos em 3.2 com o contraexemplo em `(0,0)`. Um único pomar em que o resultado "parece razoável" não garante nada sobre outros pomares ou outros pontos de partida.

**Quando vale a pena trocar otimalidade por velocidade:** quando o **custo de calcular a rota** (tempo de CPU, latência para o agrônomo receber a instrução) é caro em relação ao **custo de percorrer alguns talhões extras**. Uma condição verificável: *se o tempo de planejamento tiver de ficar abaixo de, por exemplo, 200 ms por consulta (para caber numa janela de decisão em campo, como um app do agrônomo que precisa responder no ato), e a diferença de custo entre a rota heurística e a ótima for menor que o valor de uma inspeção perdida por atraso, então compensa usar h3 em vez de UCS/h2.*

### 3.4 Busca local — escolha de K talhões (K=15)

**Modelagem:**
- **Estado:** um conjunto de 15 talhões livres (não bloqueados) do pomar.
- **Vizinhança:** trocar (swap) um talhão do conjunto por outro talhão livre fora dele.
- **Função objetivo:** `soma_risco(estado) − 0,5 × custo_percurso_guloso(estado)`, onde `risco('~') = 3`, `risco('.') = 1` (solo encharcado retém mais umidade e é associado a maior risco de praga) e `custo_percurso_guloso` aproxima, por um tour guloso do vizinho mais próximo a partir do portão, o deslocamento necessário para visitar os 15 talhões dentro das 6 horas de bateria.

**Resultado de 30 execuções cada:**

| Algoritmo | Média | Desvio-padrão | Melhor valor |
|---|---:|---:|---:|
| Subida de encosta | 33,67 | 1,62 | 36,00 |
| Têmpera simulada | 30,27 | 2,06 | 34,50 |

**Por que aceitar piora ajuda (mesmo quando, como aqui, a subida de encosta teve média maior):** a Aula 04 explica que aceitar uma piora *temporária* com probabilidade `exp(Δ/T)` permite escapar de ótimos locais — planaltos ou vales onde toda troca de um único talhão piora a função objetivo, mas que não são o melhor conjunto de 15 talhões possível. Nos nossos 30 resultados isso aparece nos casos em que a têmpera simulada aceitou um estado pior no meio da execução e, algumas iterações depois, encontrou um valor final acima da média de outras execuções (a variação maior — desvio 2,06 contra 1,62 da subida de encosta — é o próprio sinal empírico de que ela está explorando vales que a subida de encosta nunca visitaria, porque a subida de encosta para assim que nenhuma troca única melhora).

Neste pomar específico, a subida de encosta obteve média mais alta — resultado honesto e explicável: com `K=15` e a função objetivo escolhida, a paisagem de busca aparenta ser suficientemente "lisa" (poucos ótimos locais profundos) para que subir direto ao melhor vizinho, repetidas vezes a partir de pontos aleatórios, já encontre soluções boas na maioria das 30 tentativas — enquanto a têmpera simulada, com resfriamento fixo em 800 iterações, às vezes não teve tempo de reconvergir depois de aceitar uma piora. Isso não invalida a ideia da Aula 04; mostra que a vantagem da têmpera simulada depende da paisagem do problema e dos parâmetros de resfriamento, algo que vale a pena declarar como limitação.

### Bônus — Liga de IA (contraexemplo DFS)

Grade 8×8 construída à mão (`src/bonus_dfs.py`):

```
. ~ ~ ~ ~ ~ ~ ~
. # # # # # # ~
. # # # # # # ~
. # # # # # # ~
. # # # # # # ~
. # # # # # # ~
. # # # # # # ~
. . . . . . . .
```

- **Rota devolvida pela DFS:** linha 0 inteira, depois coluna 7 — custo **53**, 14 passos.
- **Rota ótima (UCS):** coluna 0 inteira, depois linha 7 — custo **14**, 14 passos.
- **Razão:** `53 / 14 ≈ 3,79×` — mais que o dobro do ótimo.

**Por que funciona:** a ordem de expansão declarada (N, S, O, L) empilha `Sul` antes de `Leste` a partir de `(0,0)`, mas como a pilha é LIFO, o topo (`Leste`) é desempilhado primeiro. A DFS então mergulha inteiramente no corredor caro (linha 0 + coluna 7, todo em `~`), que é o único caminho alcançável por ali (o miolo do 8×8 está todo bloqueado), e alcança o objetivo sem nunca voltar para tentar o corredor barato que sai para o Sul. Não é sorte: o corredor caro foi desenhado para não ter nenhum desvio, obrigando a DFS a percorrê-lo até o fim.

---

## Parte 4 — Regras e incerteza

**Parâmetros do sensor (matrícula 24114028):** `prevalência = 0,0204`, `sensibilidade = 0,99`, `taxa de falso positivo = 0,03`, `talhões por semana = 2000`.

### 4.1 Mini sistema especialista

Regras (`src/especialista.py`):

```
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
```

Exemplo de saída do encadeamento para trás (caso 1 — armadilha positiva, solo úmido, 20 dias sem pulverizar, perto de reservatório):

```
Objetivo: inspecionar_prioridade_alta_hoje -> PROVADO
Cadeia de regras usada (por que concluí isso):
  R1: SE armadilha_positiva E umidade_alta E dias_desde_pulverizacao>14 ENTAO inspecionar_prioridade_alta
  R5: SE inspecionar_prioridade_alta E talhao_proximo_reservatorio ENTAO inspecionar_prioridade_alta_hoje
```

### 4.2 Quebrando a própria base

**Caso legítimo mal classificado:** um talhão com `folhas_amareladas = verdadeiro` e `umidade_alta = verdadeiro`, mas cuja causa real é **deficiência de nitrogênio** (não fungo) — comum em solo encharcado, que lava nutrientes do solo. A base atual conclui `risco_fungico` (R3) e, se `dias_desde_pulverizacao > 21`, escala para `inspecionar_prioridade_alta` (R4), desperdiçando uma inspeção fitossanitária cara para um problema nutricional.

**Traço antes da correção:**
```
Objetivo: inspecionar_prioridade_alta -> PROVADO
  R3: SE folhas_amareladas E umidade_alta ENTAO risco_fungico
  R4: SE risco_fungico E dias_desde_pulverizacao>21 ENTAO inspecionar_prioridade_alta
```

**Regra corretiva** (sem contradizer as demais — apenas adiciona uma condição extra a R3):
```
R3': SE folhas_amareladas E umidade_alta E NAO padrao_foliar_uniforme
     ENTAO risco_fungico
```
(`padrao_foliar_uniforme` é verdadeiro quando o amarelamento está espalhado por igual pela copa — sinal típico de deficiência nutricional, diferente das manchas irregulares causadas por fungo.)

**Traço depois da correção** (mesmo talhão, agora com `padrao_foliar_uniforme = verdadeiro`):
```
Objetivo: inspecionar_prioridade_alta -> NAO PROVADO
  (R3' falha: padrao_foliar_uniforme é verdadeiro, então risco_fungico não é provado)
```

### 4.3 Bayes com os parâmetros da semente

**(a)** `P(infestado | positivo) = (0,99 × 0,0204) / (0,99 × 0,0204 + 0,03 × (1 − 0,0204)) ≈ 0,4073` (**40,73%**).

**(b)** A cada 100 alertas do sistema, cerca de **59,3** serão falsos (`1 − 0,4073 = 0,5927`).

**(c)** Com `talhões_por_semana = 2000`: alertas totais esperados por semana ≈ **99,2**; alertas falsos por semana ≈ **58,8**. A 12 minutos por inspeção, isso dá `58,8 × 12 / 60 ≈` **11,8 horas por semana** perseguindo alertas falsos.

**(d)** Aumentando a sensibilidade para 99,9% e mantendo a taxa de falso positivo em 3%: `PPV_novo ≈ 0,4095` (**40,95%**) — uma melhora de menos de **0,3 ponto percentual**. **O problema não melhora de forma relevante**, porque com prevalência baixa (2,04%) é a **taxa de falso positivo** que domina o denominador da fórmula de Bayes, não a sensibilidade. O parâmetro que valeria a pena mexer de fato é a **taxa de falso positivo** (reduzi-la, por exemplo via um segundo teste de confirmação — ver auditoria da afirmação 4 na Parte 5), não a sensibilidade, que já está bem alta.

### 4.4 A regra que salva o modelo

**Decisão que deve ficar em regra explícita:** a decisão de **aplicar defensivo agrícola em talhões próximos a corpos d'água/reservatórios** nunca deve vir de um modelo aprendido — deve ser uma regra explícita e auditável do tipo "SE `talhao_proximo_reservatorio` ENTÃO `proibir_aplicacao_defensivo_X`" (ou exigir aprovação humana). **Justificativa:** essa é uma decisão com implicação legal/ambiental direta (contaminação de recursos hídricos); a cooperativa precisa poder mostrar, a qualquer auditor, **exatamente qual condição levou à decisão** — algo que um modelo estatístico "caixa-preta" não garante da mesma forma que uma regra `SE...ENTÃO` explícita e rastreável.

---

## Parte 5 — Auditoria do laudo do fornecedor

| # | Afirmação | Veredito | Justificativa (com número medido) |
|---|---|---|---|
| 1 | "A* com h=4×Manhattan é comprovadamente ótimo porque A* é ótimo." | **Incorreta** | A otimalidade do A* depende da heurística ser **admissível**; provamos em 3.2 que `h3 = 4×Manhattan` **não é** admissível (em `(0,0)`, `h3=88 > custo real=36`). No nosso próprio pomar, a rota de h3 custou **40**, 11,1% mais cara que o ótimo (**36**, UCS) — prova empírica de que a garantia de otimalidade não vale para essa heurística. |
| 2 | "Substituir BFS por A* reduziu o custo em 38%, o que demonstra que a heurística melhora a qualidade da solução." | **Parcialmente correta** | A*(h2) de fato encontrou uma rota mais barata que a BFS (36 vs. 46 no nosso pomar, ≈22% de redução) — mas isso é esperado **de qualquer estratégia ótima em custo** (UCS chega ao mesmo custo 36 sem heurística nenhuma). A queda de custo comprova que BFS não é ótima em custo uniforme (ver 2.3), **não** que a heurística por si melhora a "qualidade" — quem melhora a otimalidade é o critério de expansão por custo (UCS/A*); a heurística só acelera a busca, reduzindo nós expandidos (no nosso caso, de 116 para 75), sem mudar o custo final da rota ótima. |
| 3 | "Sensibilidade de 99% implica que 99% dos talhões apontados estão de fato infestados." | **Incorreta** | Confunde sensibilidade com **valor preditivo positivo**. Com os nossos parâmetros medidos (prevalência 2,04%, FPR 3%), `P(infestado\|positivo) ≈ 40,7%` (Parte 4.3a) — bem longe de 99%. A prevalência baixa domina o resultado, exatamente como a armadilha nº 5 do enunciado avisa. |
| 4 | "Aplicar o teste duas vezes e exigir dois positivos eleva a confiança do alerta para mais de 99%." | **Parcialmente correta** | A direção está certa — exigir dois positivos independentes reduz tanto o falso-positivo (`0,03² = 0,0009`) quanto a sensibilidade efetiva (`0,99² = 0,9801`, já que os dois testes têm de acertar). Recalculando: `PPV = (0,9801×0,0204)/(0,9801×0,0204 + 0,0009×0,9796) ≈ 0,958` (95,8%) — uma melhora enorme frente aos 40,7% originais, mas **não acima de 99%** como o laudo afirma categoricamente, e só vale **se os dois testes forem estatisticamente independentes** (o que raramente é verdade para o mesmo sensor aplicado duas vezes seguidas no mesmo talhão, sujeito às mesmas condições de solo e luz — erros correlacionados fariam o ganho real ser bem menor). |
| 5 | "Como o pomar é estático e totalmente observável, a DFS é suficiente." | **Incorreta** | Ser estático e observável não tem relação com a **qualidade da rota** devolvida pela DFS. O nosso próprio contraexemplo (Bônus) mostra a DFS devolvendo uma rota **3,79× mais cara** que a ótima no mesmo tipo de ambiente estático/observável — a DFS "funciona" (encontra *um* caminho), mas não otimiza custo, que é a métrica de desempenho real do cliente (Parte 1.1). |

**Recomendação à diretoria:** recomendo **contratar com ressalvas**. O laudo mistura afirmações tecnicamente corretas (a ideia de dupla confirmação do sensor) com alegações de otimalidade e de precisão do sensor que os nossos próprios experimentos, com a mesma matrícula-semente, refutam numericamente (h3 não ótima; PPV real de ~41%, não 99%). A condição técnica que mudaria a resposta: o fornecedor reapresentar a proposta trocando o planejador de rota por UCS ou A* com heurística **admissível** (h2), e reportando o PPV real calculado com a prevalência medida em campo, não apenas a sensibilidade do sensor.

---

## Nota metodológica

Este relatório foi produzido com apoio de um assistente de IA para a implementação dos algoritmos e a redação inicial das análises. Os números de todas as tabelas foram gerados executando o código deste repositório com a matrícula-semente 24114028 (não foram inventados). Detalhes do uso de IA e uma verificação crítica estão em [`ANEXO_IA.md`](ANEXO_IA.md) — **a dupla deve revisar cada seção deste relatório, rodar o código com a própria matrícula final e estar pronta para defender qualquer número na arguição**, conforme exigido no enunciado (Seção 10).
