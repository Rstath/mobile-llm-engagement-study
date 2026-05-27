import json
import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from scipy import stats

from config.settings import APP_TITLE, OPENAI_API_KEY, EMBEDDING_MODEL
from config.topics import TOPICS
from config.agent_styles import ENGAGEMENT_STYLES
from database.db import init_db, load_all
from utils.conversation import (
    auto_save_when_complete,
    compute_current_metrics,
    current_style,
    current_topic,
    initialize_conversation_state,
    reset_conversation,
    save_current_conversation,
    update_device_type_from_headers,
)

LIKERT_5 = {
    "Very rarely": 1,
    "Rarely": 2,
    "Sometimes": 3,
    "Often": 4,
    "Very often": 5,
}
AI_FREQ = {
    "Never used": 0,
    "Very rarely": 1,
    "Rarely": 2,
    "Sometimes": 3,
    "Often": 4,
    "Very often": 5,
}
MSG_APP_FREQ = {
    "Less than once per day": 1,
    "1–3 times per day": 2,
    "4–10 times per day": 3,
    "More than 10 times per day": 4,
}
NEGATIVE_EMOTIONS = [
    "insecure", "helpless", "excluded", "threatened", "critical", "frustrated",
    "humiliated", "bitter", "hurt", "guilty", "powerless", "lonely",
    "startled", "disapproving", "awful", "repelled",
]
POSITIVE_EMOTIONS = ["powerful", "excited", "proud", "hopeful"]
POST_SCALE_COLS = [
    "post_engaging_1_5", "post_willing_continue_1_5", "post_coherent_1_5",
    "post_stayed_on_topic_1_5", "post_natural_1_5", "post_smooth_flow_1_5",
    "post_relevant_followups_1_5", "post_balanced_1_5", "post_overall_rating_1_5",
]


def transcript_to_dataframe(transcript):
    return pd.DataFrame(transcript)


def _safe_json_loads(value) -> Dict:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        data = json.loads(value)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _map_value(value, mapping):
    if value in mapping:
        return mapping[value]
    return value if isinstance(value, (int, float)) else math.nan


def enrich_results(conversations: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    if conversations.empty:
        return conversations

    rows: List[Dict] = []
    for _, row in conversations.iterrows():
        pre = _safe_json_loads(row.get("pre_questionnaire_json"))
        post = _safe_json_loads(row.get("post_questionnaire_json"))
        emotions = pre.get("ai_experience_emotions", {}) if isinstance(pre.get("ai_experience_emotions"), dict) else {}

        enriched = row.to_dict()
        for key, value in pre.items():
            if key != "ai_experience_emotions":
                enriched[f"pre_{key}"] = value
        for key, value in post.items():
            enriched[f"post_{key}"] = value
        for key, value in emotions.items():
            enriched[f"pre_emotion_{key}"] = value
            enriched[f"pre_emotion_{key}_score"] = _map_value(value, LIKERT_5)

        enriched["pre_messaging_app_use_score"] = _map_value(pre.get("messaging_app_use"), MSG_APP_FREQ)
        enriched["pre_ai_general_purpose_score"] = _map_value(pre.get("ai_use_general_purpose"), AI_FREQ)
        enriched["pre_ai_specific_purpose_score"] = _map_value(pre.get("ai_use_specific_purpose"), AI_FREQ)
        enriched["pre_text_communication_ease_score"] = pre.get("text_communication_ease_1_5", math.nan)
        enriched["pre_message_style_one_two_words_score"] = _map_value(pre.get("message_style_one_two_words"), LIKERT_5)
        enriched["pre_message_style_single_sentence_score"] = _map_value(pre.get("message_style_single_sentence"), LIKERT_5)
        enriched["pre_message_style_short_score"] = _map_value(pre.get("message_style_short_2_3_sentences"), LIKERT_5)
        enriched["pre_message_style_long_score"] = _map_value(pre.get("message_style_long_detailed"), LIKERT_5)

        neg_scores = [_map_value(emotions.get(e), LIKERT_5) for e in NEGATIVE_EMOTIONS]
        pos_scores = [_map_value(emotions.get(e), LIKERT_5) for e in POSITIVE_EMOTIONS]
        enriched["pre_negative_affect_mean"] = pd.Series(neg_scores, dtype="float").mean()
        enriched["pre_positive_affect_mean"] = pd.Series(pos_scores, dtype="float").mean()

        for key, value in post.items():
            if key.endswith("_1_5"):
                enriched[f"post_{key}"] = value
        rows.append(enriched)

    enriched_df = pd.DataFrame(rows)
    merged = enriched_df.merge(metrics, on="conversation_id", how="left") if not metrics.empty else enriched_df

    available_post = [c for c in POST_SCALE_COLS if c in merged.columns]
    if available_post:
        merged["post_experience_mean"] = merged[available_post].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    if "post_repetitive_1_5" in merged.columns:
        merged["post_repetitive_reverse_1_5"] = 6 - pd.to_numeric(merged["post_repetitive_1_5"], errors="coerce")
    if "post_experience_mean" in merged.columns and "post_repetitive_reverse_1_5" in merged.columns:
        merged["post_quality_index"] = merged[["post_experience_mean", "post_repetitive_reverse_1_5"]].mean(axis=1)
    return merged


def numeric_columns_for_analysis(df: pd.DataFrame) -> List[str]:
    candidates = [
        "engagement_score", "coherence", "topic_consistency", "novelty", "question_rate", "turn_balance",
        "post_experience_mean", "post_quality_index", "post_engaging_1_5", "post_willing_continue_1_5",
        "post_coherent_1_5", "post_stayed_on_topic_1_5", "post_natural_1_5", "post_smooth_flow_1_5",
        "post_repetitive_1_5", "post_relevant_followups_1_5", "post_balanced_1_5", "post_overall_rating_1_5",
        "pre_text_communication_ease_score", "pre_messaging_app_use_score", "pre_ai_general_purpose_score",
        "pre_ai_specific_purpose_score", "pre_negative_affect_mean", "pre_positive_affect_mean",
        "pre_message_style_one_two_words_score", "pre_message_style_single_sentence_score",
        "pre_message_style_short_score", "pre_message_style_long_score",
    ]
    return [c for c in candidates if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any()]


def group_test(df: pd.DataFrame, group_col: str, metric_col: str) -> Dict:
    work = df[[group_col, metric_col]].copy()
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    work = work.dropna()
    groups = [(name, values[metric_col].dropna()) for name, values in work.groupby(group_col) if len(values[metric_col].dropna()) >= 2]

    if len(groups) < 2:
        return {"test": "Not enough data", "p_value": math.nan, "statistic": math.nan, "note": "Need at least two groups with at least two observations each."}

    arrays = [g[1].to_numpy() for g in groups]
    if len(groups) == 2:
        stat, p = stats.ttest_ind(arrays[0], arrays[1], equal_var=False, nan_policy="omit")
        nonparam_stat, nonparam_p = stats.mannwhitneyu(arrays[0], arrays[1], alternative="two-sided")
        return {
            "test": "Welch independent t-test; Mann-Whitney U also reported",
            "statistic": float(stat),
            "p_value": float(p),
            "secondary_test": "Mann-Whitney U",
            "secondary_statistic": float(nonparam_stat),
            "secondary_p_value": float(nonparam_p),
            "groups": ", ".join(str(g[0]) for g in groups),
        }

    stat, p = stats.f_oneway(*arrays)
    nonparam_stat, nonparam_p = stats.kruskal(*arrays)
    return {
        "test": "One-way ANOVA; Kruskal-Wallis also reported",
        "statistic": float(stat),
        "p_value": float(p),
        "secondary_test": "Kruskal-Wallis",
        "secondary_statistic": float(nonparam_stat),
        "secondary_p_value": float(nonparam_p),
        "groups": ", ".join(str(g[0]) for g in groups),
    }


def correlation_table(df: pd.DataFrame, outcome_col: str, predictors: List[str]) -> pd.DataFrame:
    rows = []
    y = pd.to_numeric(df[outcome_col], errors="coerce")
    for col in predictors:
        if col == outcome_col:
            continue
        x = pd.to_numeric(df[col], errors="coerce")
        valid = pd.DataFrame({"x": x, "y": y}).dropna()
        if len(valid) < 3:
            continue
        pearson_r, pearson_p = stats.pearsonr(valid["x"], valid["y"])
        spearman_r, spearman_p = stats.spearmanr(valid["x"], valid["y"])
        rows.append({
            "predictor": col,
            "n": len(valid),
            "pearson_r": pearson_r,
            "pearson_p": pearson_p,
            "spearman_rho": spearman_r,
            "spearman_p": spearman_p,
        })
    return pd.DataFrame(rows).sort_values("spearman_p") if rows else pd.DataFrame()


def render_researcher_statistics(df: pd.DataFrame) -> None:
    st.header("Questionnaire + Statistical Analysis")
    st.caption("Use this as exploratory analysis. For thesis reporting, verify assumptions and sample size before drawing conclusions.")

    analysis_cols = numeric_columns_for_analysis(df)
    if not analysis_cols:
        st.info("No numeric questionnaire or metric fields available yet.")
        return

    summary_cols = ["participant_id", "session_id", "assignment_id", "device_type", "topic_id", "agent_style"] + analysis_cols
    summary_cols = [c for c in summary_cols if c in df.columns]
    st.subheader("Analysis-ready dataset")
    st.dataframe(df[summary_cols], use_container_width=True)
    st.download_button(
        "Download analysis-ready CSV",
        df[summary_cols].to_csv(index=False).encode("utf-8"),
        "analysis_ready_results.csv",
        "text/csv",
    )

    st.subheader("Descriptive statistics")
    st.dataframe(df[analysis_cols].apply(pd.to_numeric, errors="coerce").describe().T, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        metric = st.selectbox("Outcome metric", analysis_cols, index=analysis_cols.index("post_quality_index") if "post_quality_index" in analysis_cols else 0)
    with c2:
        group_options = [c for c in ["agent_style", "topic_id", "topic_category", "device_type", "pre_age_group", "pre_gender", "pre_used_ai_before"] if c in df.columns]
        group_col = st.selectbox("Compare by group", group_options) if group_options else None

    if group_col:
        st.subheader("Automatic group comparison")
        result = group_test(df, group_col, metric)
        st.dataframe(pd.DataFrame([result]), use_container_width=True)
        st.caption("Two groups: Welch t-test + Mann-Whitney U. Three or more groups: one-way ANOVA + Kruskal-Wallis.")

        plot_df = df[[group_col, metric]].copy()
        plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
        plot_df = plot_df.dropna()
        if not plot_df.empty:
            fig, ax = plt.subplots()
            plot_df.groupby(group_col)[metric].mean().sort_values(ascending=False).plot(kind="bar", ax=ax)
            ax.set_title(f"Average {metric} by {group_col}")
            ax.set_xlabel(group_col)
            ax.set_ylabel(metric)
            plt.xticks(rotation=35, ha="right")
            plt.tight_layout()
            st.pyplot(fig)

    st.subheader("Correlations with selected outcome")
    corr = correlation_table(df, metric, analysis_cols)
    if corr.empty:
        st.info("Need at least three complete observations for correlations.")
    else:
        st.dataframe(corr, use_container_width=True)


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_db()
    initialize_conversation_state(include_researcher_defaults=True)
    device_type = update_device_type_from_headers()

    st.title(APP_TITLE)
    st.caption("Researcher/Admin page. Use the Participant page for the user-facing mobile view.")

    st.divider()
    st.header("Stored Results")
    conversations, messages, metrics = load_all()

    if conversations.empty:
        st.info("No stored conversations yet.")
        return

    merged = enrich_results(conversations, metrics)
    st.dataframe(merged, use_container_width=True)

    st.download_button("Download full stored results CSV", merged.to_csv(index=False).encode("utf-8"), "conversation_full_results.csv", "text/csv")
    st.download_button("Download all messages CSV", messages.to_csv(index=False).encode("utf-8"), "conversation_messages.csv", "text/csv")

    render_researcher_statistics(merged)


if __name__ == "__main__":
    main()
