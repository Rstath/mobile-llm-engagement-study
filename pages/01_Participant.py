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


def inject_questionnaire_scroll_script(anchor_id: str) -> None:
    """Scroll smoothly to the first missing questionnaire field."""
    if not anchor_id:
        return

    components.html(
        f"""
        <script>
        setTimeout(function () {{
            const parentDoc = window.parent.document;
            const target = parentDoc.getElementById({anchor_id!r});
            if (target) {{
                target.scrollIntoView({{ behavior: "smooth", block: "center" }});
                target.classList.add("question-error-focus");
                setTimeout(function () {{
                    target.classList.remove("question-error-focus");
                }}, 1400);
            }}
        }}, 250);
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
        [data-testid="stSidebarCollapsedControl"] {display: none !important; visibility: hidden !important; width: 0 !important;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding: 1rem clamp(0.75rem, 3vw, 2.5rem) 2rem clamp(0.75rem, 3vw, 2.5rem);
        }

        .participant-questionnaire-page {
            width: 100%;
            max-width: 1100px;
            margin: 0 auto;
        }

        .questionnaire-card h2,
        .questionnaire-card h3 {
            margin-top: 0;
            margin-bottom: 0.75rem;
            font-weight: 700;
            line-height: 1.25;
        }

        .questionnaire-card h2 {
            font-size: clamp(1.35rem, 2.1vw, 1.8rem);
        }

        .questionnaire-card h3 {
            font-size: clamp(1.12rem, 1.5vw, 1.3rem);
        }

        .questionnaire-card p {
            line-height: 1.5;
        }

        .questionnaire-section {
            margin: 1.5rem 0;
            padding: 0;
        }

        .question-anchor {
            scroll-margin-top: 90px;
            border-radius: 8px;
            transition: background-color 0.25s ease, box-shadow 0.25s ease;
        }

        .question-error-focus {
            background: #fff1f2 !important;
            box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.16);
        }

        .field-error {
            color: #dc2626 !important;
            font-size: 0.88rem;
            font-weight: 600;
            margin: -0.25rem 0 0.85rem 0;
            line-height: 1.35;
        }

        .st-bw {
            text-align: center;
        }

        /* Form base */
        .questionnaire-card div[data-testid="stForm"] {
            background: #ffffff !important;
            border: 0 !important;
            padding: 0 !important;
        }

        /* QUESTION TEXT: target Streamlit's actual widget labels */
        .questionnaire-card div[data-testid="stRadio"] > label,
        .questionnaire-card div[data-testid="stTextArea"] > label,
        .questionnaire-card div[data-testid="stCheckbox"] > label {
            display: block !important;
            margin-top: 1.3rem !important;
            margin-bottom: 0.65rem !important;
            padding: 0 !important;
        }

        .questionnaire-card div[data-testid="stRadio"] > label p,
        .questionnaire-card div[data-testid="stTextArea"] > label p,
        .questionnaire-card div[data-testid="stCheckbox"] > label p {
            font-size: 1.08rem !important;
            font-weight: 700 !important;
            line-height: 1.45 !important;
        }


        .question-description {
            display: block !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #111827 !important;
            line-height: 1.55 !important;
            margin: 1.15rem 0 0.55rem 0 !important;
        }

        .question-description + div[data-testid="stCaptionContainer"] p,
        .question-description + div [data-testid="stCaptionContainer"] p {
            font-size: 0.98rem !important;
            font-weight: 500 !important;
            color: #4b5563 !important;
            line-height: 1.55 !important;
        }

        /* Standalone markdown question/description text */
        .questionnaire-section > div[data-testid="stMarkdownContainer"] p,
        .questionnaire-section [data-testid="stMarkdownContainer"] p,
        .questionnaire-card .st-emotion-cache-6urfhe p,
        .questionnaire-card .en7m6i60 p,
        .st-emotion-cache-6urfhe p {
            font-weight: 600 !important;
            font-size: 1rem !important;
            line-height: 1.55 !important;
        }

        /* Captions/help descriptions */
        .questionnaire-card [data-testid="stCaptionContainer"] p,
        .questionnaire-card small,
        .questionnaire-card div[data-testid="stCaptionContainer"] {
            font-size: 0.98rem !important;
            font-weight: 500 !important;
            color: #4b5563 !important;
            line-height: 1.55 !important;
        }

        .questionnaire-card div[role="radiogroup"] {
            display: flex;
            gap: 0.45rem 0.75rem !important;
            padding: 0.6rem 0.8rem !important;
            background: #f8fafc !important;
            border-radius: 8px !important;
            margin-top: 0.35rem !important;
            margin-bottom: 1.25rem !important;
        }

        .questionnaire-card div[role="radiogroup"] > label {
            align-items: center !important;
            padding: 0.55rem 0.65rem !important;
            border-radius: 8px !important;
            border: 1px solid #e5e7eb !important;
            margin-bottom: 0.35rem !important;
        }

        .questionnaire-card div[role="radiogroup"] > label:hover {
            border-color: #93c5fd !important;
            background: #eff6ff !important;
        }

        .questionnaire-card div[role="radiogroup"] > label:has(input:checked) {
            border-color: #2563eb !important;
            background: #dbeafe !important;
        }

        .questionnaire-card div[role="radiogroup"] > label p,
        .questionnaire-card div[role="radiogroup"] label p {
            font-size: 0.97rem !important;
            font-weight: 400 !important;
            color: #374151 !important;
            line-height: 1.4 !important;
        }

        .questionnaire-card input[type="radio"],
        .questionnaire-card input[type="checkbox"] {
            accent-color: #2563eb;
        }

        .questionnaire-card textarea {
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            min-height: 110px !important;
            font-size: 1rem !important;
        }

        .questionnaire-card div[data-testid="stFormSubmitButton"] button {
            border-radius: 8px !important;
            min-height: 44px;
            font-weight: 700;
        }

        @media (max-width: 1024px) {
            .questionnaire-card div[role="radiogroup"] {
                flex-direction: column !important;
                align-items: stretch !important;
            }

            .questionnaire-card div[role="radiogroup"] label {
                width: 100%;
            }
        }

        @media (max-width: 760px) {
            .questionnaire-card {
                border-radius: 0;
                padding: 1rem;
            }

            .questionnaire-section {
                margin: 1.25rem 0;
            }

            .questionnaire-card div[data-testid="stRadio"] > label p,
            .questionnaire-card div[data-testid="stTextArea"] > label p,
            .questionnaire-card div[data-testid="stCheckbox"] > label p {
                font-size: 1.02rem !important;
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
            font-size: 46px;
            line-height: 72px;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_questionnaire_errors(form_name: str) -> Dict[str, str]:
    errors = st.session_state.get("questionnaire_errors", {})
    return errors if st.session_state.get("questionnaire_error_form") == form_name and isinstance(errors, dict) else {}


def field_anchor(field_id: str) -> None:
    st.markdown(f'<div id="{field_id}" class="question-anchor"></div>', unsafe_allow_html=True)


def field_error(errors: Dict[str, str], field_id: str) -> None:
    if errors.get(field_id):
        st.markdown(f'<div class="field-error">{errors[field_id]}</div>', unsafe_allow_html=True)


def set_questionnaire_errors(form_name: str, errors: Dict[str, str]) -> None:
    st.session_state.questionnaire_error_form = form_name
    st.session_state.questionnaire_errors = errors
    st.session_state.questionnaire_first_error = next(iter(errors.keys()), "")


def clear_questionnaire_errors() -> None:
    st.session_state.questionnaire_error_form = ""
    st.session_state.questionnaire_errors = {}
    st.session_state.questionnaire_first_error = ""


def open_questionnaire_card(title: str, caption: str = "") -> None:
    st.markdown('<div class="participant-questionnaire-page">', unsafe_allow_html=True)
    st.subheader(title)
    if caption:
        st.caption(caption)


def close_questionnaire_card() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


def section_heading(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="questionnaire-section"><h3>{title}</h3>', unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def close_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_pre_experiment_questionnaire() -> None:
    """Render pre-questionnaire with dynamic AI section.

    Important: this is intentionally NOT inside st.form, because Streamlit forms do
    not rerun immediately when a radio value changes. Keeping normal widgets lets
    the AI follow-up section appear as soon as the participant selects "Yes".
    """
    form_name = "pre"
    errors = get_questionnaire_errors(form_name)

    open_questionnaire_card(
        "Pre-experiment questionnaire",
        "This study investigates how people interact in short text-based conversations similar to mobile messaging. "
        "Your responses will be used for research purposes only and will remain anonymous. "
        "The questionnaire takes approximately 3–5 minutes to complete. By proceeding, you confirm that you are at least 18 years old and consent to participate in this study.",
    )

    frequency_options = ["Very rarely", "Rarely", "Sometimes", "Often", "Very often"]
    ai_frequency_options = ["Never used", "Very rarely", "Rarely", "Sometimes", "Often", "Very often"]
    emotion_options = ["Very rarely", "Rarely", "Sometimes", "Often", "Very often"]

    section_heading("Demographics")

    field_anchor("age_group")
    age_group = st.radio("What is your age group? *", ["18-24", "25-34", "35-44", "35 +"], index=None, key="pre_age_group")
    field_error(errors, "age_group")

    field_anchor("gender")
    gender = st.radio("What is your gender? *", ["Female", "Male", "Non-binary / Other", "Prefer not to say"], index=None, key="pre_gender")
    field_error(errors, "gender")

    field_anchor("education")
    education = st.radio("What is your highest level of education? *", ["High school", "Undergraduate degree", "Postgraduate degree", "Other"], index=None, key="pre_education")
    field_error(errors, "education")

    field_anchor("messaging_app_use")
    messaging_app_use = st.radio(
        "How often do you use messaging applications (e.g., WhatsApp, Messenger, Viber)? *",
        ["Less than once per day", "1–3 times per day", "4–10 times per day", "More than 10 times per day"],
        index=None,
        key="pre_messaging_app_use",
    )
    field_error(errors, "messaging_app_use")
    close_section()

    section_heading("Mobile Communication Habits")

    field_anchor("text_communication_ease")
    text_communication_ease = st.radio(
        "How easy do you find it to communicate through text messages? *",
        [1, 2, 3, 4, 5],
        index=None,
        horizontal=True,
        captions=["Not easy at all", "", "", "", "Very easy"],
        key="pre_text_communication_ease",
    )
    field_error(errors, "text_communication_ease")

    st.markdown(
        '<p class="question-description">How frequently do you use the following text messaging styles when you communicate? *</p>',
        unsafe_allow_html=True,
    )    
    st.caption("Especially when you want to say a lot in your messages, consider whether you typically write everything in one long message or break your thoughts into multiple shorter consecutive messages.")

    field_anchor("style_one_two_words")
    style_one_two_words = st.radio("One or two words per message", frequency_options, index=None, horizontal=True, key="pre_style_one_two_words")
    field_error(errors, "style_one_two_words")

    field_anchor("style_single_sentence")
    style_single_sentence = st.radio("A single sentence per message", frequency_options, index=None, horizontal=True, key="pre_style_single_sentence")
    field_error(errors, "style_single_sentence")

    field_anchor("style_short_message")
    style_short_message = st.radio("A short message (2-3 sentences)", frequency_options, index=None, horizontal=True, key="pre_style_short_message")
    field_error(errors, "style_short_message")

    field_anchor("style_long_message")
    style_long_message = st.radio("A long detailed message of multiple sentences", frequency_options, index=None, horizontal=True, key="pre_style_long_message")
    field_error(errors, "style_long_message")
    close_section()

    section_heading("Experience with Conversational AI")

    field_anchor("used_ai_before")
    used_ai_before = st.radio(
        "Have you ever used conversational AI assistants to accomplish tasks in the past? *",
        ["Yes", "No"],
        index=None,
        help="For example, general-purpose assistants like ChatGPT, or specific-purpose assistants like customer service chatbots.",
        key="pre_used_ai_before",
    )
    field_error(errors, "used_ai_before")
    close_section()

    ai_general_purpose = None
    ai_specific_purpose = None
    emotion_answers: Dict[str, Any] = {}

    if used_ai_before == "Yes":
        section_heading("Experience with Conversational AI")

        st.markdown(
            '<p class="question-description">How often (if at all) do you use conversational AI assistants to accomplish various tasks? *</p>',
            unsafe_allow_html=True,
        )

        field_anchor("ai_general_purpose")
        ai_general_purpose = st.radio(
            "General-purpose AI assistants (e.g. ChatGPT, Gemini, Claude)",
            ai_frequency_options,
            index=None,
            horizontal=True,
            key="pre_ai_general_purpose",
        )
        field_error(errors, "ai_general_purpose")

        field_anchor("ai_specific_purpose")
        ai_specific_purpose = st.radio(
            "Specific-purpose AI assistants (e.g. customer service chatbots)",
            ai_frequency_options,
            index=None,
            horizontal=True,
            key="pre_ai_specific_purpose",
        )
        field_error(errors, "ai_specific_purpose")

        st.markdown(
            '<p class="question-description">Reflecting on your experience in interacting with various AI assistants, how often do you feel... *</p>',
            unsafe_allow_html=True,
        )
        emotion_rows = [
            "Insecure", "Helpless", "Excluded", "Threatened", "Critical", "Frustrated",
            "Humiliated", "Bitter", "Hurt", "Guilty", "Powerless", "Lonely",
            "Powerful", "Excited", "Proud", "Hopeful", "Startled", "Disapproving",
            "Awful", "Repelled",
        ]
        for emotion in emotion_rows:
            emotion_key = f"emotion_{emotion.lower()}"
            field_anchor(emotion_key)
            emotion_answers[emotion.lower()] = st.radio(
                emotion,
                emotion_options,
                index=None,
                horizontal=True,
                key=f"pre_emotion_{emotion.lower()}",
            )
            field_error(errors, emotion_key)

        close_section()

    field_anchor("consent")
    consent = st.checkbox(
        "I understand that my conversation and questionnaire answers will be saved for research analysis. *",
        key="pre_consent",
    )
    field_error(errors, "consent")

    submitted = st.button("Start conversation", use_container_width=True, type="primary")

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

        validation_errors: Dict[str, str] = {}
        required_fields = {
            "age_group": age_group,
            "gender": gender,
            "education": education,
            "messaging_app_use": messaging_app_use,
            "text_communication_ease": text_communication_ease,
            "style_one_two_words": style_one_two_words,
            "style_single_sentence": style_single_sentence,
            "style_short_message": style_short_message,
            "style_long_message": style_long_message,
            "used_ai_before": used_ai_before,
            **(
                {
                    "ai_general_purpose": ai_general_purpose,
                    "ai_specific_purpose": ai_specific_purpose,
                }
                if used_ai_before == "Yes"
                else {}
            ),
        }
        for field_id, value in required_fields.items():
            if value in (None, ""):
                validation_errors[field_id] = "This question is required."

        if used_ai_before == "Yes":
            for emotion, value in emotion_answers.items():
                if value in (None, ""):
                    validation_errors[f"emotion_{emotion}"] = "This question is required."

        if not consent:
            validation_errors["consent"] = "Please confirm consent before continuing."

        if validation_errors:
            set_questionnaire_errors(form_name, validation_errors)
            st.rerun()
        else:
            clear_questionnaire_errors()
            start_remote_participant_session(pre_experiment_answers=answers)
            st.rerun()

    if errors:
        inject_questionnaire_scroll_script(st.session_state.get("questionnaire_first_error", ""))

    close_questionnaire_card()


def render_post_experiment_questionnaire() -> None:
    form_name = "post"
    errors = get_questionnaire_errors(form_name)

    open_questionnaire_card("Post-experiment questionnaire", "Please answer the following questions about the conversation you just completed.")

    with st.form("post_experiment_questionnaire"):
        section_heading("Conversation experience")

        field_anchor("engaging")
        engaging = st.radio("How engaging did you find the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not engaging at all", "", "", "", "Very engaging"])
        field_error(errors, "engaging")

        field_anchor("willing_continue")
        willing_continue = st.radio("How willing would you be to continue this conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not willing at all", "", "", "", "Very willing"])
        field_error(errors, "willing_continue")

        field_anchor("coherent")
        coherent = st.radio("How coherent were the responses during the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not coherent at all", "", "", "", "Very coherent"])
        field_error(errors, "coherent")

        field_anchor("on_topic")
        on_topic = st.radio("To what extent did the conversation stay on topic? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Completely"])
        field_error(errors, "on_topic")

        field_anchor("natural")
        natural = st.radio("How natural did the conversation feel? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not natural at all", "", "", "", "Very natural"])
        field_error(errors, "natural")

        field_anchor("smooth")
        smooth = st.radio("How smooth was the flow of the conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Very much"])
        field_error(errors, "smooth")

        field_anchor("repetitive")
        repetitive = st.radio("Did the conversation feel repetitive at any point? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all repetitive", "", "", "", "Very repetitive"])
        field_error(errors, "repetitive")

        field_anchor("followups")
        followups = st.radio("Did the system ask relevant or helpful follow-up questions? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Not at all", "", "", "", "Very much"])
        field_error(errors, "followups")

        field_anchor("balanced")
        balanced = st.radio("How balanced did the conversation feel? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Very unbalanced", "", "", "", "Very balanced"])
        field_error(errors, "balanced")

        field_anchor("overall")
        overall = st.radio("Overall, how would you rate this conversation? *", [1, 2, 3, 4, 5], index=None, horizontal=True, captions=["Very poor", "", "", "", "Excellent"])
        field_error(errors, "overall")
        close_section()

        section_heading("Open feedback")

        field_anchor("liked")
        liked = st.text_area("Please mention up to 3 things that you liked about the conversation. *")
        field_error(errors, "liked")

        field_anchor("disliked")
        disliked = st.text_area("Please mention up to 3 things that you did not like about the conversation. *")
        field_error(errors, "disliked")

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

        validation_errors: Dict[str, str] = {}
        required_fields = {
            "engaging": engaging,
            "willing_continue": willing_continue,
            "coherent": coherent,
            "on_topic": on_topic,
            "natural": natural,
            "smooth": smooth,
            "repetitive": repetitive,
            "followups": followups,
            "balanced": balanced,
            "overall": overall,
            "liked": liked.strip(),
            "disliked": disliked.strip(),
        }
        for field_id, value in required_fields.items():
            if value in (None, ""):
                validation_errors[field_id] = "This question is required."

        if validation_errors:
            set_questionnaire_errors(form_name, validation_errors)
            st.rerun()
        else:
            clear_questionnaire_errors()
            st.session_state.post_experiment_answers = answers
            st.session_state.post_experiment_complete = True
            auto_save_when_complete(EMBEDDING_MODEL)
            st.rerun()

    if errors:
        inject_questionnaire_scroll_script(st.session_state.get("questionnaire_first_error", ""))

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

    msg = mobile_message_form(
        disabled=st.session_state.pending_agent_reply,
        native=native_chat,
    )
    if msg:
        queue_human_message(msg)
        st.rerun()

    if st.session_state.pending_agent_reply:
        time.sleep(st.session_state.get("agent_reply_delay_seconds", 1.2))
        send_pending_agent_reply(OPENAI_API_KEY)


if __name__ == "__main__":
    main()
