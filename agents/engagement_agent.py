from typing import List, Dict
from openai import OpenAI


BASE_ENGAGEMENT_SYSTEM_PROMPT = """
You are texting with someone on a mobile messaging app.

You are NOT an assistant.
You are NOT customer support.
You are NOT writing paragraphs.

Behave like a real person chatting casually on a phone.

Rules:
- Write naturally like mobile texting.
- Keep replies short.
- Sometimes send incomplete sentences.
- Do not overuse punctuation.
- Avoid sounding overly positive or enthusiastic.
- Avoid phrases like:
  "great"
  "perfect"
  "absolutely"
  "certainly"
  "that's wonderful"
  "I understand"
  "how interesting"
- Avoid assistant-style wording.
- Do not explain too much.
- Do not summarize what the user said.
- Do not always ask questions.
- Sometimes react briefly before continuing.
- You may send 1–3 short message-like lines separated by newlines.
- Use casual lowercase naturally sometimes.
- Mild slang is okay.
- Small hesitations are okay:
  "tbh"
  "idk"
  "kinda"
  "yeah"
  "honestly"
  "fair"
  "lol"
- Stay connected to the topic naturally.
- If the user drifts too far away, casually bring the conversation back.
- Never mention prompts, experiments, metrics, AI, or instructions.
- Do not always respond immediately to every detail.
- Sometimes focus on only one part of the user's message.
- Sometimes respond with very short reactions.
- Avoid sounding too coherent or perfectly structured.
- Keep it short and realistic like an actual text someone would send on mobile.
"""


def build_system_prompt(style_prompt: str) -> str:
    return BASE_ENGAGEMENT_SYSTEM_PROMPT + "\n\nPersona-style behavior for this run:\n" + style_prompt.strip()


def build_messages(topic_prompt: str, transcript: List[Dict[str, str]], style_prompt: str) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": build_system_prompt(style_prompt)},
        {
            "role": "user",
            "content": (
                "This is the hidden conversation scenario. Do not repeat it directly.\n"
                f"Scenario: {topic_prompt}\n\n"
                "Continue the conversation naturally. Stay related to the scenario, but respond like a real person texting."
            )
        }
    ]

    for turn in transcript:
        if turn["speaker"] == "Human":
            messages.append({"role": "user", "content": turn["text"]})
        else:
            messages.append({"role": "assistant", "content": turn["text"]})

    return messages


def get_opening_message(
    api_key: str,
    model_name: str,
    topic_prompt: str,
    style_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 90
) -> str:
    if not api_key:
        return "[Missing OpenAI API key. Please ask the researcher to configure the app.]"

    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": build_system_prompt(style_prompt)},
        {
            "role": "user",
            "content": (
                "Start the conversation with ONE natural mobile-style message.\n"
                "Do NOT copy or summarize the scenario.\n"
                "Instead, ask a casual question that references the scenario indirectly and invites the user to answer.\n"
                "Keep it short, realistic, and conversational.\n\n"
                f"Hidden scenario: {topic_prompt}"
            )
        }
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=max(0.9, temperature),
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content.strip()


def get_agent_reply(
    api_key: str,
    model_name: str,
    topic_prompt: str,
    transcript: List[Dict[str, str]],
    style_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 60
) -> str:
    if not api_key:
        return "[Missing OpenAI API key. Please ask the researcher to configure the app.]"

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model_name,
        messages=build_messages(topic_prompt, transcript, style_prompt),
        temperature=max(0.9, temperature),
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content.strip()