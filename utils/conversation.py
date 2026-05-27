from datetime import datetime
import random
from typing import Any, Dict, List, Optional

import streamlit as st

from config.settings import (
    DEFAULT_MAX_AGENT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOTAL_TURNS,
    OPENAI_MODEL,
)
from config.topics import TOPICS
from config.agent_styles import ENGAGEMENT_STYLES
from agents.engagement_agent import get_agent_reply, get_opening_message
from database.db import save_conversation
from evaluation.embeddings import load_embedder
from evaluation.metrics import compute_metrics
from utils.randomization import assign_condition, new_link_assignment_id, new_participant_id, new_session_id


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def initialize_conversation_state(include_researcher_defaults: bool = False) -> None:
    defaults = {
        "transcript": [],
        "metrics": None,
        "topic_index": 0,
        "opening_sent": False,
        "pending_agent_reply": False,
        "agent_reply_delay_seconds": 1.2,
        "auto_saved": False,
        "saved_conversation_id": None,
        "agent_style_name": "Neutral Engagement Agent",
        "target_turns": DEFAULT_TOTAL_TURNS,
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_AGENT_TOKENS,
        "model_name": OPENAI_MODEL,
        "device_type": "Unknown",
        "session_id": None,
        "participant_id": None,
        "assignment_id": None,
        "condition_assigned": False,
        "study_started": False,
        "pre_experiment_complete": False,
        "pre_experiment_answers": {},
        "post_experiment_complete": False,
        "post_experiment_answers": {},
    }

    if include_researcher_defaults:
        defaults.update({
            "participant_id": "P001",
            "run_notes": "",
        })
    else:
        defaults.update({
            "participant_id": st.session_state.get("participant_id"),
            "run_notes": st.session_state.get("run_notes", ""),
        })

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_turn(speaker: str, text: str) -> None:
    st.session_state.transcript.append({
        "turn_number": len(st.session_state.transcript) + 1,
        "speaker": speaker,
        "text": text.strip(),
        "timestamp": now_iso(),
    })
    st.session_state.metrics = None
    st.session_state.auto_saved = False
    st.session_state.saved_conversation_id = None


def reset_conversation(keep_assignment: bool = True) -> None:
    st.session_state.transcript = []
    st.session_state.metrics = None
    st.session_state.opening_sent = False
    st.session_state.pending_agent_reply = False
    st.session_state.agent_reply_delay_seconds = 1.2
    st.session_state.auto_saved = False
    st.session_state.saved_conversation_id = None
    if not keep_assignment:
        st.session_state.condition_assigned = False
        st.session_state.study_started = False
        st.session_state.session_id = None
        st.session_state.participant_id = None
        st.session_state.assignment_id = None


def ensure_hidden_remote_identity() -> None:
    """Create hidden IDs as soon as a participant opens the remote link.

    These IDs are not shown to participants. They are saved for the researcher so
    every remote user/link opening remains separated in the exported data.
    """
    if not st.session_state.get("participant_id"):
        st.session_state.participant_id = new_participant_id()
    if not st.session_state.get("session_id"):
        st.session_state.session_id = new_session_id()
    if not st.session_state.get("assignment_id"):
        st.session_state.assignment_id = new_link_assignment_id()

    if not st.session_state.get("condition_assigned"):
        topic_index, style_name = assign_condition(st.session_state.assignment_id)
        st.session_state.topic_index = topic_index
        st.session_state.agent_style_name = style_name
        st.session_state.condition_assigned = True


def start_remote_participant_session(participant_id: Optional[str] = None, pre_experiment_answers: Optional[Dict[str, Any]] = None) -> None:
    """Start a self-service participant session using hidden IDs and assignment."""
    ensure_hidden_remote_identity()

    if participant_id:
        # Optional researcher override; normal participants never see or enter this.
        st.session_state.participant_id = participant_id.strip()

    st.session_state.pre_experiment_answers = pre_experiment_answers or st.session_state.get("pre_experiment_answers", {})
    st.session_state.pre_experiment_complete = True
    st.session_state.study_started = True
    reset_conversation(keep_assignment=True)


def current_topic() -> Dict[str, Any]:
    return TOPICS[st.session_state.topic_index]


def current_style() -> Dict[str, Any]:
    return ENGAGEMENT_STYLES[st.session_state.agent_style_name]


def maybe_send_opening(api_key: str) -> None:
    if st.session_state.opening_sent:
        return

    topic = current_topic()
    style = current_style()

    with st.spinner("Starting conversation..."):
        opening = get_opening_message(
            api_key=api_key,
            model_name=st.session_state.model_name,
            topic_prompt=topic["prompt"],
            style_prompt=style["style_prompt"],
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
        )

    add_turn("Agent", opening)
    st.session_state.opening_sent = True
    st.rerun()


def _random_reply_delay(text: str) -> float:
    """Return a small varied delay so each agent reply feels less mechanical."""
    word_count = len(text.split())
    base_delay = random.uniform(0.75, 1.65)
    length_delay = min(word_count * 0.035, 0.85)
    return round(base_delay + length_delay, 2)


def queue_human_message(text: str) -> None:
    if len(st.session_state.transcript) >= st.session_state.target_turns:
        return

    add_turn("Human", text)

    if len(st.session_state.transcript) < st.session_state.target_turns:
        st.session_state.agent_reply_delay_seconds = _random_reply_delay(text)
        st.session_state.pending_agent_reply = True


def send_pending_agent_reply(api_key: str) -> bool:
    if not st.session_state.pending_agent_reply:
        return False

    if len(st.session_state.transcript) >= st.session_state.target_turns:
        st.session_state.pending_agent_reply = False
        return False

    topic = current_topic()
    style = current_style()

    reply = get_agent_reply(
        api_key=api_key,
        model_name=st.session_state.model_name,
        topic_prompt=topic["prompt"],
        transcript=st.session_state.transcript,
        style_prompt=style["style_prompt"],
        temperature=st.session_state.temperature,
        max_tokens=st.session_state.max_tokens,
    )

    add_turn("Agent", reply)
    st.session_state.pending_agent_reply = False
    st.rerun()
    return True


def compute_current_metrics(topic_prompt: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2") -> Dict[str, float]:
    topic_prompt = topic_prompt or current_topic()["prompt"]
    embedder = load_embedder(embedding_model)
    st.session_state.metrics = compute_metrics(st.session_state.transcript, topic_prompt, embedder)
    return st.session_state.metrics


def build_conversation_meta() -> Dict[str, Any]:
    topic = current_topic()
    return {
        "participant_id": st.session_state.get("participant_id", ""),
        "session_id": st.session_state.get("session_id", ""),
        "assignment_id": st.session_state.get("assignment_id", ""),
        "topic_id": topic["id"],
        "topic_category": topic["category"],
        "topic_prompt": topic["prompt"],
        "agent_style": st.session_state.agent_style_name,
        "model_name": st.session_state.model_name,
        "run_notes": st.session_state.get("run_notes", ""),
        "device_type": st.session_state.get("device_type", "Unknown"),
        "pre_questionnaire": st.session_state.get("pre_experiment_answers", {}),
        "post_questionnaire": st.session_state.get("post_experiment_answers", {}),
    }


def save_current_conversation(metrics: Optional[Dict[str, float]] = None) -> str:
    if metrics is None:
        metrics = st.session_state.metrics

    conversation_id = save_conversation(
        meta=build_conversation_meta(),
        transcript=st.session_state.transcript,
        metrics=metrics,
    )
    st.session_state.saved_conversation_id = conversation_id
    st.session_state.auto_saved = True
    return conversation_id


def auto_save_when_complete(embedding_model: str) -> Optional[str]:
    complete = len(st.session_state.transcript) >= st.session_state.target_turns
    if not complete or st.session_state.auto_saved or len(st.session_state.transcript) < 2:
        return None

    # In remote participant mode, save only after the post-experiment questionnaire
    # is submitted, so the exported row contains the full study data.
    if st.session_state.get("study_started") and not st.session_state.get("post_experiment_complete"):
        return None

    if st.session_state.metrics is None:
        compute_current_metrics(current_topic()["prompt"], embedding_model)

    return save_current_conversation(st.session_state.metrics)


def update_device_type_from_headers() -> str:
    """Best-effort device detection from URL/device script first, then browser headers."""
    # Client-side script writes ?device=mobile/tablet/desktop on first load.
    try:
        query_device = st.query_params.get("device", "")
        if isinstance(query_device, list):
            query_device = query_device[0] if query_device else ""
    except Exception:
        query_device = ""

    query_device = str(query_device).lower().strip()
    if query_device in {"mobile", "tablet", "desktop"}:
        device_type = query_device.capitalize()
        st.session_state.device_type = device_type
        return device_type

    user_agent = ""
    try:
        user_agent = st.context.headers.get("user-agent", "")  # Streamlit >= 1.36
    except Exception:
        user_agent = ""

    ua = user_agent.lower()
    if any(token in ua for token in ["ipad", "tablet", "kindle", "silk"]):
        device_type = "Tablet"
    elif "android" in ua and "mobile" not in ua:
        device_type = "Tablet"
    elif any(token in ua for token in ["mobi", "iphone", "ipod", "android"]):
        device_type = "Mobile"
    elif ua:
        device_type = "Desktop"
    else:
        device_type = "Unknown"

    st.session_state.device_type = device_type
    return device_type
