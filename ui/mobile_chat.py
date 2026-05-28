import html
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

CHAT_NAME = "Alex"


def inject_mobile_css():
    st.markdown(
        """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .phone-shell {
        width: min(100%, 410px);
        max-width: 410px;
        margin: 0 auto;
        border: clamp(7px, 2.5vw, 13px) solid #1f1f1f;
        border-radius: clamp(26px, 7vw, 38px);
        background: #111;
        box-shadow: 0 12px 40px rgba(0,0,0,0.28);
        padding: clamp(3px, 1.5vw, 6px);
    }

    .phone-screen {
        background: #f2f2f7;
        border-radius: clamp(18px, 5vw, 28px);
        height: min(86vh, 760px);
        min-height: 560px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }

    .status-bar {
        height: 28px;
        padding: 7px 16px 0 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
        font-weight: 700;
        color: #111;
        background: #f8f8fb;
    }

    .status-icons {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
    }

    .signal {
        letter-spacing: -1px;
        font-size: 11px;
    }

    .battery {
        width: 24px;
        height: 11px;
        border: 1.8px solid #111;
        border-radius: 3px;
        position: relative;
        box-sizing: border-box;
    }

    .battery::after {
        content: "";
        position: absolute;
        right: -4px;
        top: 3px;
        width: 2px;
        height: 5px;
        background: #111;
        border-radius: 1px;
    }

    .battery-level {
        height: 100%;
        width: 76%;
        background: #111;
        border-radius: 1px;
    }

    .phone-header {
        text-align: center;
        font-weight: 700;
        padding: 10px;
        background: #f8f8fb;
        border-bottom: 1px solid #dedee5;
        color: #111;
    }

    .phone-avatar {
        width: 34px;
        height: 34px;
        margin: 0 auto 4px auto;
        border-radius: 50%;
        background: linear-gradient(135deg, #c7d2fe, #60a5fa);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
        font-weight: 800;
    }

    .phone-messages {
        padding: clamp(8px, 2.5vw, 12px);
        overflow-y: auto;
        flex: 1;
        min-height: 0;
        scroll-behavior: smooth;
        background:
            radial-gradient(circle at top left, rgba(255,255,255,0.9), transparent 28%),
            #f2f2f7;
    }

    .message-row {
        display: flex;
        flex-direction: column;
        margin: 7px 0 9px 0;
        width: 100%;
    }

    .message-row.human-row {
        align-items: flex-end;
    }

    .message-row.agent-row {
        align-items: flex-start;
    }

    .agent-message-wrap {
        display: flex;
        align-items: flex-end;
        gap: 6px;
        max-width: 86%;
    }

    .agent-mini-avatar {
        width: 24px;
        height: 24px;
        flex: 0 0 24px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c7d2fe, #60a5fa);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 11px;
        font-weight: 800;
        margin-bottom: 1px;
    }

    .bubble {
        display: inline-block;
        width: fit-content;
        max-width: min(78%, 300px);
        padding: 9px 13px;
        border-radius: 19px;
        font-size: clamp(14px, 3.6vw, 15px);
        line-height: 1.35;
        word-wrap: break-word;
        overflow-wrap: anywhere;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    .agent-message-wrap .bubble {
        max-width: 100%;
    }

    .human {
        background: #0A84FF;
        color: white;
        border-bottom-right-radius: 5px;
    }

    .agent {
        background: #E5E5EA;
        color: #111;
        border-bottom-left-radius: 5px;
    }

    .speaker-label {
        font-size: 11px;
        color: #777;
        margin-bottom: 2px;
        padding: 0 4px;
    }

    .agent-row .speaker-label {
        padding-left: 34px;
    }

    .message-meta {
        font-size: 10.5px;
        color: #8e8e93;
        margin-top: 3px;
        padding: 0 4px;
        line-height: 1.1;
    }

    .human-row .message-meta {
        text-align: right;
    }

    .agent-row .message-meta {
        text-align: left;
        padding-left: 34px;
    }

    .typing-bubble {
        min-width: 42px;
        padding: 10px 12px;
    }

    .typing-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        margin: 0 1px;
        border-radius: 50%;
        background: #8e8e93;
        animation: typingPulse 1.2s infinite ease-in-out;
    }

    .typing-dot:nth-child(2) {
        animation-delay: 0.16s;
    }

    .typing-dot:nth-child(3) {
        animation-delay: 0.32s;
    }

    @keyframes typingPulse {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.45; }
        40% { transform: translateY(-3px); opacity: 1; }
    }

    .phone-message-form div[data-testid="stForm"] {
        width: min(calc(100% - 64px), 350px) !important;
        max-width: 350px !important;
        margin: calc(-1 * var(--composer-height, 92px)) auto 0 auto !important;
        background: transparent;
        border: none;
        padding: 0 0 12px 0 !important;
        position: relative;
        z-index: 5;
        box-sizing: border-box !important;
    }

    .phone-message-form div[data-testid="stForm"] > div,
    .native-message-form div[data-testid="stForm"] > div {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-end !important;
        gap: 8px !important;
        width: 100% !important;
        flex-wrap: nowrap !important;
    }

    .phone-message-form div[data-testid="column"],
    .native-message-form div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        flex: unset !important;
    }

    .phone-message-form div[data-testid="column"]:first-child,
    .native-message-form div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    .phone-message-form div[data-testid="column"]:last-child,
    .native-message-form div[data-testid="column"]:last-child {
        flex: 0 0 42px !important;
        width: 42px !important;
        min-width: 42px !important;
    }

    .phone-message-form div[data-testid="stTextArea"],
    .native-message-form div[data-testid="stTextArea"] {
        width: 100% !important;
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    .phone-message-form div[data-testid="stTextArea"] textarea,
    .native-message-form div[data-testid="stTextArea"] textarea {
        border-radius: 22px !important;
        border: 1px solid #d1d1d6 !important;
        background-color: #ffffff !important;
        color: #111111 !important;
        padding: 10px 16px !important;
        font-size: 15px !important;
        min-height: 42px !important;
        box-shadow: none !important;
        outline: none !important;
        transition: border-color 0.15s ease;
        cursor: text !important;
        caret-color: #0A84FF !important;
        resize: vertical !important;
        overflow-y: auto !important;
        scrollbar-width: none !important;
        max-height: min(26vh, 150px) !important;
        line-height: 1.35 !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #0A84FF !important;
        box-shadow: 0 0 0 1px rgba(10,132,255,0.15) !important;
    }

    div[data-testid="stTextArea"] textarea:focus-visible {
        outline: none !important;
        caret-color: #0A84FF !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #8e8e93 !important;
        opacity: 1 !important;
        font-weight: 400 !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"],
    .native-message-form div[data-testid="stFormSubmitButton"] {
        flex: 0 0 42px !important;
        width: 42px !important;
        min-width: 42px !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button,
    .native-message-form div[data-testid="stFormSubmitButton"] button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        padding: 0 !important;
        background: #0A84FF !important;
        color: white !important;
        border: none !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button:hover,
    .native-message-form div[data-testid="stFormSubmitButton"] button:hover {
        background: #006FE6 !important;
        color: white !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button:disabled,
    .native-message-form div[data-testid="stFormSubmitButton"] button:disabled {
        background: #b8b8bd !important;
        color: white !important;
    }

    .phone-message-form div[data-testid="stForm"] > div {
        max-width: 100% !important;
    }

    .phone-message-form div[data-testid="stTextArea"] textarea {
        height: 44px;
        resize: none !important;
        overflow-x: hidden !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"],
    .phone-message-form div[data-testid="stFormSubmitButton"] button {
        flex: 0 0 42px !important;
        align-self: flex-end !important;
    }


    /* Keep the simulated-phone composer visually inside the phone screen.
       As the textarea grows, the spacer and negative margin are recalculated
       from --composer-height, so the composer expands upward instead of
       dropping below the frame. */
    .phone-shell {
        position: relative !important;
    }

    .phone-message-form div[data-testid="stForm"],
    body.phone-frame-active .native-message-form div[data-testid="stForm"] {
        overflow: visible !important;
    }

    .phone-message-form div[data-testid="stTextAreaRootElement"],
    body.phone-frame-active .native-message-form div[data-testid="stTextAreaRootElement"] {
        max-width: 100% !important;
        overflow: hidden !important;
        border-radius: 22px !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"],
    body.phone-frame-active .native-message-form div[data-testid="stFormSubmitButton"] {
        padding-bottom: 1px !important;
    }


    .native-chat-screen {
        width: 100%;
        max-width: 760px;
        margin: 0 auto;
        height: calc(var(--chat-vvh, 100dvh) - var(--composer-height, 78px));
        min-height: 0;
        background: #f2f2f7;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }

    .native-chat-screen .phone-messages {
        padding-bottom: 12px !important;
    }

    .native-message-form div[data-testid="stForm"] {
        position: fixed !important;
        left: 50% !important;
        bottom: var(--keyboard-offset, 0px) !important;
        transform: translateX(-50%) !important;
        width: 100% !important;
        max-width: 760px !important;
        margin: 0 auto !important;
        padding: 8px max(12px, env(safe-area-inset-right)) max(10px, env(safe-area-inset-bottom)) max(12px, env(safe-area-inset-left)) !important;
        background: rgba(242, 242, 247, 0.96) !important;
        border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
        box-sizing: border-box !important;
        z-index: 9999 !important;
    }

    .native-message-form div[data-testid="stForm"] > div {
        align-items: flex-end !important;
        gap: 8px !important;
    }

    .native-message-form div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    .native-message-form div[data-testid="column"]:last-child {
        flex: 0 0 44px !important;
        width: 44px !important;
        min-width: 44px !important;
    }

    .native-message-form div[data-testid="stTextArea"] textarea {
        min-height: 44px !important;
        height: 44px;
        max-height: min(30dvh, 160px) !important;
        font-size: 16px !important;
        -webkit-text-size-adjust: 100%;
        touch-action: manipulation;
        resize: none !important;
        overflow-y: auto !important;
        line-height: 1.35 !important;
    }

    .native-message-form div[data-testid="stFormSubmitButton"],
    .native-message-form div[data-testid="stFormSubmitButton"] button {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
    }

    /* Safety: if a phone shell is visible, the composer must behave like the
       simulated phone composer, not like the full-width native mobile composer. */
    body.phone-frame-active .native-message-form div[data-testid="stForm"] {
        position: relative !important;
        left: auto !important;
        bottom: auto !important;
        transform: none !important;
        width: min(calc(100% - 64px), 350px) !important;
        max-width: 350px !important;
        margin: calc(-1 * var(--composer-height, 92px)) auto 0 auto !important;
        padding: 0 0 12px 0 !important;
        background: transparent !important;
        border: none !important;
        z-index: 20 !important;
        box-sizing: border-box !important;
    }

    body.phone-frame-active .native-message-form div[data-testid="stTextArea"] textarea {
        max-height: min(26vh, 150px) !important;
        font-size: 15px !important;
    }

    body.phone-frame-active .native-chat-screen {
        width: min(100%, 410px) !important;
        max-width: 410px !important;
    }

    div[data-testid="stTextArea"] textarea::-webkit-scrollbar {
        display: none !important;
    }

    @media (hover: none) and (pointer: coarse), (max-width: 1024px) {
        .native-message-form div[data-testid="stForm"] {
            width: 100vw !important;
            max-width: 100vw !important;
        }

        .native-chat-screen {
            width: 100vw;
            max-width: 100vw;
            height: calc(var(--chat-vvh, 100dvh) - var(--composer-height, 78px));
        }
    }

    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.35rem;
            padding-right: 0.35rem;
        }

        .phone-shell {
            width: 100%;
            max-width: 100%;
        }

        .phone-screen {
            height: 92dvh;
            min-height: min(560px, 92dvh);
        }

        .status-bar {
            padding-left: 14px;
            padding-right: 14px;
        }

        .phone-header {
            padding-top: 8px;
            padding-bottom: 8px;
        }

        .phone-avatar {
            width: 30px;
            height: 30px;
            font-size: 14px;
        }

        .bubble {
            max-width: 82%;
        }

        .phone-message-form div[data-testid="stForm"] {
            width: min(calc(100% - 48px), 340px) !important;
            max-width: 340px !important;
        }
    }

    @media (max-height: 700px) {
        .phone-screen {
            height: 88vh;
            min-height: 500px;
        }

        .phone-avatar {
            width: 28px;
            height: 28px;
        }

        .phone-header {
            padding: 7px 10px;
        }

        .phone-message-form div[data-testid="stForm"] {
            width: min(calc(100% - 48px), 340px) !important;
            max-width: 340px !important;
        }
    }

    .st-c9,
    .st-bs,
    .st-ee,
    .st-di {
        background-color: transparent !important;
    }

    .st-c8,
    .st-br,
    .st-d3,
    .st-cm,
    .st-ed,
    .st-ek {
        border-bottom-color: transparent !important;
    }

    .st-c7,
    .st-bq,
    .st-d2,
    .st-cl,
    .st-ec,
    .st-ej {
        border-top-color: transparent !important;
    }

    .st-c6,
    .st-bp,
    .st-d1,
    .st-ck,
    .st-eb,
    .st-ei {
        border-right-color: transparent !important;
    }

    .st-c5,
    .st-bo,
    .st-d0,
    .st-cj,
    .st-ea {
        border-left-color: transparent !important;
    }

    .st-bx,
    .st-bc,
    .st-eb {
        overflow: visible !important;
    }



    /* Final visual restore for the simulated phone composer.
       Streamlit/BaseWeb hashed classes can override borders/backgrounds,
       so these selectors intentionally target the stable data-testid attributes. */
    .phone-shell {
        border: clamp(7px, 2.5vw, 13px) solid #1f1f1f !important;
        background: #111 !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.28) !important;
    }

    .phone-screen,
    .native-chat-screen {
        background: #f2f2f7 !important;
    }

    .phone-message-form div[data-testid="stForm"],
    body.phone-frame-active .native-message-form div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .phone-message-form div[data-testid="stTextArea"] label,
    .native-message-form div[data-testid="stTextArea"] label {
        display: none !important;
    }

    .phone-message-form div[data-testid="stTextAreaRootElement"],
    .phone-message-form div[data-baseweb="base-input"],
    body.phone-frame-active .native-message-form div[data-testid="stTextAreaRootElement"],
    body.phone-frame-active .native-message-form div[data-baseweb="base-input"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid #d1d1d6 !important;
        border-radius: 22px !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }

    .phone-message-form div[data-baseweb="base-input"],
    body.phone-frame-active .native-message-form div[data-baseweb="base-input"] {
        border: 0 !important;
    }

    .phone-message-form textarea[placeholder="Message..."],
    body.phone-frame-active .native-message-form textarea[placeholder="Message..."] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 0 !important;
        border-radius: 22px !important;
        box-shadow: none !important;
        caret-color: #0A84FF !important;
        padding: 10px 16px !important;
    }

    .phone-message-form textarea[placeholder="Message..."]:focus,
    body.phone-frame-active .native-message-form textarea[placeholder="Message..."]:focus {
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .phone-message-form div[data-testid="stTextAreaRootElement"]:focus-within,
    body.phone-frame-active .native-message-form div[data-testid="stTextAreaRootElement"]:focus-within {
        border-color: #0A84FF !important;
        box-shadow: 0 0 0 1px rgba(10,132,255,0.15) !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button,
    body.phone-frame-active .native-message-form div[data-testid="stFormSubmitButton"] button {
        background: #0A84FF !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50% !important;
        box-shadow: none !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button p,
    body.phone-frame-active .native-message-form div[data-testid="stFormSubmitButton"] button p {
        color: #ffffff !important;
        margin: 0 !important;
        line-height: 1 !important;
    }



    /* Final position fix: the desktop/simulated-phone composer must sit inside
       the phone screen at the bottom, using the same placement as the inspected DOM. */
    #phone-form-anchor.phone-message-form {
        width: 100% !important;
        position: relative !important;
        z-index: 30 !important;
        flex: 0 0 auto !important;
    }

    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stForm"] {
        position: relative !important;
        left: auto !important;
        bottom: auto !important;
        transform: none !important;
        width: min(calc(100% - 64px), 350px) !important;
        max-width: 350px !important;
        margin: calc(-1 * var(--composer-height, 92px)) auto 0 auto !important;
        padding: 0 0 12px 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        box-sizing: border-box !important;
        z-index: 40 !important;
        overflow: visible !important;
    }

    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stForm"] > div {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-end !important;
        gap: 8px !important;
        width: 100% !important;
        flex-wrap: nowrap !important;
    }

    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="column"]:last-child {
        flex: 0 0 42px !important;
        width: 42px !important;
        min-width: 42px !important;
    }

    .phone-message-form-source {
        display: contents !important;
    }



    /* =========================================================
       FINAL COMPOSER SAME-LINE LOCK
       Keeps textarea + send button in one row at every resolution.
       This must stay near the end of the stylesheet so it wins over
       Streamlit/BaseWeb responsive column rules.
       ========================================================= */
    .phone-message-form div[data-testid="stForm"],
    .native-message-form div[data-testid="stForm"],
    body.phone-frame-active .native-message-form div[data-testid="stForm"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stForm"] {
        box-sizing: border-box !important;
        overflow: visible !important;
    }

    .phone-message-form div[data-testid="stForm"] > div,
    .native-message-form div[data-testid="stForm"] > div,
    body.phone-frame-active .native-message-form div[data-testid="stForm"] > div,
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stForm"] > div,
    .phone-message-form div[data-testid="stHorizontalBlock"],
    .native-message-form div[data-testid="stHorizontalBlock"],
    body.phone-frame-active .native-message-form div[data-testid="stHorizontalBlock"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: flex-end !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }

    .phone-message-form div[data-testid="column"],
    .native-message-form div[data-testid="column"],
    body.phone-frame-active .native-message-form div[data-testid="column"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .phone-message-form div[data-testid="column"]:first-child,
    .native-message-form div[data-testid="column"]:first-child,
    body.phone-frame-active .native-message-form div[data-testid="column"]:first-child,
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="column"]:first-child {
        flex: 1 1 calc(100% - 50px) !important;
        width: calc(100% - 50px) !important;
        min-width: 0 !important;
        max-width: calc(100% - 50px) !important;
    }

    .phone-message-form div[data-testid="column"]:last-child,
    .native-message-form div[data-testid="column"]:last-child,
    body.phone-frame-active .native-message-form div[data-testid="column"]:last-child,
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="column"]:last-child {
        flex: 0 0 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        align-self: flex-end !important;
    }

    .phone-message-form div[data-testid="stTextArea"],
    .native-message-form div[data-testid="stTextArea"],
    body.phone-frame-active .native-message-form div[data-testid="stTextArea"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stTextArea"],
    .phone-message-form div[data-testid="stTextAreaRootElement"],
    .native-message-form div[data-testid="stTextAreaRootElement"],
    body.phone-frame-active .native-message-form div[data-testid="stTextAreaRootElement"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stTextAreaRootElement"] {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    .phone-message-form textarea[placeholder="Message..."],
    .native-message-form textarea[placeholder="Message..."],
    body.phone-frame-active .native-message-form textarea[placeholder="Message..."],
    .phone-screen #phone-form-anchor.phone-message-form textarea[placeholder="Message..."] {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        resize: none !important;
        overflow-x: hidden !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"],
    .native-message-form div[data-testid="stFormSubmitButton"],
    body.phone-frame-active .native-message-form div[data-testid="stFormSubmitButton"],
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stFormSubmitButton"] {
        flex: 0 0 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        align-self: flex-end !important;
    }

    .phone-message-form div[data-testid="stFormSubmitButton"] button,
    .native-message-form div[data-testid="stFormSubmitButton"] button,
    body.phone-frame-active .native-message-form div[data-testid="stFormSubmitButton"] button,
    .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stFormSubmitButton"] button {
        flex: 0 0 42px !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        min-height: 42px !important;
        max-width: 42px !important;
        max-height: 42px !important;
        align-self: flex-end !important;
        flex-shrink: 0 !important;
    }

    @media (max-width: 480px) {
        .phone-message-form div[data-testid="stForm"],
        body.phone-frame-active .native-message-form div[data-testid="stForm"],
        .phone-screen #phone-form-anchor.phone-message-form div[data-testid="stForm"] {
            width: min(calc(100% - 44px), 340px) !important;
            max-width: 340px !important;
        }

        .native-message-form div[data-testid="stForm"] {
            width: 100vw !important;
            max-width: 100vw !important;
        }
    }


    .participant-complete {
        max-width: 390px;
        margin: 0.75rem auto;
        text-align: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Keep focus on the message input. This is inside an iframe, so it will not print as raw text.
    components.html(
        """
        <script>
        (function () {
            const parentDoc = window.parent.document;
            const parentWin = window.parent;

            function syncFrameModeClass() {
                const hasPhoneShell = !!parentDoc.querySelector('.phone-shell');
                parentDoc.body.classList.toggle('phone-frame-active', hasPhoneShell);
            }

            function getComposer() {
                return parentDoc.querySelector('.native-message-form div[data-testid="stForm"]') ||
                       parentDoc.querySelector('.phone-message-form div[data-testid="stForm"]') ||
                       parentDoc.querySelector('div[data-testid="stForm"]');
            }

            function getTextarea() {
                return parentDoc.querySelector('textarea[placeholder="Message..."]');
            }

            function movePhoneFormIntoFrame() {
                const anchor = parentDoc.querySelector('#phone-form-anchor.phone-message-form');
                const textarea = getTextarea();
                if (!anchor || !textarea || parentDoc.querySelector('.native-message-form')) return;
                const form = textarea.closest('div[data-testid="stForm"]');
                if (!form || anchor.contains(form)) return;
                const wrapper = form.closest('div[data-testid="stLayoutWrapper"]') || form;
                anchor.appendChild(wrapper);
            }

            function scrollMessagesToBottom() {
                const messages = parentDoc.querySelector('#phone-messages');
                if (messages) messages.scrollTop = messages.scrollHeight;
            }

            function updateViewportVars() {
                syncFrameModeClass();
                movePhoneFormIntoFrame();
                const root = parentDoc.documentElement;
                const vv = parentWin.visualViewport;
                const viewportHeight = vv ? vv.height : parentWin.innerHeight;
                const keyboardOffset = vv ? Math.max(0, parentWin.innerHeight - vv.height - vv.offsetTop) : 0;
                const composer = getComposer();
                const composerHeight = composer ? composer.getBoundingClientRect().height : 78;

                root.style.setProperty('--chat-vvh', viewportHeight + 'px');
                root.style.setProperty('--keyboard-offset', keyboardOffset + 'px');
                root.style.setProperty('--composer-height', Math.ceil(composerHeight) + 'px');
                scrollMessagesToBottom();
            }

            function autoGrowTextArea() {
                const textarea = getTextarea();
                if (!textarea) return;
                const isNative = !!parentDoc.querySelector('.native-message-form');
                const viewportHeight = parentWin.visualViewport ? parentWin.visualViewport.height : parentWin.innerHeight;
                const phoneScreen = parentDoc.querySelector('.phone-screen');
                const screenHeight = phoneScreen ? phoneScreen.getBoundingClientRect().height : viewportHeight;
                const maxHeight = isNative
                    ? Math.min(viewportHeight * 0.30, 160)
                    : Math.min(screenHeight * 0.24, 150);
                textarea.style.height = '44px';
                textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px';
                textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
                textarea.scrollTop = textarea.scrollHeight;
                updateViewportVars();
            }

            function bindAutoGrow() {
                movePhoneFormIntoFrame();
                const textarea = getTextarea();
                if (!textarea) return;
                textarea.setAttribute('rows', '1');
                textarea.setAttribute('autocomplete', 'off');
                textarea.setAttribute('autocorrect', 'on');
                textarea.setAttribute('autocapitalize', 'sentences');
                if (textarea.dataset.autogrowBound === '1') {
                    autoGrowTextArea();
                    return;
                }
                textarea.dataset.autogrowBound = '1';
                textarea.addEventListener('input', autoGrowTextArea);
                textarea.addEventListener('focus', function () {
                    setTimeout(autoGrowTextArea, 60);
                    setTimeout(autoGrowTextArea, 300);
                });
                textarea.addEventListener('blur', updateViewportVars);
                autoGrowTextArea();
            }

            syncFrameModeClass();
            if (parentWin.visualViewport) {
                parentWin.visualViewport.addEventListener('resize', updateViewportVars);
                parentWin.visualViewport.addEventListener('scroll', updateViewportVars);
            }
            parentWin.addEventListener('resize', updateViewportVars);

            setInterval(bindAutoGrow, 150);
            setInterval(updateViewportVars, 250);
        })();
        </script>
        """,
        height=0,
    )


def _message_time(turn: Dict[str, Any]) -> str:
    """Return hour/minute only, using the saved message timestamp when available."""
    value = (
        turn.get("timestamp")
        or turn.get("created_at")
        or turn.get("datetime")
        or turn.get("time")
    )

    if isinstance(value, datetime):
        return value.strftime("%H:%M")

    if isinstance(value, str) and value.strip():
        clean_value = value.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(clean_value[:19], fmt).strftime("%H:%M")
            except ValueError:
                pass

        # Last safe fallback for ISO strings with timezone suffixes.
        try:
            return datetime.fromisoformat(clean_value.replace("Z", "+00:00")).strftime("%H:%M")
        except ValueError:
            pass

    return datetime.now().strftime("%H:%M")


def render_mobile_shell(
    transcript: List[Dict[str, Any]],
    typing: bool = False,
    agent_name: str = CHAT_NAME,
    device_type: Optional[str] = None,
    show_device: bool = False,
    use_phone_shell: bool = True,
):
    """
    Render the mobile chat UI.

    Use typing=True while the agent response is delayed/pending.
    Use show_device=True only in the researcher/admin view; keep it False for participants.
    """
    inject_mobile_css()

    current_time = datetime.now().strftime("%H:%M")
    initial = agent_name[:1].upper() if agent_name else "A"

    html_parts = []
    if use_phone_shell:
        html_parts.append('<div class="phone-shell">')
        html_parts.append('<div class="phone-screen">')
        html_parts.append('<div class="status-bar">')
        html_parts.append(f'<div>{current_time}</div>')
        html_parts.append('<div class="status-icons">')
        html_parts.append('<span class="signal">●●●</span>')
        html_parts.append('<span>5G</span>')
        html_parts.append('<div class="battery"><div class="battery-level"></div></div>')
        html_parts.append('</div>')
        html_parts.append('</div>')
    else:
        html_parts.append('<div class="native-chat-screen">')

    html_parts.append('<div class="phone-header">')
    html_parts.append(f'<div class="phone-avatar">{html.escape(initial)}</div>')
    html_parts.append(html.escape(agent_name))
    if show_device and device_type:
        html_parts.append(f'<div class="message-meta">Device: {html.escape(device_type)}</div>')
    html_parts.append('</div>')

    html_parts.append('<div class="phone-messages" id="phone-messages">')

    for turn in transcript:
        speaker = turn.get("speaker", "")
        is_human = speaker == "Human"
        row_cls = "human-row" if is_human else "agent-row"
        bubble_cls = "human" if is_human else "agent"
        label = "You" if is_human else agent_name
        safe_text = html.escape(str(turn.get("text", ""))).replace("\n", "<br>")
        msg_time = _message_time(turn)
        meta = f"Delivered · {msg_time}" if is_human else msg_time

        html_parts.append(f'<div class="message-row {row_cls}">')
        html_parts.append(f'<div class="speaker-label">{html.escape(label)}</div>')
        if is_human:
            html_parts.append(f'<div class="bubble {bubble_cls}">{safe_text}</div>')
        else:
            html_parts.append('<div class="agent-message-wrap">')
            html_parts.append(f'<div class="agent-mini-avatar">{html.escape(initial)}</div>')
            html_parts.append(f'<div class="bubble {bubble_cls}">{safe_text}</div>')
            html_parts.append('</div>')
        html_parts.append(f'<div class="message-meta">{html.escape(meta)}</div>')
        html_parts.append('</div>')

    if typing:
        html_parts.append('<div class="message-row agent-row">')
        html_parts.append(f'<div class="speaker-label">{html.escape(agent_name)}</div>')
        html_parts.append('<div class="agent-message-wrap">')
        html_parts.append(f'<div class="agent-mini-avatar">{html.escape(initial)}</div>')
        html_parts.append('<div class="bubble agent typing-bubble" aria-label="Agent is typing">')
        html_parts.append('<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>')
        html_parts.append('</div>')
        html_parts.append('</div>')
        html_parts.append('</div>')

    html_parts.append('</div>')
    if use_phone_shell:
        html_parts.append('<div id="phone-form-anchor" class="phone-message-form"></div>')
    html_parts.append('</div>')
    if use_phone_shell:
        html_parts.append('</div>')

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

    # Auto-scroll safely through a hidden component iframe. Do not append this script to st.markdown,
    # otherwise Streamlit can display it as raw text inside the chat.
    components.html(
        """
        <script>
        const scrollMessages = () => {
            const messages = window.parent.document.querySelector('#phone-messages');
            if (messages) {
                messages.scrollTop = messages.scrollHeight;
            }
        };
        scrollMessages();
        setTimeout(scrollMessages, 80);
        setTimeout(scrollMessages, 250);
        </script>
        """,
        height=0,
    )


def mobile_message_form(disabled: bool = False, native: bool = False):
    wrapper_class = "native-message-form" if native else "phone-message-form-source"
    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)

    with st.form("mobile_message_form", clear_on_submit=True):
        col_input, col_button = st.columns([1, 0.13])
        with col_input:
            text = st.text_area(
                "Message",
                placeholder="Message...",
                label_visibility="collapsed",
                disabled=disabled,
                key="mobile_message_input",
                height=68,  # Streamlit 1.45 requires text_area height >= 68; CSS visually keeps it compact.
            )
        with col_button:
            submitted = st.form_submit_button("➤", disabled=disabled)

    st.markdown("</div>", unsafe_allow_html=True)
    return text.strip() if submitted and text and text.strip() else None
