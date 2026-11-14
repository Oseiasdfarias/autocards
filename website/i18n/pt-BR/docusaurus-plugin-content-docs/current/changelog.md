---
title: Novidades
---

# Novidades

## 1.1.0

**Novo**
- **Aprovar antes de entrar:** fila de revisão para aceitar, editar ou descartar os cards gerados antes de eles chegarem ao seu estudo.
- **Reforçar o que você erra:** cards novos que explicam de outro jeito as notas que você continua errando.
- **Seguir uma lista de tópicos:** gera a partir da sua própria lista, em ordem.
- Áudio pela ElevenLabs.
- Exportar e importar geradores (`.autocards.json`). Chaves, serviços, baralho e modelo nunca são exportados.
- Assistente de configuração do primeiro serviço de IA.
- Interface em português.

**Correções**
- As chamadas de rede não prendem mais a thread da coleção do Anki, então a sincronização ao abrir e as revisões nunca esperam a IA.
- Fechar o perfil no meio da geração não gasta mais chamadas à API nem marca o dia como feito.
- Sem internet, o aviso diz isso, e a geração tenta de novo em 2 minutos.
- A tela de revisão fecha quando a fila esvazia.
- Saída estruturada em modo estrito, para a IA nunca deixar de fora um campo obrigatório.
- O registro exportado (CSV) mostra o nome do gerador, põe o custo de cada geração numa linha só (a coluna soma o gasto real) e deixa os testes de fora.
- A fila de revisão mostra o texto limpo enquanto você edita.
- Clicar em **Gerar agora** durante uma geração mostra um aviso, em vez de não fazer nada.

## 1.0.0

Primeira versão:
- geradores com quatro abas e quatro modelos iniciais;
- regras: aumentar aos poucos, só em alguns dias, frear quando acumular, não repetir, teto de gasto;
- qualquer serviço de texto compatível com a OpenAI;
- áudio do Edge e da OpenAI;
- geração diária automática, com aviso e um comando opcional ao terminar;
- registro com exportação em CSV.
