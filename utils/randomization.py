import hashlib
import uuid
from typing import Sequence, TypeVar

from config.agent_styles import ENGAGEMENT_STYLES
from config.topics import TOPICS

T = TypeVar("T")


def stable_index(seed: str, modulo: int, salt: str = "") -> int:
    """Return a reproducible index for a participant/session seed."""
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % modulo


def stable_choice(items: Sequence[T], seed: str, salt: str = "") -> T:
    return items[stable_index(seed, len(items), salt)]


def new_session_id() -> str:
    return str(uuid.uuid4())


def new_participant_id() -> str:
    """Create a hidden participant code for remote self-service sessions."""
    return f"P-{uuid.uuid4().hex[:8].upper()}"


def assign_condition(participant_id: str):
    """Assign topic/style once per participant in a reproducible way."""
    clean_id = participant_id.strip() or "anonymous"
    topic_index = stable_index(clean_id, len(TOPICS), "topic")
    style_names = list(ENGAGEMENT_STYLES.keys())
    style_name = stable_choice(style_names, clean_id, "style")
    return topic_index, style_name
