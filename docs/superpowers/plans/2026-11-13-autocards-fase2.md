# AutoCards fase 2 (publicação) — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** a parte de código da fase 2 da spec (§9, §7.6, §12): exportar/importar geradores, configuração guiada do primeiro serviço, tradução pt completa e README público em inglês.

**Architecture:** formato de troca em `addon/core/exchange.py` (Python puro, testável); telas em `addon/gui/`. Sem mudar o runner.

**Spec:** [`docs/superpowers/specs/2026-11-10-autocards-design.md`](../specs/2026-11-10-autocards-design.md)

## Global Constraints
As da 1.0 e 1.1. Arquivo exportado **nunca** leva chave, serviço, baralho nem estado de execução.

## Fora deste plano (decisão do dono)
- Retirar `docs/reference/` do histórico do git (reescrita irreversível do histórico).
- Página no AnkiWeb, nome definitivo, repositório público.

## Review Focus
1. **Arquivo de versão de formato mais nova** → erro claro, nada importado.
2. **Arquivo que não é de gerador (JSON qualquer)** → erro claro.
3. **Importar sem serviço de texto configurado** → manda para a configuração guiada.
4. **Exportar gerador com chave no texto de um campo do prompt** → exporta o texto como está (é do usuário); só os campos de serviço são removidos.
5. **Importar o mesmo arquivo duas vezes** → dois geradores com ids diferentes.

---

### Task 1: Formato de troca
**Files:** Create `addon/core/exchange.py`, `tests/test_exchange.py`
**Produces:** `FORMAT = "autocards-generator"`, `FORMAT_VERSION = 1`, `EXTENSION = ".autocards.json"`; `class ExchangeError(Exception)`; `export_generator(gen) -> dict` (`{"format", "format_version", "generator": {...}}` sem `id`, `deck`, `text_service_id`, `audio_service_id`, `last_success`, `attempts_today`, `created`, `rules.topics_done`); `summary(data) -> dict` (nome, modelo, formato, nº de campos, regras ligadas, áudio); `import_generator(data, deck, text_service_id, audio_service_id, today) -> Generator` (id novo, `created=today`, estado limpo).
- [ ] Testes: exportado não contém `api_key`/ids de serviço/baralho/estado; roundtrip preserva prompt, formato, regras e voz; versão 2 → `ExchangeError`; JSON sem `format` → `ExchangeError`; importar 2× → ids diferentes.
- [ ] FAIL → implementar → PASS → commit `feat: formato de troca de geradores`.

### Task 2: Exportar/Importar na tela
**Files:** Modify `addon/gui/generator_dialog.py`, `addon/core/i18n.py`; Create `addon/gui/import_dialog.py`; Test `tests/test_gui_smoke.py`
- [ ] Botões "Export…" e "Import…" na lista de geradores. Importar: lê o arquivo, mostra o resumo e pede baralho, serviço de texto e de áudio (`ImportDialog`).
- [ ] Teste de fumaça: exportar para arquivo temporário e importar de volta pela `ImportDialog` cria um segundo gerador com o baralho escolhido.
- [ ] Commit `feat: exportar e importar geradores`.

### Task 3: Configuração guiada do primeiro serviço
**Files:** Create `addon/gui/setup_wizard.py`; Modify `addon/gui/generator_dialog.py`, `addon/gui/menu.py`, `addon/core/i18n.py`; Test `tests/test_gui_smoke.py`
**Produces:** `SetupWizard(parent)` (QWizard, 3 páginas): 1) escolher serviço (OpenAI, OpenRouter, Groq, Ollama local) com explicação do que é uma chave e link para criar; 2) colar a chave (pulada para Ollama) e testar na hora; 3) pronto — cria o serviço de texto e um serviço de áudio Edge se não houver. `needs_setup(cfg) -> bool`. Abre sozinho ao abrir Geradores sem serviço de texto; também no menu "Setup assistant…".
- [ ] Teste de fumaça: `apply()` com OpenAI e chave cria 1 serviço de texto com o endereço do atalho e 1 Edge; segunda execução não duplica o Edge.
- [ ] Commit `feat: configuração guiada`.

### Task 4: Tradução completa e README público
**Files:** Modify `addon/core/i18n.py`, `README.md`, `addon/manifest.json`; Create `docs/LEIAME.md`; Test `tests/test_i18n.py`
- [ ] Teste: toda chave de `en` existe em `pt` (`test_pt_complete`).
- [ ] `README.md` público em inglês (o que é, por que, recursos, instalação, primeiro uso, custos, privacidade, licença, desenvolvimento); o conteúdo atual em português vai para `docs/LEIAME.md`.
- [ ] `manifest.json` → `human_version` `1.1.0`.
- [ ] Commit `docs: README público e tradução completa`.
