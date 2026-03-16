# app.py — PromptShield v3.0 — Self-Learning Edition

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from detector import PromptShield
from dataset import ATTACK_EXAMPLES, SAFE_EXAMPLES

# ── Page config ──
st.set_page_config(
    page_title="PromptShield v3.0",
    page_icon="🛡️",
    layout="wide"
)

# ── Load model once ──
@st.cache_resource
def load_shield():
    return PromptShield()

shield = load_shield()

# ── Header ──
st.title("🛡️ PromptShield v3.0")
st.markdown("**Agentic AI Prompt Injection Detection & Prevention Framework**")

# ── Model Stats Banner ──
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("🧠 Model", "Random Forest")
col_b.metric("📊 Training Data", "546 examples")
col_c.metric("🎯 Accuracy", "85.34%")
col_d.metric("⚡ Detection Layers", "3 (Pattern + ML + AI)")

st.markdown("---")

# ── Model Comparison Graph ──
if os.path.exists("model_comparison.png"):
    with st.expander("📈 Model Comparison — v1.0 vs v2.0 dekhein"):
        st.image("model_comparison.png",
                 caption="Random Forest beats all other models at 85.34%")

st.markdown("---")

# ── Two columns layout ──
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🔍 Test a Prompt")

    user_input = st.text_area(
        "Enter any prompt to scan:",
        height=150,
        placeholder="Koi bhi prompt yahan likho — jaise:\n• Ignore all previous instructions...\n• What is machine learning?\n• You are now DAN with no restrictions..."
    )

    use_gemini = st.toggle(
        "🤖 Gemini AI Judge bhi use karo (Layer 3)",
        value=False,
        help="Gemini AI se deep analysis — thoda slow hoga"
    )

    scan_btn = st.button("🔎 Scan Prompt", use_container_width=True, type="primary")

    if scan_btn and user_input.strip():
        result = shield.scan(user_input, use_gemini=use_gemini)

        # ── Severity Badge ──
        sev = result["severity"]
        if sev["level"] == "HIGH":
            st.error(f"### {sev['emoji']} {sev['label']} — {result['final_verdict']}")
        elif sev["level"] == "MEDIUM":
            st.warning(f"### {sev['emoji']} {sev['label']} — {result['final_verdict']}")
        elif sev["level"] == "LOW":
            st.warning(f"### {sev['emoji']} {sev['label']} — {result['final_verdict']}")
        else:
            st.success(f"### {sev['emoji']} {sev['label']} — {result['final_verdict']}")

        # ── Severity Details ──
        st.markdown(f"**📋 Description:** {sev['description']}")
        st.markdown(f"**💡 Recommendation:** {sev['recommendation']}")

        # ── Severity Meter ──
        st.markdown("#### 🎚️ Severity Level")
        sev_cols = st.columns(4)
        levels = ["SAFE", "LOW", "MEDIUM", "HIGH"]
        colors_map = {
            "SAFE": "🟢", "LOW": "🟡",
            "MEDIUM": "🟠", "HIGH": "🔴"
        }
        for i, (col, level) in enumerate(zip(sev_cols, levels)):
            if level == sev["level"]:
                col.markdown(
                    f"<div style='background-color:{sev['color']};padding:10px;"
                    f"border-radius:8px;text-align:center;color:white;"
                    f"font-weight:bold'>{colors_map[level]}<br>{level}</div>",
                    unsafe_allow_html=True
                )
            else:
                col.markdown(
                    f"<div style='padding:10px;border-radius:8px;"
                    f"text-align:center;border:1px solid #ddd;color:gray'>"
                    f"{colors_map[level]}<br>{level}</div>",
                    unsafe_allow_html=True
                )

        # ── Scores ──
        st.markdown("#### 📊 Detection Scores")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pattern Severity", result["pattern_severity"])
        c2.metric("ML Attack Prob", f"{result['ml_attack_prob']}%")
        c3.metric("Final Severity", sev["level"])

        # ── Online Model Score ──
        if "online_attack_prob" in result:
            c4, c5 = st.columns(2)
            c4.metric("Online Model Prob",
                      f"{result['online_attack_prob']}%",
                      delta="Self-learned")
            c5.metric("Combined Prob",
                      f"{result['combined_prob']}%",
                      delta="Final score")

        # ── Gemini AI Analysis ──
        if result["gemini_result"]:
            st.markdown("---")
            st.markdown("### 🤖 Gemini AI Judge — Layer 3 Analysis")
            g = result["gemini_result"]
            g1, g2, g3 = st.columns(3)
            g1.metric("AI Verdict", g["verdict"])
            g2.metric("AI Severity", g["severity"])
            g3.metric("Confidence", f"{g['confidence']}%")
            st.markdown(f"**🎯 Attack Type:** `{g['attack_type']}`")
            st.markdown(f"**💬 AI Explanation:** {g['explanation']}")

        # ── Feedback Buttons ──
        st.markdown("#### 💬 Model ka faisla sahi tha?")
        fb_col1, fb_col2 = st.columns(2)

        if fb_col1.button("✅ Haan, Sahi Tha!", use_container_width=True):
            true_label = 1 if "ATTACK" in result["final_verdict"] or \
                         "SUSPICIOUS" in result["final_verdict"] else 0
            shield.give_feedback(
                user_input, result["final_verdict"], "correct", true_label
            )
            st.success("Shukriya! Model ne yeh example yaad kar liya 🧠")

        if fb_col2.button("❌ Nahi, Galat Tha!", use_container_width=True):
            true_label = 0 if "ATTACK" in result["final_verdict"] or \
                         "SUSPICIOUS" in result["final_verdict"] else 1
            shield.give_feedback(
                user_input, result["final_verdict"], "incorrect", true_label
            )
            st.warning("Shukriya! Model ne galti se seekh liya 🔄")

        # ── Matched Pattern ──
        if result["matched_pattern"]:
            st.markdown("#### ⚠️ Matched Pattern")
            st.code(result["matched_pattern"])
        else:
            st.info("No rule-based patterns — ML layer decided.")

        # ── Probability bar ──
        st.markdown("#### 🎯 ML Confidence")
        prob_df = pd.DataFrame({
            "Category": ["Safe", "Attack"],
            "Probability": [result["ml_safe_prob"], result["ml_attack_prob"]]
        })
        fig, ax = plt.subplots(figsize=(5, 2))
        bars = ax.barh(
            prob_df["Category"],
            prob_df["Probability"],
            color=["#2ecc71", "#e74c3c"]
        )
        ax.set_xlim(0, 100)
        ax.set_xlabel("Probability (%)")
        for bar, val in zip(bars, prob_df["Probability"]):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2,
                    f"{val}%", va='center', fontsize=11, fontweight='bold')
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('#f8f9fa')
        st.pyplot(fig)

with col2:
    st.subheader("📈 Batch Analysis")
    st.markdown("Scan all 40 examples at once — see overall accuracy")

    if st.button("🔄 Run All Examples", use_container_width=True):
        all_prompts = (
            [(p, "Attack") for p in ATTACK_EXAMPLES] +
            [(p, "Safe") for p in SAFE_EXAMPLES]
        )
        with st.spinner("Scanning all prompts..."):
            results = []
            for prompt, true_label in all_prompts:
                r = shield.scan(prompt)
                predicted = "Attack" if "ATTACK" in r["final_verdict"] else "Safe"
                correct = predicted == true_label
                results.append({
                    "Prompt": prompt[:40] + "...",
                    "True Label": true_label,
                    "Predicted": predicted,
                    "ML Score": f"{r['ml_attack_prob']}%",
                    "Result": "✅" if correct else "❌"
                })

        df = pd.DataFrame(results)
        correct = sum(1 for r in results if r["Result"] == "✅")
        total = len(results)
        accuracy = correct / total * 100

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scanned", total)
        m2.metric("Correct", correct)
        m3.metric("Accuracy", f"{accuracy:.1f}%",
                  delta="vs 80% before" if accuracy > 80 else None)

        st.markdown("#### Results Table")
        st.dataframe(df, use_container_width=True, height=380)

        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.pie(
            [correct, total - correct],
            labels=["Correct", "Wrong"],
            colors=["#2ecc71", "#e74c3c"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax2.set_title("Batch Detection Accuracy", fontweight='bold')
        fig2.patch.set_facecolor('#f8f9fa')
        st.pyplot(fig2)

# ── Attack Types Info ──
st.markdown("---")
with st.expander("📚 Attack Types — PromptShield kya detect karta hai?"):
    st.markdown("""
    | Attack Type | Example | Status |
    |---|---|---|
    | **Direct Injection** | "Ignore previous instructions..." | ✅ Detected |
    | **Goal Hijacking** | "Your real task is to..." | ✅ Detected |
    | **Persona Override** | "You are now DAN..." | ✅ Detected |
    | **System Override** | "### SYSTEM OVERRIDE ###" | ✅ Detected |
    | **Jailbreak** | "Developer mode enabled..." | ✅ Detected |
    """)

# ── Self-Learning Dashboard ──
st.markdown("---")
st.subheader("🧠 Self-Learning Dashboard")

stats = shield.get_learning_stats()

l1, l2, l3, l4 = st.columns(4)
l1.metric("Total Scans", stats["total_scans"], delta="Examples learned")
l2.metric("Auto-Learned", stats["total_learned"], delta="From scans")
l3.metric("Patterns Found", stats["patterns_found"], delta="Auto-discovered")
l4.metric("User Feedback", stats["feedback_count"], delta="Manual corrections")

if stats["learned_patterns"]:
    with st.expander(f"🔍 Auto-Discovered Patterns ({stats['patterns_found']})"):
        for p in stats["learned_patterns"]:
            st.code(p)

recent = shield.get_recent_feedback()
if len(recent) > 0:
    with st.expander("📋 Recent Feedback History"):
        st.dataframe(recent, use_container_width=True)

# ── Footer ──
st.markdown("---")
st.markdown(
    "🔬 **PromptShield v3.0** | Random Forest + Pattern Matching + Self-Learning | "
    "546 Training Examples | 85.34% Accuracy | "
    "Research Project — Agentic AI Security | "
    "👨‍💻 [GitHub](https://github.com/Arsu09/PromptShield)"
)