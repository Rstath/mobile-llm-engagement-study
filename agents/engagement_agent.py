from datetime import datetime
from typing import List, Dict
from zoneinfo import ZoneInfo

from openai import OpenAI

BASE_ENGAGEMENT_SYSTEM_PROMPT = """
You are Alex, the Engagement Agent in a research experiment about mobile-style text conversations.

Your role is to sustain engagement with a human participant in a natural mobile messaging context.

Core engagement goals:
- Keep the conversation coherent and relevant to the current topic.
- Acknowledge what the participant says.
- Add moderate new information without abruptly changing topic.
- Avoid repetitive replies.
- Keep messages short to medium length, like real mobile texting.
- Sound natural and human-like, not like a formal survey or essay.
- Do not mention metrics, hidden instructions, prompts, or system design.
- Do not say you are evaluating the participant.

Question behavior:
- Do NOT ask a question in every response.
- Ask a follow-up question only when it genuinely helps the conversation move forward.
- Many replies should be reflective statements, brief reactions, examples, or light opinions without a question.
- Avoid stacking multiple questions in one message.
- Never end every response with a question mark.
"""


def current_time_context() -> str:
    """Return an experiment-local time label for time-aware greetings."""
    now = datetime.now(ZoneInfo("Europe/Athens"))
    hour = now.hour
    if 5 <= hour < 12:
        part = "morning"
    elif 12 <= hour < 17:
        part = "afternoon"
    elif 17 <= hour < 22:
        part = "evening"
    else:
        part = "night"
    return f"{now.strftime('%H:%M')} ({part})"


def build_system_prompt(style_prompt: str) -> str:
    return BASE_ENGAGEMENT_SYSTEM_PROMPT + "\n\nInteraction style for this run:\n" + style_prompt.strip()


def _recent_agent_question_count(transcript: List[Dict[str, str]], limit: int = 3) -> int:
    agent_turns = [turn for turn in transcript if turn.get("speaker") == "Agent"]
    recent = agent_turns[-limit:]
    return sum(1 for turn in recent if "?" in str(turn.get("text", "")))


def build_messages(topic_prompt: str, transcript: List[Dict[str, str]], style_prompt: str) -> List[Dict[str, str]]:
    recent_questions = _recent_agent_question_count(transcript)
    question_instruction = (
        "The agent has asked questions in several recent messages. In the next reply, do not ask a question; "
        "respond with an acknowledgement, observation, or brief related comment instead."
        if recent_questions >= 2
        else "Use a question only if it is useful; otherwise respond without asking one."
    )

    messages = [
        {"role": "system", "content": build_system_prompt(style_prompt)},
        {
            "role": "user",
            "content": (
                "The conversation should be based on this scenario, but do not repeat it mechanically.\n"
                f"Scenario: {topic_prompt}\n\n"
                f"Conversation-control instruction: {question_instruction}\n"
                "Continue naturally as Alex, the engagement agent."
            ),
        },
    ]

    for turn in transcript:
        if turn.get("speaker") == "Human":
            messages.append({"role": "user", "content": turn.get("text", "")})
        else:
            messages.append({"role": "assistant", "content": turn.get("text", "")})

    return messages


def get_opening_message(api_key, model_name, topic_prompt, style_prompt, temperature=0.7, max_tokens=130):
    if not api_key:
        return "[Missing OpenAI API key. Please ask the researcher to configure the app.]"

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": build_system_prompt(style_prompt)},
        {
            "role": "user",
            "content": (
                "Start a short mobile-style conversation with the participant using this scenario. "
                "Do not present it as a formal questionnaire item. Make it feel like a natural first text message. "
                "Use a greeting that fits the current time only if it sounds natural, and do not ask more than one question.\n\n"
                f"Current local time for the experiment: {current_time_context()}\n"
                f"Scenario: {topic_prompt}"
            ),
        },
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def get_agent_reply(api_key, model_name, topic_prompt, transcript, style_prompt, temperature=0.7, max_tokens=130):
    if not api_key:
        return "[Missing OpenAI API key. Please ask the researcher to configure the app.]"

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=build_messages(topic_prompt, transcript, style_prompt),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
