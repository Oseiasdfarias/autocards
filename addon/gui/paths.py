"""Caminhos dos dados do usuário (pasta user_files, preservada pelo Anki nas atualizações)."""
import os

USER_FILES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_files")
CONFIG_PATH = os.path.join(USER_FILES, "autocards.json")
LOG_PATH = os.path.join(USER_FILES, "log.sqlite3")
