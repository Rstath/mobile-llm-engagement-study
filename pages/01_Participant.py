import time
from typing import Any, Dict

import streamlit as st
import streamlit.components.v1 as components

from config.settings import EMBEDDING_MODEL, OPENAI_API_KEY
from database.db import init_db
from ui.mobile_chat import render_mobile_shell, mobile_message_form
from utils.conversation import (
    auto_save_when_complete,
    ensure_hidden_remote_identity,
    initialize_conversation_state,
    maybe_send_opening,
    queue_human_message,
    send_pending_agent_reply,
    start_remote_participant_session,
    update_device_type_from_headers,
)


def inject_device_detection_script() -> None:
    """Detect viewport/client device from the browser that opened the shared link."""
    components.html(
        """
        <script>
        (function () {
            const parentWindow = window.parent;
            const url = new URL(parentWindow.location.href);
            if (url.searchParams.get('device')) return;

            const ua = navigator.userAgent.toLowerCase();
            const width = Math.min(parentWindow.innerWidth || screen.width, screen.width || parentWindow.innerWidth);
            let device = 'desktop';
            if (/ipad|tablet|kindle|silk/.test(ua) || (ua.includes('android') && !ua.includes('mobile')) || (width > 767 && width <= 1024)) {
                device = 'tablet';
            } else if (/mobi|iphone|ipod|android/.test(ua) || width <= 767) {
                device = 'mobile';
            }
            url.searchParams.set('device', device);
            parentWindow.history.replaceState({}, '', url.toString());
            parentWindow.location.reload();
        })();
        </script>
        """,
        height=0,
    )


def hide_all_researcher_ui() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        :root {
            --study-blue: #2563eb;
            --study-blue-soft: #dbeafe;
            --study-border: #d7dee8;
            --study-text: #111827;
            --study-muted: #6b7280;
            --study-bg: #f3f6fb;
        }

        .stApp {
            background: var(--study-bg);
        }

        .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding: 1rem clamp(0.75rem, 3vw, 2.5rem) 2rem clamp(0.75rem, 3vw, 2.5rem);
        }

        .participant-questionnaire-page {
            width: 100%;
        }

        .questionnaire-card {
            width: min(100%, 1180px);
            margin: 0 auto;
            padding: clamp(1rem, 2.5vw, 2rem);
            border-radius: 26px;
            background: #ffffff;
            border: 1px solid var(--study-border);
            box-shadow: 0 16px 45px rgba(15, 23, 42, 0.08);
        }

        .questionnaire-card h2,
        .questionnaire-card h3 {
            color: var(--study-text);
            margin-top: 0;
        }

        .questionnaire-card .stCaption,
        .questionnaire-card p {
            color: var(--study-muted);
        }

        .questionnaire-section {
            padding: 1.15rem;
            margin: 1rem 0;
            border: 1px solid #e5eaf3;
            background: #ffffff;
            border-radius: 18px;
        }

        .questionnaire-section h3 {
            font-size: 1.08rem;
            margin-bottom: 0.65rem;
        }

        .questionnaire-card div[data-testid="stForm"] {
            background: #ffffff !important;
            border: 1px solid var(--study-border) !important;
            border-radius: 22px !important;
            padding: clamp(1rem, 2vw, 1.5rem) !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        .questionnaire-card label,
        .questionnaire-card [data-testid="stMarkdownContainer"] {
            color: var(--study-text);
        }

        .questionnaire-card div[role="radiogroup"] {
            gap: 0.45rem 0.8rem;
        }

        .questionnaire-card div[role="radiogroup"] label,
        .questionnaire-card [data-testid="stCheckbox"] label {
            border: 1px solid #dbe3ee;
            background: #f8fbff;
            border-radius: 14px;
            padding: 0.45rem 0.65rem;
            margin: 0.15rem 0;
            transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
        }

        .questionnaire-card div[role="radiogroup"] label:has(input:checked),
        .questionnaire-card [data-testid="stCheckbox"] label:has(input:checked) {
            border-color: var(--study-blue) !important;
            background: var(--study-blue-soft) !important;
            box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
        }

        .questionnaire-card input[type="radio"],
        .questionnaire-card input[type="checkbox"] {
            accent-color: var(--study-blue);
        }

        .questionnaire-card textarea,
        .questionnaire-card input[type="text"] {
            background: #ffffff !important;
            border-color: #cbd5e1 !important;
            border-radius: 14px !important;
        }

        .questionnaire-card div[data-testid="stFormSubmitButton"] button {
            background: var(--study-blue) !important;
            color: white !important;
            border: 0 !important;
            border-radius: 14px !important;
            min-height: 46px;
            font-weight: 700;
        }

        .bs-row {
            display: grid;
            grid-template-columns: repeat(12, minmax(0, 1fr));
            gap: 1rem;
            width: 100%;
        }

        .bs-col-12 { grid-column: span 12; }
        .bs-col-6 { grid-column: span 6; }

        @media (max-width: 1440px) {
            .questionnaire-card div[role="radiogroup"] {
                flex-direction: column !important;
                align-items: stretch !important;
            }

            .questionnaire-card div[role="radiogroup"] label {
                width: 100%;
            }

            .bs-col-6 { grid-column: span 12; }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 0;
                padding-right: 0;
            }

            .questionnaire-card {
                border-radius: 0;
                border-left: 0;
                border-right: 0;
                padding: 1rem;
            }

            .questionnaire-card div[data-testid="stForm"] {
                padding: 0.85rem !important;
                border-radius: 16px !important;
            }

            .questionnaire-section {
                padding: 0.85rem;
                border-radius: 14px;
            }
        }

        .thank-you-card {
            width: min(100%, 680px);
            margin: 14vh auto 0 auto;
            text-align: center;
            padding: clamp(1.5rem, 5vw, 3rem);
            border-radius: 28px;
            background: #ffffff;
            border: 1px solid #dcfce7;
            box-shadow: 0 10px 35px rgba(22, 163, 74, 0.12);
        }

        .thank-you-check {
            width: 72px;
            height: 72px;
            margin: 0 auto 1rem auto;
            border-radius: 50%;
            background: #16a34a;
            color: white;
            font-size: 46px;
            line-height: 72px;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def open_questionnaire_card(title: str, caption: str = "") -> None:
    st.markdown('<div class="participant-questionnaire-page"><div class="questionnaire-card">', unsafe_allow_html=True)
    st.subheader(title)
    if caption:
        st.caption(caption)


def close_questionnaire_card() -> None:
    st.markdown('</div></div>', unsafe_allow_html=True)


def section_heading(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="questionnaire-section"><h3>{title}</h3>', unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def close_section() -> None:
    st.markdown('</div>', unsafe_allow_html=True)


def render_pre_experiment_questionnaire() -> None:
    open_questionnaire_card(
        "Pre-experiment questionnaire",
        "This study investigates how people interact in short text-based conversations similar to mobile messaging. "
        "Your responses will be used for research purposes only and will remain anonymous. "
        "The questionnaire takes approximately 3–5 minutes to complete. By proceeding, you confirm that you are at least 18 years old and consent to participate in this study.",
    )

    frequency_options = ["Very rarely", "Rarely", "Sometimes", "Often", "Very often"]
    ai_frequency_options = ["Never used", "Very rarely", "Rarely", "Sometimes", "Often", "Very often"]
    emotion_options = ["Very rarely", "Rarely", "Sometimes", "Often", "Very often"]

    with st.form("pre_experiment_questionnaire"):
        section_heading("Demographics")
        age_group = st.radio("What is your age group? *", ["18-24", "25-34", "35-44", "35 +"], index=None)
        gender = st.radio("What is your gender? *", ["Female", "Male", "Non-binary / Other", "Prefer not to say"], index=None)
        education = st.radio("What is your highest level of education? *", ["High school", "Undergraduate degree", "Postgraduate degree", "Other"], index=None)
        messaging_app_use = st.radio(
            "How often do you use messaging applications (e.g., WhatsApp, Messenger, Viber)? *",
            ["Less than once per day", "1–3 times per day", "4–10 times per day", "More than 10 times per day"],
            index=None,
        )
        close_section()

        section_heading("Mobile Communication Habits")
        text_communication_ease = st.radio(
            "How easy do you find it to communicate through text messages? *",
            [1, 2, 3, 4, 5],
            index=None,
            horizontal=True,
            captions=["Not easy at all", "", "", "", "Very easy"],
        )
        st.markdown("How frequently do you use the following text messaging styles when you communicate? *")
        st.caption("Especially when you want to say a lot in your messages, consider whether you typically write everything in one long message or break your thoughts into multiple shorter consecutive messages.")
        style_one_two_words = st.radio("One or two words per message", frequency_options, index=None, horizontal=True)
        style_single_sentence = st.radio("A single sentence per message", frequency_options, index=None, horizontal=True)
        style_short_message = st.radio("A short message (2-3 sentences)", frequency_options, index=None, horizontal=True)
        style_long_message = st.radio("A long detailed message of multiple sentences", frequency_options, index=None, horizontal=True)
        close_section()

        section_heading("Experience with Conversational AI")
        used_ai_before = st.radio(
            "Have you ever used conversational AI assistants to accomplish tasks in the past? *",
            ["Yes", "No"],
            index=None,
            help="For example, general-purpose assistants like ChatGPT, or specific-purpose assistants like customer service chatbots.",
        )
        close_section()

        section_heading("Experience with Conversational AI")
        st.markdown("How often (if at all) do you use conversational AI assistants to accomplish various tasks? *")
        ai_general_purpose = st.radio("General-purpose AI assistants (e.g. ChatGPT, Gemini, Claude)", ai_frequency_options, index=None, horizontal=True)
        ai_specific_purpose = st.radio("Specific-purpose AI assistants (e.g. customer service chatbots)", ai_frequency_options, index=None, horizontal=True)

        st.markdown("Reflecting on your experience in interacting with various AI assistants, how often do you feel... *")
        emotion_rows = [
            "Insecure", "Helpless", "Excluded", "Threatened", "Critical", "Frustrated",
            "Humiliated", "Bitter", "Hurt", "Guilty", "Powerless", "Lonely",
            "Powerful", "Excited", "Proud", "Hopeful", "Startled", "Disapproving",
            "Awful", "Repelled",
        ]
        emotion_answers = {}
        for emotion in emotion_rows:
            emotion_answers[emotion.lower()] = st.radio(
                emotion,
                emotion_options,
                index=None,
                horizontal=True,
                key=f"pre_emotion_{emotion.lower()}",
            )

        consent = st.checkbox("I understand that my conversation and questionnaire answers will be saved for research analysis. *")
        close_section()
        submitted = st.form_submit_button("Start conversation", use_container_width=True)

    if submitted:
        answers: Dict[str, Any] = {
            "age_group": age_group,
            "gender": gender,
            "education": education,
            "messaging_app_use": messaging_app_use,
            "text_communication_ease_1_5": text_communication_ease,
            "message_style_one_two_words": style_one_two_words,
            "message_style_single_sentence": style_single_sentence,
            "message_style_short_2_3_sentences": style_short_message,
            "message_style_long_detailed": style_long_message,
            "used_ai_before": used_ai_before,
            "ai_use_general_purpose": ai_general_purpose,
            "ai_use_specific_purpose": ai_specific_purpose,
            "ai_experience_emotions": emotion_answers,
            "consent_confirmed": consent,
        }
        missing = [key for key, value in answers.items() if value in (None, "")]
        missing += [f"ai_experience_emotions.{key}" for key, value in emotion_answers.items() if value in (None, "")]
        if missing or not consent:
            st.warning("Please answer all required questions before starting.")
        else:
            start_remote_participant_session(pre_experiment_answers=answers)
            st.rerun()

    close_questionnaire_card()


def render_post_experiment_questionnaire() -> None:
    open_questionnaire_card("Post-experiment questionnaire", "Please answer the following questions about the conversation you just completed.")

    with st.form("post_experiment_questionnaire"):
        section_heading("Conversation experience")
        engaging = st.radio("How engaging did you find the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not engaging at all", "", "", "", "Very engaging"])
        willing_continue = st.radio("How willing would you be to continue this conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not willing at all", "", "", "", "Very willing"])
        coherent = st.radio("How coherent were the responses during the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not coherent at all", "", "", "", "Very coherent"])
        on_topic = st.radio("To what extent did the conversation stay on topic? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Completely"])
        natural = st.radio("How natural did the conversation feel? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not natural at all", "", "", "", "Very natural"])
        smooth = st.radio("How smooth was the flow of the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Very much"])
        repetitive = st.radio("Did the conversation feel repetitive at any point? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all repetitive", "", "", "", "Very repetitive"])
        followups = st.radio("Did the system ask relevant or helpful follow-up questions? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Very much"])
        balanced = st.radio("How balanced did the conversation feel? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Very unbalanced", "", "", "", "Very balanced"])
        overall = st.radio("Overall, how would you rate this conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Very poor", "", "", "", "Excellent"])
        close_section()

        section_heading("Open feedback")
        liked = st.text_area("Please mention up to 3 things that you liked about the conversation. *")
        disliked = st.text_area("Please mention up to 3 things that you did not like about the conversation. *")
        improvements = st.text_area("Do you have any ideas about how the conversational assistant could be improved? What would you remove, add or change in its behaviour?")
        close_section()

        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        answers: Dict[str, Any] = {
            "engaging_1_5": engaging,
            "willing_continue_1_5": willing_continue,
            "coherent_1_5": coherent,
            "stayed_on_topic_1_5": on_topic,
            "natural_1_5": natural,
            "smooth_flow_1_5": smooth,
            "repetitive_1_5": repetitive,
            "relevant_followups_1_5": followups,
            "balanced_1_5": balanced,
            "overall_rating_1_5": overall,
            "liked_up_to_3": liked.strip(),
            "disliked_up_to_3": disliked.strip(),
            "improvement_ideas": improvements.strip(),
        }
        required = {k: v for k, v in answers.items() if k != "improvement_ideas"}
        if any(value in (None, "") for value in required.values()):
            st.warning("Please answer all required questions before submitting.")
        else:
            st.session_state.post_experiment_answers = answers
            st.session_state.post_experiment_complete = True
            auto_save_when_complete(EMBEDDING_MODEL)
            st.rerun()

    close_questionnaire_card()


def render_thank_you() -> None:
    st.markdown(
        """
        <div class="thank-you-card">
            <div class="thank-you-check">✓</div>
            <h2>Thank you!</h2>
            <p>Your responses have been submitted successfully.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Conversation", layout="wide")
    hide_all_researcher_ui()
    inject_device_detection_script()
    init_db()
    initialize_conversation_state(include_researcher_defaults=False)
    ensure_hidden_remote_identity()
    device_type = update_device_type_from_headers()

    if st.session_state.get("post_experiment_complete"):
        render_thank_you()
        return

    if not st.session_state.get("study_started"):
        render_pre_experiment_questionnaire()
        return

    complete = len(st.session_state.transcript) >= st.session_state.target_turns
    if complete:
        render_post_experiment_questionnaire()
        return

    maybe_send_opening(OPENAI_API_KEY)

    native_chat = device_type in {"Mobile", "Tablet"}
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        render_mobile_shell(
            st.session_state.transcript,
            typing=st.session_state.pending_agent_reply,
            device_type=device_type,
            show_device=False,
            use_phone_shell=not native_chat,
        )

    msg = mobile_message_form(disabled=st.session_state.pending_agent_reply, native=native_chat)
    if msg:
        queue_human_message(msg)
        st.rerun()

    if st.session_state.pending_agent_reply:
        time.sleep(st.session_state.get("agent_reply_delay_seconds", 1.2))
        send_pending_agent_reply(OPENAI_API_KEY)


if __name__ == "__main__":
    main()
