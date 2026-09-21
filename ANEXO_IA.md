# Anexo de uso de IA

> ⚠️ Este arquivo precisa ser completado/revisado pela dupla com honestidade —
> um anexo genérico ou fabricado **zera as Partes 5 e 6** (Seção 8 do
> enunciado). O que está abaixo é um ponto de partida real, baseado na sessão
> de desenvolvimento; adapte com a experiência de vocês dois, incluindo
> qualquer erro que vocês mesmos encontrarem ao rodar e revisar o código.

## A.1 — Ferramentas usadas e em que partes

Usamos o Claude (Anthropic) como assistente de IA para:
- Implementar `gerador_pomar.py` (cópia fiel do enunciado, sem alterações).
- Implementar `buscas.py` (BFS, DFS, UCS, A*) e validar os números contra a
  caixa de aferição do enunciado (matrícula fictícia 20231045) antes de rodar
  com a matrícula real da dupla.
- Implementar `busca_local.py`, `especialista.py` e `bayes.py`.
- Redigir a primeira versão do `RELATORIO.md` a partir dos números gerados
  pelo próprio código.

## A.2 — Dois prompts na íntegra (copiar e colar)

**Prompt 1:**
> "241.14.028" (fornecendo a matrícula-semente após a IA pedir esse dado
> para gerar o pomar e come.çar a implementação)

**Resposta recebida (resumo):** a IA gerou o pomar com `gerar_pomar(24114028)`,
implementou BFS/DFS/UCS/A* e **validou o código contra a caixa de aferição do
enunciado antes de confiar nos resultados** — rodando primeiro com a
matrícula fictícia `20231045` e comparando com os valores de referência
(custo UCS=34, custo BFS=55, passos BFS=22, nós UCS≈112, nós A*-Manhattan≈93).

*(Substitua por um dos prompts reais que a dupla efetivamente trocou com a
ferramenta de IA que usarem, copiado e colado sem edição.)*

**Prompt 2:**
> *(A dupla deve colar aqui um segundo prompt real usado durante o trabalho —
> por exemplo, um pedido de ajuste no gráfico, uma dúvida sobre a prova de
> admissibilidade de h2, ou um pedido de revisão do sistema especialista —
> com a resposta recebida.)*

## A.3 — Um erro, imprecisão ou invenção do assistente (com evidência experimental)

**O que descobrimos ao rodar o código de verdade (Parte 3.4 — busca local):**
antes de rodar as 30 execuções, a expectativa (baseada na Aula 04) era de que
a têmpera simulada, por aceitar piora de propósito, teria uma **média maior**
que a subida de encosta. Ao rodar de fato com a matrícula 24114028, o
resultado medido foi o oposto: subida de encosta obteve média **33,67**
contra **30,27** da têmpera simulada.

Isso não é bem um "erro" de fato inventado pelo assistente — o código está
correto e os números foram gerados pela própria execução — mas é um exemplo
real de **expectativa desalinhada com o resultado empírico** que só ficou
claro depois de rodar o experimento e não apenas ler a explicação teórica:
o assistente explicou corretamente *por que* aceitar piora ajuda em teoria,
mas isso não implica que, para este pomar específico, com `K=15` e os
parâmetros de resfriamento usados (800 iterações, resfriamento 0,995), a
têmpera simulada bateria a subida de encosta na média das 30 execuções.

*(Se, ao revisarem o código com atenção, a dupla encontrar um erro real de
implementação, uma afirmação incorreta do assistente sobre teoria de IA, ou
um número que ele "inventou" sem rodar o código, substituam este exemplo
pelo achado real — é exatamente esse tipo de verificação que o enunciado
pede.)*

## A.4 — O que só se sabe depois de rodar o código

Só depois de rodar as 30 execuções da têmpera simulada e comparar com a
subida de encosta é que ficou claro que a vantagem teórica de "aceitar
piora ajuda a escapar de ótimos locais" **depende da paisagem específica do
problema e dos parâmetros de resfriamento** — algo que nenhuma explicação
teórica, por si só, deixaria evidente sem os números medidos.
