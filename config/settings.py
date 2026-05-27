import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


def _secret_or_env(name: str, default: str = "") -> str:
    if st is not None:
        try:
            value = st.secrets.get(name, None)
            if value is not None:
                return str(value)
        except Exception:
            pass
    return os.getenv(name, default)


APP_TITLE = "Human + Engagement Agent Experiment"
DB_PATH = _secret_or_env("DB_PATH", "human_experiment_data.db")

OPENAI_API_KEY = _secret_or_env("OPENAI_API_KEY", "")
OPENAI_MODEL = _secret_or_env("OPENAI_MODEL", "gpt-4o-mini")

DEFAULT_TOTAL_TURNS = int(_secret_or_env("DEFAULT_TOTAL_TURNS", "14"))
DEFAULT_MAX_AGENT_TOKENS = int(_secret_or_env("DEFAULT_MAX_AGENT_TOKENS", "130"))
DEFAULT_TEMPERATURE = float(_secret_or_env("DEFAULT_TEMPERATURE", "0.7"))
EMBEDDING_MODEL = _secret_or_env("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
