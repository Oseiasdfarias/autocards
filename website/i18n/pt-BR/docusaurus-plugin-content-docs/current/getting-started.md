---
sidebar_position: 3
title: Primeiros passos
---

# Primeiros passos

## 1. Conecte um serviço de IA

Abra **Ferramentas › AutoCards › Geradores…**. Na primeira vez, abre o **assistente de configuração**:

1. **Escolha um serviço.** A OpenAI é a mais simples; OpenRouter e Groq têm opções grátis; o Ollama roda no seu computador (instale antes).
2. **Cole sua chave de API.** A chave de API é um código, parecido com uma senha, que deixa o add-on usar a sua conta. O assistente tem o link da página onde você cria a chave. Clique em **Testar conexão** para conferir na hora.
3. **Concluir.** O serviço é salvo, junto com o áudio grátis do Edge.

![Assistente de configuração: escolha o serviço, depois cole e teste a chave](/img/screens/pt-BR/wizard-1.png)
![Assistente de configuração: escolha o serviço, depois cole e teste a chave](/img/screens/pt-BR/wizard-2.png)

*Assistente de configuração: escolha o serviço, depois cole e teste a chave*


Dá para mudar os serviços depois em **Ferramentas › AutoCards › Serviços…**.

![A última página do assistente](/img/screens/pt-BR/wizard-3.png)

*A última página do assistente*


## 2. Crie um gerador

Clique em **+ Novo gerador** e escolha um modelo inicial:

![Escolha do modelo inicial](/img/screens/pt-BR/template-picker.png)

*Escolha do modelo inicial*


| Modelo | Bom para | Padrões |
|---|---|---|
| **Idioma** | Frases na língua que você estuda, traduzidas para a sua | Campo de contexto e áudio ligados |
| **Entrevista técnica** | Perguntas de entrevista com respostas curtas e objetivas | Sem áudio |
| **Conceitos** | Um conceito por card, definição e exemplo | Sem áudio |
| **Em branco** | Escrever seu próprio prompt do zero | Todos os campos vazios |

Depois, na aba **Básico**, preencha o que você quer estudar, o nível, os cards por dia e o baralho de destino. Veja [Geradores](generators.md) para todas as opções.

![A aba Básico de um gerador de Idioma](/img/screens/pt-BR/generator-basic.png)

*A aba Básico de um gerador de Idioma*


## 3. Teste antes de salvar

Clique em **Testar: gerar 1 card de exemplo**. O AutoCards mostra um card feito com a configuração atual, toca o áudio se houver e **não o coloca no Anki**. É também o jeito mais rápido de conferir se a chave funciona.

![Um card de exemplo: nada entra no Anki](/img/screens/pt-BR/test-result.png)

*Um card de exemplo: nada entra no Anki*


## 4. Salve e deixe rodar

Clique em **Salvar**. A partir daí, sempre que seu perfil abrir:

- cada gerador que ainda não rodou hoje cria a cota em segundo plano;
- você continua estudando enquanto ele trabalha;
- um aviso mostra o resultado, por exemplo `Inglês do dia a dia: 6 novos · Entrevista: 3 novos · 2 esperando revisão`.

Para rodar na hora, use **Gerar agora** (na tela ou no menu).

![O aviso no fim da geração](/img/screens/pt-BR/notice.png)

*O aviso no fim da geração*


:::tip Comece pequeno
A regra **Aumentar aos poucos** vem ligada: um gerador novo começa com 2 cards por dia e chega a 10 em 4 semanas. Mude isso na aba [Regras](rules.md).
:::
