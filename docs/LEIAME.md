# AutoCards

Add-on do Anki que cria cards novos todo dia, sozinho, com IA. Cada pessoa configura geradores (tema, prompt por campos, formato, áudio e regras), e o add-on gera a cota do dia ao abrir o Anki.

**Estado:** versões 1.0 e 1.1 e o código da fase 2 implementados (branches `feature/v1.0` → `feature/v1.1` → `feature/fase2`), em validação. O README público, em inglês, está na raiz.

## Documentação

| Onde | O quê |
|---|---|
| [`docs/superpowers/specs/2026-11-10-autocards-design.md`](superpowers/specs/2026-11-10-autocards-design.md) | Documento de desenho: o que é, por quê, comportamento, telas, fases |
| [`docs/mockups/`](mockups/) | Rascunhos de tela aprovados: escolha da tela (B), aba Prompt, aba Regras |
| [`docs/research/2026-11-10-mercado.md`](research/2026-11-10-mercado.md) | Concorrentes, mercado brasileiro e licença |

| [`docs/superpowers/plans/`](superpowers/plans/) | Planos de implementação |

## Desenvolvimento

Nada para instalar: tudo roda com o Python que vem no Anki 26.09.

| Comando | O quê |
|---|---|
| `../scripts/test.sh` | Testes (`unittest`) com o Python do Anki |
| `AUTOCARDS_NET=1 scripts/test.sh` | Inclui o teste real do Edge TTS (precisa de internet) |
| `../scripts/dev-link.sh` | Liga `addon/` à pasta de add-ons do Anki (`ANKI_ADDONS=` muda o destino) |
| `../scripts/build.sh` | Gera `dist/autocards.ankiaddon` |

Estrutura:

- `addon/core/`: Python puro (modelo, prompt, IA, regras, registro, áudio);
- `addon/ankiops/`: operações na coleção e a execução de um gerador;
- `addon/gui/`: menu, telas e agendamento (só dentro do Anki).

Dados do usuário ficam em `addon/user_files/` (`autocards.json` e `log.sqlite3`), fora do git e do pacote.

Para testar sem tocar no perfil real, use uma pasta de dados separada:
`anki -b /caminho/de/teste -p AutoCards-dev`.

> O README público do add-on, em inglês, será escrito na fase de publicação.
