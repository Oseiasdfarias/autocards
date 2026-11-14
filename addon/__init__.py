"""AutoCards: gera cards novos todo dia, sozinho, com IA.

Só registra menus e hooks quando carregado dentro do Anki; importar este pacote fora do
Anki (testes) não tem efeito colateral.
"""
try:
    from aqt import mw
except ImportError:  # fora do Anki
    mw = None

if mw is not None:
    try:
        from .gui import menu, scheduler

        menu.setup()
        scheduler.setup()
    except ImportError:  # interface ainda não implementada (desenvolvimento)
        pass
