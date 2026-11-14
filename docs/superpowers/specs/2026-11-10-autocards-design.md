# AutoCards: desenho do add-on

- **Data:** 10/11/2026
- **Status:** rascunho para aprovação (já com as respostas da revisão de 10/11)
- **Nome:** "AutoCards", definido pelo dono em 14/11/2026.
- **Rascunhos de tela:** [`docs/mockups/`](../../mockups/) (`config-v1.html`, `prompt-v1.html`, `regras-v1.html`). A tela escolhida foi a **B** de `config-v1.html`.

Legenda das decisões, usada em todo o documento:

- **[dono]**: decidido pelo dono do projeto durante a conversa de desenho.
- **[desenho]**: decisão de quem escreveu este documento, que o dono não confirmou item por item. Pode ser contestada.
- **[construtor]**: deixado para quem for planejar e construir.

---

## 1. O que é e por quê

Um add-on do Anki que **cria cards novos todo dia, sozinho, usando IA**. Cada pessoa configura "geradores": receitas que dizem o tema, como o texto deve ser escrito, o formato do card, se tem áudio e que regras seguir. Ao abrir o Anki, o add-on gera a cota do dia de cada gerador e avisa quando termina.

**Por que existe:**

1. **Para o dono, agora.** Ele tem três sistemas separados que geram cards por fora do Anki, via AnkiConnect e timers do systemd (ver o levantamento em `autocards-privado/reference/sistemas-atuais.md`, fora do repositório, ao lado da pasta do projeto). Só o de inglês funciona, justamente o único que não depende de escrita manual. Os três repetem o mesmo código: conector, abertura do Anki e controle de repetição. O add-on substitui os três.
2. **Prática real com LLM.** Montar prompts, lidar com JSON de vários serviços, controlar custo e **medir a qualidade do que a IA gera** é a experiência prática de engenharia de LLM que o dono quer ganhar.
3. **Comunidade e renda extra.** O add-on é publicado de graça para o mundo todo. Depois vêm um curso, ensinando a configurar, e pacotes de geradores prontos por tema, vendidos fora do AnkiWeb (seção 12).

**O que o diferencia** (pesquisa em [`docs/research/2026-11-10-mercado.md`](../../research/2026-11-10-mercado.md)): os add-ons de IA que existem geram cards **quando a pessoa pede**. Nenhum dos encontrados junta estas quatro coisas:

- gerar sozinho todo dia;
- frear quando a pessoa acumula atrasados;
- prompt montado por campos e totalmente editável;
- áudio com o serviço que a pessoa escolher.

## 2. Para quem

1. **O dono**, primeiro usuário. Estuda no PC, com Linux e Anki 26.09.2, e quer que o Anki abra sozinho de manhã.
2. **Usuários do Anki no mundo todo** **[dono]**, que leem a página do add-on em inglês. A maioria não sabe o que é uma chave de API.
3. **Alunos do curso**, em português, que compram para não ter que montar card e áudio à mão.

## 3. Objetivos, não objetivos e anti-objetivos

**Objetivos**

- Gerar cards automaticamente, uma vez por dia por gerador, sem ação do usuário além de abrir o Anki.
- Permitir que qualquer pessoa crie um gerador para qualquer tema, partindo de um modelo pronto, sem saber escrever prompt.
- Permitir que quem sabe edite tudo: cada campo do prompt, formato, áudio e regras.
- Funcionar com qualquer serviço de texto compatível com o formato OpenAI e com vários serviços de áudio.
- Proteger o usuário da avalanche de cards e de gasto inesperado.
- Registrar tudo o que foi gerado, para medir a qualidade.
- Substituir por completo os três sistemas atuais do dono.

**Não objetivos (fora desta versão)**

- Gerar cards a partir de PDF, página web ou arquivo. Fica para depois **[dono]**.
- IA hospedada pelo próprio add-on, sem chave do usuário.
- Funcionar no AnkiDroid ou no AnkiMobile. A geração é só no computador. Os cards gerados sincronizam normalmente.
- Explicar cards durante a revisão, ou conversar com a IA sobre um card.
- Cards de autoria própria, como o `RESPOSTAS.md` do sistema de entrevista. Respostas pessoais continuam sendo escritas à mão no Anki.
- Cópia própria do Anki. É add-on, decisão tomada **[dono]**.

**Anti-objetivos (seria fracasso mesmo funcionando)**

- O usuário abre o Anki e encontra centenas de cards novos. O freio e o "não acumular dias" existem para isso.
- Cards com erro factual entrando sem que o usuário tenha como perceber ou filtrar.
- Gasto com a IA que o usuário não esperava.
- O Anki trava enquanto o add-on gera.
- Um gerador que dá erro quebra os outros, ou impede o Anki de abrir.
- Chave de API vazando num arquivo de gerador exportado.

## 4. Restrições

- **Add-on do Anki, Python.** Roda dentro do Anki. A versão mínima é a 26.09 **[desenho]**; o construtor decide se dá para suportar versões anteriores sem custo.
- **Nada para instalar** **[dono]**. Quem usa o add-on não instala nenhum pacote, programa ou biblioteca além do próprio Anki. O add-on usa só a biblioteca padrão do Python e o que o Anki já traz. Levantamento feito no Anki 26.09.2 (`app_packages`):

  | Necessidade | Usar (já vem no Anki) | Em vez de |
  |---|---|---|
  | HTTP para os serviços de texto e áudio | `requests` / `urllib3` / `certifi` | SDK `openai` |
  | Validar o JSON da IA | `jsonschema` | `pydantic` |
  | WebSocket do Edge TTS | `PyQt6.QtWebSockets` | `edge-tts` + `aiohttp` (partes compiladas) |
  | Segundo plano | tarefas em segundo plano do Anki | timers do systemd |
  | Inserir notas | API interna do Anki | AnkiConnect |

  - Código de terceiros só entra se for Python puro, com licença compatível com AGPL3, copiado para dentro do add-on (por exemplo, a geração do token do Edge, do `edge-tts`, que é LGPL3).
  - Serviços externos, como uma chave de API ou um Ollama local, são **escolha** do usuário, nunca exigência. Sempre há um caminho de custo zero: texto por um serviço com camada grátis ou local, e áudio pelo Edge.
- **Não travar a interface.** Toda chamada de rede roda em segundo plano, usando o mecanismo de tarefas em segundo plano do Anki. A escrita na coleção segue as regras de thread do Anki.
- **Licença AGPL3** **[desenho]**, exigida para add-ons do AnkiWeb, segundo o fórum oficial (ver a pesquisa).
- **Linux, Windows e Mac.** O dono usa Linux, mas o público é mundial.
- **Repositório privado até a publicação** **[dono]**. `docs/reference/` tinha detalhes da máquina e dos estudos do dono. Feito em 14/11/2026: esses documentos saíram do repositório (e do histórico), e só então ele vira público.
- **Interface em inglês, com português como segunda língua** **[dono]**. Todo texto da tela passa por um mecanismo de tradução desde o início.
- **Não depender dos nomes de campo do idioma do Anki.** O sistema de entrevista atual quebraria num Anki em português, porque fixa `Front`/`Back`. Ver seção 7.3.

## 5. Conceitos

| Conceito | O que é |
|---|---|
| **Gerador** | Uma receita de cards: modelo de origem, tema, baralho de destino, campos do prompt, formato, áudio, regras e os serviços que usa. Uma pessoa pode ter vários. |
| **Modelo inicial** | Um gerador pré-preenchido para começar: Idioma, Entrevista técnica, Conceitos ou Em branco. |
| **Serviço** | Uma conexão configurada uma vez só, com endereço, chave e modelo. Há serviços de texto e de áudio. Cada gerador aponta para um serviço de texto e, se tiver áudio, para um de áudio. |
| **Execução** | Uma rodada de um gerador num dia: decide se roda, quantos cards, monta o prompt, chama a IA, filtra, gera o áudio, insere e registra. |
| **Registro** | O histórico de tudo o que foi gerado, com o prompt usado, modelo, custo e o destino de cada card. |

## 6. Como roda

### 6.1 Quando gera

- O Anki abre sozinho, por fora do add-on:
  - na entrada do sistema, por um atalho de inicialização do sistema operacional;
  - às 05:00, por um timer que só abre o Anki se ele estiver fechado.
  - **[dono]** Isso é configuração da máquina dele, não do add-on. Ver a seção 11.
- O add-on gera **ao abrir o perfil** e **confere a cada hora** se o dia virou, para o caso de o Anki ficar aberto de um dia para o outro **[dono]**.
- **Uma vez por dia por gerador.** Cada gerador guarda a data da última execução bem-sucedida.
- **Não acumula dias perdidos** **[dono]**. Ficou três dias sem abrir, gera a cota de um dia só.
- "Dia" segue o horário local do computador **[desenho]**. O construtor avalia se vale usar a virada de dia do Anki (padrão 04:00).
- Os geradores rodam um depois do outro, em segundo plano. Se um falha, os outros seguem. A falha aparece no aviso final e no registro.
- Há também um botão "Gerar agora" por gerador, que ignora a regra de "uma vez por dia" mas respeita as proteções **[desenho]**.

### 6.2 Aviso ao terminar

- Um aviso discreto dentro do Anki, com o total por gerador: "Inglês do dia a dia: 10 novos · Entrevista: 3 novos · Vocabulário: falhou (ver registro)".
- **[desenho]** Uma opção avançada, "Rodar um comando ao terminar", recebe sucesso ou erro e a mensagem. Serve para o dono manter o popup com som que já usa (um script local de aviso).

### 6.3 Uma execução, passo a passo

1. **Checar as regras de bloqueio**, em ordem: dia da semana permitido, freio por atrasados, teto de gasto. Se uma bloqueia, registra o motivo e para, sem chamar a IA.
2. **Calcular a quantidade** do dia: a fixa, ou a da regra "Aumentar aos poucos".
3. **Escolher o conteúdo extra**, se houver:
   - os tópicos do dia, da lista;
   - os cards com mais erros, da regra de reforço.
4. **Montar o prompt** (seção 7.2).
5. **Chamar o serviço de texto** pedindo JSON. Validar a resposta. Se vier inválida, tentar mais uma vez. Se falhar de novo, registrar o erro e parar este gerador.
6. **Filtrar:** descartar cards repetidos (seção 8) e cards com campos vazios.
7. **Gerar o áudio**, se ligado, card a card. Se o áudio de um card falha, o card entra sem áudio e a falha vai para o registro **[desenho]**.
8. **Inserir no Anki**, ou mandar para a fila de aprovação se a regra estiver ligada.
9. **Registrar** tudo (seção 10) e atualizar a data da última execução.

## 7. A tela de configuração

Fica no menu Ferramentas › AutoCards. Lista de geradores à esquerda, com "+ Novo gerador"; o gerador selecionado aparece à direita, em quatro abas **[dono]**. Botões comuns a todas as abas: **Testar**, **Cancelar** e **Salvar**.

**Testar: gerar 1 card de exemplo** usa a configuração atual, ainda não salva, e o serviço escolhido. Mostra o card pronto, com áudio se houver, **sem inserir no Anki**. Fica no registro marcado como teste. É também a forma de checar se a chave funciona.

### 7.1 Aba Básico

- **Modelo inicial**, só ao criar: Idioma, Entrevista técnica, Conceitos ou Em branco. Cada modelo preenche os campos do prompt, o formato e as regras com valores bons para o caso.
- **Sobre o que você quer estudar**: uma frase, que vira o campo "Tema" do prompt.
- **Nível**: básico, intermediário ou avançado.
- **Cards por dia.**
- **Baralho de destino**: escolher um existente ou criar.
- **Serviço de texto** e modelo de IA.
- Para o modelo Idioma: **sua língua** e **língua que você estuda**. Não supor português ↔ inglês **[dono]**.

### 7.2 Aba Prompt

Ver [`prompt-v1.html`](../../mockups/prompt-v1.html), aprovado **[dono]**.

- **Vários campos de texto**, cada um descrevendo um aspecto do card **[dono]**. Os campos padrão são: Papel da IA, Tema, Nível e público, Frente do card, Verso do card, O que evitar, e Exemplos de cards bons.
- Cada campo pode ser **ligado ou desligado** sem perder o texto, e **reordenado** arrastando.
- **"+ Adicionar campo próprio"**, com o nome que a pessoa quiser.
- **Prévia do prompt final**, ao vivo e só leitura: os campos ligados, na ordem da tela, cada um com seu nome como título. Tem um botão Copiar.
- **Bloco fixo no fim**, que o add-on acrescenta e o usuário não edita **[desenho]**:
  - quantos cards gerar;
  - o idioma da resposta, quando fizer sentido;
  - a lista do que já existe (seção 8);
  - os tópicos do dia ou os cards com erros, quando as regras estão ligadas;
  - o formato JSON exato da resposta, derivado do formato do card.
- O texto do bloco fixo é do add-on e vai em inglês para o modelo. O texto dos campos é do usuário, em qualquer idioma.

### 7.3 Aba Formato e áudio

- **Formato do card**: Frente e verso, Frente e verso com cartão invertido, ou Cloze (lacunas).
- **[desenho]** O add-on cria e usa **tipos de nota próprios**, por exemplo "AutoCards Basic", "AutoCards Reversed" e "AutoCards Cloze", com campos de nome fixo: frente, verso, áudio e um campo de contexto opcional. Isso evita depender do nome dos campos em cada idioma do Anki, e permite um modelo de card que já toca o áudio. O construtor decide nomes, modelos de card e estilo.
- **Campo extra "Contexto"**, opcional. É uma frase curta de quando se usa aquilo, como o campo `context` do sistema de inglês atual.
- **Áudio**: liga ou desliga; de qual lado sai o texto do áudio (frente ou verso); serviço de áudio; voz.
- **Botão "Ouvir exemplo"** da voz escolhida.

### 7.4 Aba Regras

Ver [`regras-v1.html`](../../mockups/regras-v1.html), aprovado **[dono]**. Cada regra liga e desliga. Os padrões abaixo valem para um gerador novo; os modelos iniciais podem mudá-los.

| Regra | Padrão | Parâmetros | Comportamento |
|---|---|---|---|
| Aumentar aos poucos | ligada | começar com A, chegar a B em N semanas | Quantidade sobe em linha reta de A até B ao longo de N semanas, contadas da criação do gerador. Com a regra desligada, usa "Cards por dia". |
| Só em alguns dias | desligada | dias da semana | Fora dos dias marcados, não gera. |
| Frear quando acumular | ligada | limite de cards vencidos (padrão 30) | Se o baralho de destino tiver mais vencidos que o limite, não gera hoje e diz por quê no aviso. |
| Não repetir | ligada | sem parâmetros | Ver seção 8. |
| Teto de gasto | ligada | US$ por mês (padrão 2) | Soma o custo estimado do mês (texto mais áudio) de **todos** os geradores **[desenho]**. Ao passar do teto, nenhum gerador roda até o mês virar ou o teto subir. |
| Aprovar antes de entrar (1.1) | desligada | sem parâmetros | Ver 7.5. |
| Reforçar o que você erra (1.1) | desligada | a partir de E erros; até R por dia | Pega até R cards do baralho com E ou mais erros, ainda não usados para reforço, e pede cards novos sobre o mesmo assunto, explicados de outro jeito. Esses cards contam dentro da cota do dia e recebem uma marca de reforço. |
| Seguir uma lista de tópicos (1.1) | desligada | lista, um por linha; T por dia | Pega os próximos T tópicos, em ordem, e manda a IA gerar sobre eles. Quando a lista acaba, avisa e volta a gerar só pelo tema. Os tópicos já usados ficam marcados na lista. |
| Ler de um arquivo ou página | fora desta versão | | Aparece desabilitada, com "em breve", ou não aparece. Decisão do construtor. |

### 7.5 Fila de aprovação (versão 1.1)

- Com "Aprovar antes de entrar" ligada, os cards gerados ficam numa fila, sem entrar no estudo.
- Uma tela "Revisar cards gerados" mostra a fila. Para cada card: **Aceitar**, **Editar e aceitar** ou **Descartar**.
- **[desenho]** O jeito mais simples: inserir as notas já **suspensas** e com uma etiqueta de pendente. Aceitar tira a suspensão e a etiqueta; descartar apaga a nota. O construtor pode escolher outro mecanismo, desde que o card não apareça no estudo antes de ser aceito.
- O resultado de cada card (aceito, editado ou descartado) vai para o registro. É o principal dado de qualidade.

### 7.6 Tela Serviços

Separada dos geradores. Guarda cada conexão uma vez só **[dono]**.

- **Texto**: um único tipo de conexão, o formato OpenAI de chat. Campos: nome, endereço base, chave e modelo padrão. Vem com atalhos prontos que preenchem o endereço: OpenAI, OpenRouter, Ollama (local), LM Studio (local) e Groq. Um serviço local não exige chave.
- **Áudio**: um adaptador por serviço **[dono]**:
  - Edge, grátis, sem chave;
  - formato OpenAI de áudio;
  - ElevenLabs.
  - A 1.0 tem só um deles; os outros chegam na 1.1 (seção 12).
- **Preço**: cada serviço tem um campo de preço, por milhão de tokens para texto e por mil caracteres para áudio. Ele alimenta o teto de gasto e o registro **[desenho]**. Os atalhos vêm com preços preenchidos quando conhecidos, sempre editáveis, com o aviso de que são estimativas.
- **Botão "Testar conexão"** em cada serviço.
- **Configuração guiada do primeiro serviço** (fase 2): quem abre o add-on pela primeira vez sem nenhum serviço vê um passo a passo, com o que é uma chave, link para criar a chave em cada atalho, onde colar e um teste na hora.

## 8. Não repetir

- Antes de chamar a IA, junta o texto da frente das notas que já existem no baralho de destino, em **qualquer** tipo de nota. Isso inclui os cards antigos do dono, criados pelos sistemas atuais.
- Manda para a IA uma parte dessa lista, no bloco fixo, como "não repita estes". **[construtor]** Escolhe quantos itens e quais (os mais recentes, uma amostra), sabendo que baralhos grandes não cabem inteiros no prompt.
- Depois da resposta, descarta os cards cuja frente, normalizada, é igual ou parecida demais com uma existente ou com outra do mesmo lote. **[construtor]** Escolhe o critério de "parecida demais".
- Se o filtro derrubar cards, **não** faz nova chamada para completar a cota **[desenho]**. Registra quantos caíram.

## 9. Exportar e importar geradores (fase 2)

- **Exportar**: salva um gerador num arquivo, com tudo menos chaves, identificação do serviço e baralho. Pacotes vendidos e trocas na comunidade usam este arquivo.
- **Importar**: lê o arquivo, mostra um resumo e pergunta o baralho de destino e o serviço de texto e de áudio a usar.
- O arquivo tem um número de versão de formato, para o add-on conseguir ler arquivos de versões antigas.
- **[construtor]** Formato (JSON é o óbvio) e extensão.

## 10. Registro e qualidade

É a parte que dá ao dono prática de avaliação de LLM, e a base para afinar os pacotes de geradores.

- Cada execução registra: data, gerador, versão da configuração, prompt final enviado, serviço e modelo, tokens de entrada e saída, custo estimado, duração, cards pedidos, recebidos, descartados por repetição e inseridos, motivo de bloqueio ou erro.
- Cada card registra: o texto gerado, o identificador da nota criada, se teve áudio e o destino (inserido direto, aceito, editado ou descartado). Se editado, guarda o texto original e o final.
- O registro fica na pasta de dados do add-on, que sobrevive a atualizações. **[construtor]** Formato: SQLite ou linhas JSON.
- **Primeira versão**: só registrar, com um botão "Exportar registro (CSV)". As análises o dono faz por fora.
- **[desenho]** Depois: uma tela simples por gerador, com taxa de aceitação, custo do mês e, cruzando com o Anki, quantas vezes os cards gerados foram errados.

## 11. Migração dos sistemas do dono

Detalhes no levantamento em `autocards-privado/reference/sistemas-atuais.md`, fora do repositório, ao lado da pasta do projeto.

### 11.1 Primeiro em paralelo, depois a troca **[dono]**

Os sistemas atuais **continuam rodando** até o add-on estar completamente validado. O uso do dono é a prova real de que o add-on funciona, e serve de base para vender o curso e os pacotes (seção 12, fase 3). Por isso, o registro (seção 10) é guardado desde o primeiro dia.

1. **Etapa 1: entrevista.** O primeiro gerador real é o de entrevista, porque o `estudo-entrevista` está parado e o baralho `Entrevista` não existe. É uso real, sem conflito com nada, e prova o add-on num tema que não é idioma.
2. **Etapa 2: inglês em paralelo.** Um gerador separado no baralho `AutoCards::English-teste`, com 2 a 3 cards por dia, roda ao lado do `anki-english`. A regra "Não repetir" lê os cards de `English::*`, então não duplica o que o sistema atual criou. Por algumas semanas, a qualidade dos dois é comparada.
3. **Etapa 3: troca.** Só quando o dono decidir, a partir dos números do registro. Aí valem a tabela e os passos abaixo.

Enquanto durar o paralelo, o add-on não mexe nos timers, nos scripts nem nos baralhos `English::*` e `Interview`.

### 11.2 Como fica cada sistema depois da troca

| Sistema atual | Vira |
|---|---|
| `estudo-ingles`, cotidiano | Gerador "Inglês do dia a dia" (modelo Idioma), baralho `English::Daily`, com áudio Edge, cerca de 6 por dia. |
| `estudo-ingles`, ML/MLOps | Gerador "Inglês para ML" (modelo Idioma), baralho `English::ML-MLOps`, com áudio, cerca de 4 por dia. |
| `estudo-entrevista` | Gerador "Entrevista técnica" (modelo Entrevista técnica), com a regra "Seguir uma lista de tópicos", alimentada pelas perguntas do `PLANO.md`. Só os itens que eram gerados pela IA (`tipo:fato`). Baralho a definir. |
| banco manual de frases | Não vira gerador, porque era um banco escrito à mão. Os cards dele ficam como estão. |

- Os textos dos prompts de hoje (`phrase_generator.py` do `estudo-ingles`) servem de ponto de partida para os campos de prompt dos geradores de inglês e do modelo Idioma.
- O desenho dos adaptadores de áudio pode seguir o contrato de `estudo-ingles/providers/base.py`.
- **Desligar, só na etapa 3 (11.1):**
  - os timers `anki-english` e o do banco manual de frases;
  - as duas entradas de inicialização duplicadas, `anki-english.desktop` e `anki-study.desktop`.
- **Manter:** uma entrada de inicialização só e um timer às 05:00, que apenas abrem o Anki.
- Os cards existentes não são tocados.
- Isso é configuração da máquina dele. Não faz parte do add-on publicado.

## 12. Fases

1. **Primeira versão (1.0), enxuta, para o dono** **[dono]**, estimada em 30 a 40 horas:
   - geradores com as quatro abas e os quatro modelos iniciais;
   - regras: Aumentar aos poucos, Só em alguns dias, Frear quando acumular, Não repetir e Teto de gasto;
   - serviços de texto (formato OpenAI) e **um** serviço de áudio: Edge pelo `QtWebSockets`, ou o formato OpenAI de áudio se o Edge falhar (ver a seção 13);
   - geração automática, aviso e "Rodar um comando ao terminar";
   - registro, com exportação em CSV;
   - interface em inglês, com a estrutura de tradução pronta.
   - **Critério de pronto da 1.0:** as etapas 1 e 2 da seção 11.1 rodam em paralelo por pelo menos 4 semanas **[desenho]**, sem falha que impeça a geração do dia, e o registro mostra custo, cards inseridos e descartados.
   - **Critério da troca (etapa 3):** decisão do dono, olhando o registro. Só aí os timers e scripts atuais são desligados.

   **Versão 1.1, logo depois, ainda dentro da fase 1** **[dono]**:
   - fila de aprovação (7.5);
   - Reforçar o que você erra;
   - Seguir uma lista de tópicos, e com ela o gerador de entrevista da migração;
   - os demais serviços de áudio (ElevenLabs, e o que tiver ficado de fora entre Edge e o formato OpenAI).
   - Os campos e telas dessas regras não precisam existir na 1.0, mas o formato de configuração do gerador deve deixar espaço para elas sem quebrar geradores já salvos.
2. **Publicação:**
   - exportar e importar geradores;
   - configuração guiada do primeiro serviço;
   - tradução para português;
   - página no AnkiWeb e repositório público, com README em inglês.
3. **Venda, fora do código e do AnkiWeb** **[dono]**:
   - **3a.** Curso em português ensinando a configurar: chave, serviço, campos de prompt, regras e rotina.
   - **3b.** Pacotes de geradores prontos por tema ou edital.
   - **Contexto:** o mercado brasileiro já compra pacotes de flashcards prontos na Hotmart.

## 13. Riscos conhecidos

- **Edge TTS** é um serviço não oficial da Microsoft. É o maior risco técnico desta lista.
  - O problema de instalação está resolvido: o Anki já traz o `PyQt6.QtWebSockets`, então o protocolo pode ser falado direto, sem o `edge-tts` nem o `aiohttp`.
  - **Provado em 13/11/2026:** um protótipo com o Python do Anki, só `QtWebSockets` e a geração de token copiada do `edge-tts` 7.3.1 (o `drm.py`, sem a dependência do `aiohttp`), gerou um MP3 válido (24 kHz, 48 kbps) em 1,5 s, com a voz `en-US-AriaNeural`.
  - O risco que sobra: a Microsoft muda o token de acesso (`Sec-MS-GEC`) de tempos em tempos, e o add-on vai precisar de atualização quando isso acontecer. O código do token fica isolado num módulo só, para facilitar.
  - **[dono]** Plano B: o formato OpenAI de áudio (pago, centavos por mês no volume do dono). Como último recurso, a voz nativa do Anki (`{{tts}}`), que tem custo zero, mas depende das vozes do sistema e no Linux geralmente não tem nenhuma.
  - Um áudio que falha nunca impede o card de entrar (seção 6.3, passo 7).
- **JSON de modelos pequenos ou locais** às vezes vem quebrado. Usar o modo de resposta estruturada quando o serviço suporta; senão, pedir JSON no prompt e validar.
- **Custo é estimativa**, porque depende do preço que o usuário informa. A tela diz isso.
- **Cards errados em temas sensíveis**, como medicina e direito. A fila de aprovação e o registro existem para isso. Um aviso na página do add-on recomenda ligar a aprovação nesses temas.
- **A API de add-ons do Anki muda entre versões.** Fixar a versão mínima e testar na atual.
- **Chaves guardadas em texto simples** na configuração do add-on. É o padrão dos add-ons. Nunca vão para arquivos exportados nem para o registro.

## 14. O que fica para o construtor

- Organização do código e das pastas, nomes de módulos e testes.
- Formato do registro e do arquivo de gerador.
- Nomes e modelos de card dos tipos de nota próprios.
- Critério de "parecido demais" no filtro de repetição, e quantos itens existentes mandar no prompt.
- Textos exatos dos modelos iniciais. Os de inglês partem do sistema atual.
- Detalhes visuais das telas, respeitando os rascunhos aprovados.
- Como empacotar e publicar o add-on.

## 15. Pendências

- ~~Nome definitivo do add-on~~: "AutoCards" (14/11/2026).
