import hashlib
import uuid
from typing import Sequence, TypeVar

from config.agent_styles import ENGAGEMENT_STYLES
from config.topics import TOPICS

T = TypeVar("T")


def stable_index(seed: str, modulo: int, salt: str = "") -> int:
    """Return a reproducible index for a seed."""
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % modulo


def stable_choice(items: Sequence[T], seed: str, salt: str = "") -> T:
    return items[stable_index(seed, len(items), salt)]


def new_session_id() -> str:
    return str(uuid.uuid4())


def new_participant_id() -> str:
    """Create a hidden participant code for remote self-service sessions."""
    return f"P-{uuid.uuid4().hex[:10].upper()}"


def new_link_assignment_id() -> str:
    """Hidden assignment seed generated per opened participant link/session."""
    return f"L-{uuid.uuid4().hex[:12].upper()}"


def assign_condition(seed: str):
    """Assign topic/style once per hidden link/session seed."""
    clean_seed = seed.strip() or new_link_assignment_id()
    topic_index = stable_index(clean_seed, len(TOPICS), "topic")
    style_names = list(ENGAGEMENT_STYLES.keys())
    style_name = stable_choice(style_names, clean_seed, "style")
    return topic_index, style_name
