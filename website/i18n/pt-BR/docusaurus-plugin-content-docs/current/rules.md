---
title: Regras
---

# Regras

Cada regra liga e desliga na aba **Regras** de um gerador. Os padrões abaixo valem para um gerador novo.

![Aba Regras, com a fila de revisão e a lista de tópicos ligadas](/img/screens/pt-BR/generator-rules-topics.png)

*Aba Regras, com a fila de revisão e a lista de tópicos ligadas*


| Regra | Padrão | Ajustes | O que faz |
|---|---|---|---|
| **Aumentar aos poucos** | ligada | começar com A, chegar a B em N semanas (2 → 10 em 4) | A quantidade do dia sobe em linha reta de A até B, contando do dia em que o gerador foi criado. Desligada, vale *Cards por dia*. |
| **Só em alguns dias** | desligada | dias da semana | Não gera nos dias desmarcados. |
| **Frear quando acumular** | ligada | limite (30) | Se o baralho de destino tiver mais cards de revisão vencidos que o limite, nada é gerado hoje, e o aviso diz por quê. |
| **Não repetir** | ligada | — | Veja abaixo. |
| **Teto de gasto** | ligada | US$ por mês (2,00) | Soma o custo estimado de **todos** os geradores no mês. Acima do teto, nenhum gerador roda até o mês virar ou você subir o teto. |
| **Aprovar antes de entrar** | desligada | — | Os cards esperam na [fila de revisão](review-queue.md) em vez de ir direto para o estudo. |
| **Reforçar o que você erra** | desligada | a partir de E erros (3), até R por dia (2) | Acha até R notas do baralho que você errou E ou mais vezes e pede cards novos explicando o mesmo assunto de outro jeito. Eles contam na cota do dia e recebem a etiqueta `autocards::reinforcement`. Cada nota de origem é usada uma vez só (etiqueta `autocards::reinforced`). |
| **Seguir uma lista de tópicos** | desligada | um tópico por linha, T por dia (1) | A cada dia pega os próximos T tópicos, em ordem, em vez de a IA escolher. Um tópico só conta como usado se entrou pelo menos um card. Quando a lista acaba, você recebe um aviso e o gerador volta ao tema. Editar ou trocar a lista nunca pula nem repete tópicos, porque os usados são lembrados pelo texto. |

:::info Dia bloqueado conta como feito
Quando *Só em alguns dias*, *Frear quando acumular* ou *Teto de gasto* param um gerador, o dia conta como tratado, e ele não tenta de novo a cada hora. Use **Gerar agora** se quiser cards mesmo assim.
:::

## Não repetir

Antes de chamar a IA, o AutoCards junta a frente de **todas** as notas do baralho de destino, de qualquer tipo, inclusive os cards que você criou antes de instalar o add-on. Também entram os cards que você **descartou** na fila de revisão.

- O prompt recebe as 150 mais recentes como "não repita estes".
- Depois da resposta, um card cai se a frente for igual ou parecida demais (88% de semelhança ou mais) com uma existente ou com outro card do mesmo lote.
- Se o filtro derrubar cards, o AutoCards **não** chama a IA de novo para completar a cota. O registro guarda quantos caíram.

## Outras proteções

- Cards com algum campo vazio, e cards cloze sem a lacuna `{{c1::…}}`, são descartados.
- Se a IA responder sem nenhum card válido, a execução conta como falha e tenta de novo depois.
- Se você fechar o perfil durante a geração, ela para antes de gravar qualquer coisa e não conta o dia.
