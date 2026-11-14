# AutoCards 1.0 — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** add-on do Anki que gera, uma vez por dia por gerador, cards com IA (texto formato OpenAI + áudio Edge/OpenAI), com regras de proteção, registro e telas de configuração — a versão 1.0 da spec.

**Architecture:** núcleo em Python puro (`addon/core/`, sem `aqt`), testável com `unittest` no Python do Anki; camada de coleção (`addon/ankiops/`) que usa só `anki.collection` e é testada numa coleção temporária; camada de interface (`addon/gui/`) com Qt/`aqt`, verificada à mão no perfil `AutoCards-dev`. A execução roda numa thread de fundo (`QueryOp`), e a rede nunca toca a thread da interface.

**Tech Stack:** Python 3.13 do Anki 26.09.2; `requests`, `jsonschema`, `PyQt6` (`QtWebSockets`) que vêm no Anki; `sqlite3`, `unittest`, `difflib`, `http.server` da stdlib.

**Spec:** [`docs/superpowers/specs/2026-11-10-autocards-design.md`](../specs/2026-11-10-autocards-design.md)

## Global Constraints

- Nada para instalar: só stdlib + o que o Anki 26.09.2 traz (`requests`, `jsonschema`, `PyQt6`, `anki`, `aqt`). Nenhum `pip` em tempo de uso.
- Versão mínima do Anki: 26.09 (`manifest.json` → `"min_point_version": 260900`).
- Licença AGPL3 (arquivo `LICENSE` na raiz e em `addon/`).
- Rede nunca na thread da interface. Falha de um gerador não afeta os outros nem a abertura do Anki.
- Chaves de API nunca vão para registro, CSV ou arquivo exportado.
- Todo texto visível passa por `tr()` (`addon/core/i18n.py`), inglês como padrão.
- Não depender de nomes de campo do idioma do Anki: só tipos de nota próprios, criados pelo add-on.
- Dados do usuário em `addon/user_files/` (o Anki preserva essa pasta em atualizações): `autocards.json` (config) e `log.sqlite3` (registro).
- Desenvolvimento no perfil `AutoCards-dev`; o perfil real e os timers dos sistemas atuais não são tocados.
- Testes: `scripts/test.sh` = `~/.local/share/AnkiProgramFiles/.venv/bin/python -m unittest discover -s tests -t .` (sem pytest).

## Decisões do construtor (spec §14)

| Tema | Decisão |
|---|---|
| Registro | SQLite (`log.sqlite3`), tabelas `runs` e `cards` |
| Arquivo de gerador | JSON com `schema_version` (exportação é fase 2, mas o modelo já serializa assim) |
| Tipos de nota | `AutoCards Basic`, `AutoCards Reversed` (campos `Front`, `Back`, `Context`, `Audio`) e `AutoCards Cloze` (`Text`, `Back Extra`, `Context`, `Audio`) |
| Áudio no card | `[sound:<arquivo>]` no campo `Audio`, que o modelo mostra no lado escolhido |
| "Parecido demais" | `difflib.SequenceMatcher` ratio ≥ 0,88 sobre o texto normalizado (minúsculas, sem HTML, sem pontuação, espaços colapsados) |
| Itens no prompt "não repita" | os 150 mais recentes do baralho |
| "Dia" | data local do computador (`date.today()`) |
| Falha de rede | o dia não é marcado como feito; nova tentativa na checagem de hora em hora, no máximo 3 tentativas por dia por gerador |
| Regra "Ler de arquivo" | não aparece na 1.0 |

## Review Focus

1. **IA devolve JSON dentro de ```` ```json ```` ou com campos faltando/extras** → remover cercas, validar com `jsonschema`, descartar só os cards inválidos (Task 3).
2. **Sem internet às 05:00** → gerador falha, dia não marcado, nova tentativa na próxima hora, até 3 por dia (Task 9).
3. **Perfil fechado durante a geração** → a execução para antes de escrever, sem exceção visível (Task 10).
4. **Texto da IA com `<`, `&` ou quebras de linha** → escapado como HTML e `\n` vira `<br>`; lacunas `{{c1::...}}` preservadas (Task 7).
5. **Baralho de destino apagado depois da configuração** → recriado com o mesmo nome na inserção (Task 7).

---

## Estrutura de arquivos

```
addon/                      # pasta do add-on (link simbólico em addons21/autocards no dev)
  __init__.py               # ponto de entrada: só registra hooks se rodando dentro do Anki
  manifest.json  config.json  LICENSE
  core/                     # Python puro, sem aqt
    model.py                # dataclasses Generator, PromptField, Rules, Service, AppConfig + (de)serialização
    templates.py            # modelos iniciais: language, interview, concepts, blank
    prompt.py               # monta o prompt e o JSON Schema de resposta
    llm.py                  # cliente chat formato OpenAI (requests)
    dedupe.py               # normalização e filtro de repetidos
    rules.py                # cota do dia, dias da semana, freio, teto de gasto
    costs.py                # custo estimado
    store.py                # registro SQLite + CSV
    config_store.py         # lê/grava autocards.json
    i18n.py                 # tr() com tabelas en/pt
    tts/base.py  tts/edge.py  tts/edge_drm.py  tts/openai_tts.py
  ankiops/                  # usa anki.collection, sem GUI
    notetypes.py            # cria/garante os tipos de nota próprios
    collection.py           # vencidos, frentes existentes, inserir notas, gravar mídia
    runner.py               # uma execução de gerador, passo a passo (spec §6.3)
  gui/
    menu.py                 # Ferramentas › AutoCards
    scheduler.py            # profile_did_open + timer de 1 h + aviso + comando ao terminar
    services_dialog.py      # tela Serviços
    generator_dialog.py     # lista de geradores + 4 abas + Testar/Cancelar/Salvar
    widgets.py              # editor de campos do prompt (liga/desliga, arrastar, prévia)
tests/                      # unittest, um arquivo por módulo
scripts/test.sh  scripts/dev-link.sh  scripts/build.sh
```

---

### Task 1: Esqueleto, modelo de dados e config

**Files:** Create `addon/__init__.py`, `addon/manifest.json`, `addon/config.json`, `LICENSE`, `addon/LICENSE`, `addon/core/__init__.py`, `addon/core/model.py`, `addon/core/config_store.py`, `scripts/test.sh`, `scripts/dev-link.sh`, `tests/__init__.py`, `tests/test_model.py`

**Interfaces — Produces:**
- `PromptField(key: str, title: str, text: str, enabled: bool = True)`
- `Rules(ramp_enabled=True, ramp_start=2, ramp_end=10, ramp_weeks=4, weekdays_enabled=False, weekdays: list[int] = [0..6], brake_enabled=True, brake_limit=30, no_repeat=True, spend_cap_enabled=True, spend_cap_usd=2.0, extra: dict = {})` — `extra` guarda regras da 1.1 sem quebrar.
- `Generator(id: str, name: str, template: str, topic: str, level: str, cards_per_day: int, deck: str, text_service_id: str, text_model: str, prompt_fields: list[PromptField], card_format: str  # "basic"|"reversed"|"cloze", context_field: bool, audio_enabled: bool, audio_side: str  # "front"|"back", audio_service_id: str, voice: str, native_lang: str, target_lang: str, rules: Rules, created: str  # ISO date, last_success: str|None, attempts_today: dict, extra: dict)`
- `Service(id, name, kind: "text"|"tts", provider: str, base_url, api_key, default_model, price_in_per_m: float, price_out_per_m: float, price_per_k_chars: float)`
- `AppConfig(schema_version: int = 1, generators: list, services: list, post_run_command: str = "")`
- `to_dict(obj) -> dict`, `app_config_from_dict(d) -> AppConfig` (campos desconhecidos vão para `extra`; ausentes recebem padrão)
- `config_store.load(path) -> AppConfig`, `config_store.save(path, cfg) -> None` (grava em arquivo temporário e renomeia)

- [ ] Teste `test_roundtrip`: `app_config_from_dict(to_dict(cfg)) == cfg` para uma config com 1 gerador e 2 serviços.
- [ ] Teste `test_unknown_fields_preserved`: dict com `generators[0]["approval"]=True` → após roundtrip, `extra["approval"] is True`.
- [ ] Teste `test_load_missing_file_returns_empty`: `load(caminho_inexistente).generators == []`.
- [ ] Rodar `scripts/test.sh` → FAIL; implementar; rodar → PASS.
- [ ] `addon/__init__.py`: `try: from aqt import mw` / `except ImportError: mw = None`; se `mw`, importa `gui.menu.setup()` e `gui.scheduler.setup()` (criados nas Tasks 10–12; até lá guardados por `try`).
- [ ] `manifest.json`: `{"package": "autocards", "name": "AutoCards", "min_point_version": 260900, "human_version": "1.0.0-dev"}`.
- [ ] `scripts/dev-link.sh` cria `~/.local/share/Anki2/addons21/autocards -> <repo>/addon`.
- [ ] Commit `feat: esqueleto do add-on e modelo de dados`.

### Task 2: Montagem do prompt

**Files:** Create `addon/core/prompt.py`, `tests/test_prompt.py`

**Interfaces — Consumes:** `Generator`, `PromptField`. **Produces:**
- `response_schema(card_format: str, context_field: bool) -> dict` — JSON Schema: `{"type":"object","properties":{"cards":{"type":"array","items":{...}}},"required":["cards"]}`; item basic/reversed: `front`, `back` (+`context`); cloze: `text`, `back_extra` (+`context`).
- `user_part(gen) -> str` — campos ligados, em ordem, cada um como `## {title}\n{text}`.
- `fixed_block(gen, count: int, existing: list[str], extras: list[str]) -> str` — em inglês: quantidade, idioma (se `target_lang`), "Do not repeat these:" + lista, extras, e o schema serializado.
- `build_messages(gen, count, existing, extras) -> list[dict]` — `[{"role":"system","content": user_part}, {"role":"user","content": fixed_block}]`.

- [ ] Testes: campo desligado não aparece; ordem preservada; `fixed_block` contém `"Generate exactly 5 cards"`; lista de existentes aparece; schema cloze exige `text`.
- [ ] FAIL → implementar → PASS → commit `feat: montagem do prompt`.

### Task 3: Cliente de texto formato OpenAI

**Files:** Create `addon/core/llm.py`, `tests/test_llm.py` (servidor fake com `http.server` numa thread)

**Interfaces — Produces:**
- `@dataclass ChatResult(cards: list[dict], tokens_in: int, tokens_out: int, raw: str, dropped_invalid: int)`
- `class LLMError(Exception)`
- `chat_cards(base_url, api_key, model, messages, schema, timeout=60, http=requests) -> ChatResult` — POST `{base_url}/chat/completions` com `response_format={"type":"json_schema","json_schema":{"name":"cards","schema":schema}}`; se HTTP 400, repete sem `response_format`. Extrai `choices[0].message.content`, remove cercas ```` ``` ````, `json.loads`, valida cada item com `jsonschema` e descarta os inválidos. JSON inválido → mais uma tentativa; falhou de novo → `LLMError`. Header `Authorization` só se `api_key`.

- [ ] Testes: resposta com cercas é aceita; item sem `back` é descartado (`dropped_invalid == 1`); 400 com `response_format` → segunda chamada sem ele funciona; JSON quebrado duas vezes → `LLMError`; sem chave não envia `Authorization`; `usage` vira `tokens_in/out`.
- [ ] FAIL → implementar → PASS → commit `feat: cliente de texto formato OpenAI`.

### Task 4: Filtro de repetidos

**Files:** Create `addon/core/dedupe.py`, `tests/test_dedupe.py`

**Produces:** `normalize(text: str) -> str`; `filter_cards(cards: list[dict], key: str, existing: list[str], threshold=0.88) -> tuple[list[dict], int]` (compara com existentes e com o próprio lote; devolve aceitos e quantos caíram); `sample_existing(fronts_newest_first: list[str], limit=150) -> list[str]`.

- [ ] Testes: `normalize("<b>Hello,</b>  World!") == "hello world"`; duplicata exata cai; "I'd rather go" vs "I would rather go" decide pelo limiar (teste fixa o ratio esperado); duplicata dentro do lote cai; frente vazia cai.
- [ ] FAIL → implementar → PASS → commit `feat: filtro de repetidos`.

### Task 5: Regras, custo e registro

**Files:** Create `addon/core/rules.py`, `addon/core/costs.py`, `addon/core/store.py`, `tests/test_rules.py`, `tests/test_store.py`

**Produces:**
- `daily_quota(rules, cards_per_day, created: date, today: date) -> int` — com rampa: `round(A + (B-A) * min(1, dias/(7*N)))`; sem rampa: `cards_per_day`.
- `@dataclass Block(reason: str, detail: str)`; `check_blocks(gen, today, overdue: int, month_cost: float) -> Block|None` — ordem: dia da semana (`today.weekday()` fora de `weekdays`) → freio (`overdue > brake_limit`) → teto (`month_cost >= spend_cap_usd`).
- `should_run(gen, today, force: bool) -> bool` — `force` ou (`last_success != today` e `attempts_today.get(today,0) < 3`).
- `text_cost(svc, tin, tout) -> float`; `tts_cost(svc, chars) -> float`.
- `Store(path)`: `start_run(gen_id, config_version, is_test) -> run_id`; `finish_run(run_id, **fields)` (campos da spec §10: prompt, service, model, tokens_in, tokens_out, cost, duration_s, requested, received, dropped_dupe, inserted, blocked_reason, error); `add_card(run_id, text_json, note_id, has_audio, outcome)`; `month_cost(year, month) -> float` (soma sem testes); `export_csv(path)`.

- [ ] Testes: rampa 2→10 em 4 semanas dá 2 no dia 0, 6 no dia 14, 10 no dia 28 e no 60; freio com 31 vencidos e limite 30 bloqueia, com 30 não; teto bloqueia todos quando `month_cost=2.0`; `should_run` falso após 3 tentativas; `month_cost` ignora runs de teste; CSV não contém a string da chave usada no teste.
- [ ] FAIL → implementar → PASS → commit `feat: regras, custo e registro`.

### Task 6: Áudio (Edge e formato OpenAI)

**Files:** Create `addon/core/tts/__init__.py`, `base.py`, `edge.py`, `edge_drm.py`, `openai_tts.py`, `tests/test_tts.py`

**Produces:** `class TTSProvider(Protocol): synthesize(text: str, voice: str) -> bytes` (MP3) ; `class TTSError(Exception)`; `EdgeTTS().synthesize` (protocolo do protótipo `scratchpad/edge_qt/edge_qt_test.py`, com `QEventLoop` local — provado em thread de fundo em 13/11); `OpenAITTS(base_url, api_key, model="gpt-4o-mini-tts").synthesize` (POST `/audio/speech`, `response_format="mp3"`); `make_tts(service: Service) -> TTSProvider`; `EDGE_VOICES: dict[str, list[str]]` com vozes por idioma (en-US, en-GB, pt-BR, es-ES, fr-FR, de-DE, it-IT, ja-JP).

- [ ] `edge_drm.py`: copiar `drm.py` do `edge-tts` 7.3.1 sem `aiohttp`, com cabeçalho de licença LGPL3 e origem.
- [ ] Testes: `OpenAITTS` contra servidor fake devolve os bytes; erro HTTP vira `TTSError`; `EdgeTTS` real só com `AUTOCARDS_NET=1` (pula sem ele) e confere que começa com cabeçalho MP3.
- [ ] FAIL → implementar → PASS (`AUTOCARDS_NET=1 scripts/test.sh`) → commit `feat: áudio Edge e formato OpenAI`.

### Task 7: Tipos de nota e operações na coleção

**Files:** Create `addon/ankiops/__init__.py`, `notetypes.py`, `collection.py`, `tests/test_collection.py` (coleção temporária)

**Produces:**
- `ensure_notetype(col, card_format: str) -> NotetypeId` — cria se não existe; modelo mostra `{{Audio}}` no lado de `audio_side` e `{{Context}}` no verso se preenchido; `reversed` tem 2 modelos de card.
- `overdue_count(col, deck: str) -> int` — `len(col.find_cards(f'deck:"{deck}" is:due is:review'))`.
- `existing_fronts(col, deck: str) -> list[str]` — primeiro campo de todas as notas do baralho (qualquer tipo), mais recentes primeiro.
- `to_html(text: str) -> str` — `html.escape` + `\n`→`<br>`, preservando `{{cN::...}}`.
- `add_card(col, deck: str, card_format: str, card: dict, audio_file: str|None, audio_side: str, tags: list[str]) -> NoteId` — `col.decks.id(deck)` cria o baralho se faltar; tag `autocards`.
- `write_audio(col, data: bytes, stem: str) -> str` — `col.media.write_data(f"autocards_{stem}.mp3", data)`.

- [ ] Testes: tipo criado uma vez só (chamar 2×); nota basic com `<b>` no texto é escapada; cloze mantém `{{c1::x}}`; vencidos = 0 numa coleção nova; frentes de nota `Basic` do Anki também aparecem em `existing_fronts`; baralho apagado é recriado.
- [ ] FAIL → implementar → PASS → commit `feat: tipos de nota e operações na coleção`.

### Task 8: Modelos iniciais

**Files:** Create `addon/core/templates.py`, `tests/test_templates.py`

**Produces:** `TEMPLATES: dict[str, dict]` com `language`, `interview`, `concepts`, `blank`; `new_generator(template: str, name: str, deck: str, text_service_id: str, today: date) -> Generator`. Campos padrão (spec §7.2): `role`, `topic`, `level`, `front`, `back`, `avoid`, `examples`. O `language` parte do prompt de `estudo-ingles/phrase_generator.py` (frase curta natural no idioma estudado na frente, tradução no verso, contexto ligado, áudio ligado na frente). `interview`: pergunta na frente, resposta objetiva no verso, sem áudio. `concepts`: conceito/definição. `blank`: campos vazios ligados.

- [ ] Testes: cada modelo gera `Generator` válido; `language` tem `audio_enabled` e `context_field`; `blank` tem 7 campos com texto vazio.
- [ ] FAIL → implementar → PASS → commit `feat: modelos iniciais`.

### Task 9: Execução de um gerador

**Files:** Create `addon/ankiops/runner.py`, `tests/test_runner.py`

**Interfaces — Consumes:** Tasks 2–7. **Produces:**
- `@dataclass RunResult(generator_name: str, status: "ok"|"blocked"|"error"|"skipped", inserted: int, message: str)`
- `run_generator(col, cfg: AppConfig, gen: Generator, store: Store, today: date, force=False, is_test=False, chat=chat_cards, tts_factory=make_tts, should_abort=lambda: False) -> RunResult` — passos da spec §6.3. `is_test=True`: gera 1 card, não insere, devolve o card em `RunResult.message` como JSON. Sucesso: `last_success = today`. Erro: incrementa `attempts_today[today]`. Áudio que falha: card entra sem áudio e o erro vai para o registro. `should_abort()` checado antes de escrever.
- `run_all(col, cfg, store, today, force=False) -> list[RunResult]` — um depois do outro; exceção num gerador vira `status="error"` e segue.

- [ ] Testes (com `chat` e `tts` falsos): bloqueio pelo freio não chama `chat`; repetidos são contados; erro de rede não marca o dia e soma tentativa; 4ª tentativa no mesmo dia → `skipped`; falha de áudio insere sem áudio; `is_test` não cria nota; exceção no gerador A não impede o B; `should_abort` → nada inserido.
- [ ] FAIL → implementar → PASS → commit `feat: execução de geradores`.

### Task 10: Agendador, aviso e comando ao terminar

**Files:** Create `addon/gui/__init__.py`, `addon/gui/scheduler.py`, `addon/core/i18n.py`, `tests/test_i18n.py`

**Produces:** `setup()` — `gui_hooks.profile_did_open` dispara `run_due()`; `mw.progress.timer(3600*1000, run_due, repeat=True, parent=mw)`; `gui_hooks.profile_will_close` liga a flag de abortar. `run_due(force=False, only: str|None=None)` — evita duas execuções ao mesmo tempo; `QueryOp(parent=mw, op=lambda col: run_all(...), success=on_done).run_in_background()`, sem barra de progresso modal. `on_done(results)` — `tooltip` com "Nome: N new · Nome: failed (see log)", `mw.reset()`/refresh, e `post_run_command` via `subprocess.Popen([cmd, "success"|"error", msg])` se configurado. `i18n.tr(key, **kw) -> str` com idioma de `anki.lang.current_lang`, fallback `en`.
- [ ] Teste `test_i18n`: chave existente em `pt` traduz; chave só em `en` cai no inglês; chave desconhecida devolve a própria chave.
- [ ] Verificação manual no perfil `AutoCards-dev`: abrir o perfil com 1 gerador configurado (JSON à mão) gera os cards sem travar a tela e mostra o aviso.
- [ ] Commit `feat: agendador e aviso`.

### Task 11: Tela Serviços e menu

**Files:** Create `addon/gui/menu.py`, `addon/gui/services_dialog.py`

**Produces:** `menu.setup()` — Ferramentas › AutoCards: "Generators…", "Services…", "Generate now", "Export log (CSV)…". `ServicesDialog(mw)` — lista + formulário (nome, tipo, endereço, chave, modelo, preços); atalhos de texto: OpenAI `https://api.openai.com/v1`, OpenRouter `https://openrouter.ai/api/v1`, Ollama `http://localhost:11434/v1`, LM Studio `http://localhost:1234/v1`, Groq `https://api.groq.com/openai/v1`; áudio: Edge (sem chave), OpenAI TTS. "Test connection" roda em segundo plano (`GET {base}/models` para texto; síntese de "Hello" para áudio). Preços dos atalhos com aviso "estimates".
- [ ] Verificação manual: criar serviço OpenAI com a chave do sistema de inglês atual, testar conexão → OK; criar Edge → OK.
- [ ] Commit `feat: tela de serviços e menu`.

### Task 12: Tela de geradores

**Files:** Create `addon/gui/generator_dialog.py`, `addon/gui/widgets.py`

**Produces:** `GeneratorsDialog(mw)` — lista à esquerda com "+ New generator" (pergunta o modelo inicial), 4 abas: **Basic** (tema, nível, cards/dia, baralho com combo editável, serviço de texto e modelo, línguas no modelo `language`); **Prompt** (`PromptFieldsEditor`: lista arrastável com caixa liga/desliga, texto editável, "+ Add custom field", prévia somente leitura ao vivo de `user_part` + `fixed_block` com "Copy"); **Format & audio** (formato, contexto, áudio liga/desliga, lado, serviço, voz, "Listen to sample"); **Rules** (as 5 regras da 1.0 com parâmetros). Rodapé: "Test (1 sample card)" — roda `run_generator(is_test=True)` com a config não salva e mostra o card + toca o áudio; "Generate now"; Cancel; Save.
- [ ] Verificação manual: criar "Interview test" pelo modelo `interview`, Testar mostra um card e nada entra no baralho; Salvar e "Generate now" insere a cota.
- [ ] Commit `feat: tela de geradores`.

### Task 13: Pacote e validação de ponta a ponta

**Files:** Create `scripts/build.sh`, `README.md` (seção "Desenvolvimento")

- [ ] `scripts/build.sh` gera `dist/autocards.ankiaddon` (zip de `addon/` sem `user_files/`, `__pycache__`, `meta.json`).
- [ ] Suite completa: `AUTOCARDS_NET=1 scripts/test.sh` → todos PASS.
- [ ] Ponta a ponta no `AutoCards-dev`: fechar e abrir o perfil → gera a cota uma vez; reabrir no mesmo dia → não gera de novo; "Export log" gera CSV sem a chave.
- [ ] Commit `chore: pacote e validação da 1.0` e PR `feature/v1.0 → develop`.

---

## Depois deste plano

- **Plano 1.1** (`2026-xx-xx-autocards-v1.1.md`): fila de aprovação, Reforçar o que você erra, Seguir uma lista de tópicos (+ gerador de entrevista do `PLANO.md`), ElevenLabs.
- **Plano fase 2**: exportar/importar geradores, configuração guiada, tradução pt completa, README em inglês, retirada de `docs/reference/` do histórico.
- **Etapa 1 da validação real (spec §11.1)**: instalar no perfil real só com o gerador de entrevista.
