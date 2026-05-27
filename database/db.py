import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd

from config.settings import DB_PATH


def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with connect() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            participant_id TEXT,
            session_id TEXT,
            assignment_id TEXT,
            created_at TEXT,
            topic_id TEXT,
            topic_category TEXT,
            topic_prompt TEXT,
            agent_style TEXT,
            model_name TEXT,
            total_turns INTEGER,
            run_notes TEXT,
            device_type TEXT,
            pre_questionnaire_json TEXT,
            post_questionnaire_json TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT,
            turn_number INTEGER,
            speaker TEXT,
            text TEXT,
            word_count INTEGER,
            contains_question INTEGER,
            created_at TEXT,
            FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            conversation_id TEXT PRIMARY KEY,
            coherence REAL,
            topic_consistency REAL,
            novelty REAL,
            question_rate REAL,
            turn_balance REAL,
            engagement_score REAL,
            computed_at TEXT,
            FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
        )
        """)

        existing_columns = {
            row[1] for row in cur.execute("PRAGMA table_info(conversations)").fetchall()
        }
        migrations = {
            "device_type": "ALTER TABLE conversations ADD COLUMN device_type TEXT",
            "session_id": "ALTER TABLE conversations ADD COLUMN session_id TEXT",
            "assignment_id": "ALTER TABLE conversations ADD COLUMN assignment_id TEXT",
            "pre_questionnaire_json": "ALTER TABLE conversations ADD COLUMN pre_questionnaire_json TEXT",
            "post_questionnaire_json": "ALTER TABLE conversations ADD COLUMN post_questionnaire_json TEXT",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
                cur.execute(statement)


def save_conversation(meta: Dict[str, Any], transcript: List[Dict[str, Any]], metrics: Dict[str, float]) -> str:
    conversation_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat(timespec="seconds")

    with connect() as conn:
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO conversations (
            conversation_id, participant_id, session_id, assignment_id, created_at, topic_id, topic_category,
            topic_prompt, agent_style, model_name, total_turns, run_notes, device_type,
            pre_questionnaire_json, post_questionnaire_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            meta.get("participant_id", ""),
            meta.get("session_id", ""),
            meta.get("assignment_id", ""),
            created_at,
            meta["topic_id"],
            meta["topic_category"],
            meta["topic_prompt"],
            meta.get("agent_style", ""),
            meta["model_name"],
            len(transcript),
            meta.get("run_notes", ""),
            meta.get("device_type", "Unknown"),
            json.dumps(meta.get("pre_questionnaire", {}), ensure_ascii=False),
            json.dumps(meta.get("post_questionnaire", {}), ensure_ascii=False),
        ))

        for turn in transcript:
            text = turn.get("text", "")
            cur.execute("""
            INSERT INTO messages (
                message_id, conversation_id, turn_number, speaker, text,
                word_count, contains_question, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                conversation_id,
                turn["turn_number"],
                turn["speaker"],
                text,
                len(text.split()),
                1 if "?" in text else 0,
                turn.get("timestamp") or turn.get("created_at") or created_at,
            ))

        cur.execute("""
        INSERT INTO metrics (
            conversation_id, coherence, topic_consistency, novelty,
            question_rate, turn_balance, engagement_score, computed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            metrics["coherence"],
            metrics["topic_consistency"],
            metrics["novelty"],
            metrics["question_rate"],
            metrics["turn_balance"],
            metrics["engagement_score"],
            datetime.now().isoformat(timespec="seconds"),
        ))

    return conversation_id


def load_all():
    with connect() as conn:
        conversations = pd.read_sql_query("SELECT * FROM conversations", conn)
        messages = pd.read_sql_query(
            "SELECT * FROM messages ORDER BY conversation_id, turn_number",
            conn,
        )
        metrics = pd.read_sql_query("SELECT * FROM metrics", conn)
    return conversations, messages, metrics
