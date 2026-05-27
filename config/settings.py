import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "Human + Engagement Agent Experiment"
DB_PATH = "human_experiment_data.db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

DEFAULT_TOTAL_TURNS = 14
DEFAULT_MAX_AGENT_TOKENS = 130
DEFAULT_TEMPERATURE = 0.7
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
