---
sidebar_position: 2
title: Instalação
---

# Instalação

1. Baixe o `autocards.ankiaddon` na [página de Releases do GitHub](https://github.com/Oseiasdfarias/autocards/releases), ou [gere a partir do código](development.md#gerar-o-pacote).
2. No Anki, abra **Ferramentas › Extensões › Instalar de um arquivo...** e escolha o arquivo.
3. Reinicie o Anki.

Aparece um menu novo: **Ferramentas › AutoCards**.

![O menu do AutoCards](/img/screens/pt-BR/menu.png)

*O menu do AutoCards*


| Item do menu | O que faz |
|---|---|
| Geradores… | Criar e editar geradores. |
| Serviços… | Suas conexões de IA e de áudio. |
| Assistente de configuração… | Configuração guiada do primeiro serviço de IA. |
| Revisar cards gerados… | A fila de aprovação (veja [Fila de revisão](review-queue.md)). |
| Gerar agora | Roda todos os geradores agora, mesmo que já tenham rodado hoje. |
| Exportar registro (CSV)… | Salva o registro completo como planilha. |

## Atualizar

Instale o arquivo novo do mesmo jeito. Seus geradores, serviços e registro ficam na pasta `user_files` do add-on, que o Anki preserva nas atualizações.

## Desinstalar

**Ferramentas › Extensões**, selecione o AutoCards e clique em **Excluir**. Os cards já criados continuam na sua coleção.
