# app.py — PromptShield Interactive Demo

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from detector import PromptShield
from dataset import ATTACK_EXAMPLES, SAFE_EXAMPLES

# ── Page config ──
st.set_page_config(
    page_title="PromptShield",
    page_icon="🛡️",
    layout="wide"
)

# ── Load model once ──
@st.cache_resource
def load_shield():
    return PromptShield()

shield = load_shield()

# ── Header ──
st.title("🛡️ PromptShield")
st.markdown("**Agentic AI Prompt Injection Detection & Prevention Framework**")
st.markdown("---")

# ── Two columns layout ──
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🔍 Test a Prompt")

    # Quick examples dropdown
    example_type = st.selectbox(
        "Load an example:",
        ["Write your own..."] +
        ["⚔️ Attack: " + a[:50] + "..." for a in ATTACK_EXAMPLES[:5]] +
        ["✅ Safe: " + s[:50] + "..." for s in SAFE_EXAMPLES[:5]]
    )

    # Auto-fill if example selected
    if example_type.startswith("⚔️ Attack"):
        idx = int(example_type.split(" ")[2].replace(":", "")) if False else \
              next(i for i, a in enumerate(ATTACK_EXAMPLES)
                   if a[:50] in example_type)
        default_text = ATTACK_EXAMPLES[idx]
    elif example_type.startswith("✅ Safe"):
        idx = next(i for i, s in enumerate(SAFE_EXAMPLES)
                   if s[:50] in example_type)
        default_text = SAFE_EXAMPLES[idx]
    else:
        default_text = ""

    user_input = st.text_area(
        "Enter a prompt to scan:",
        value=default_text,
        height=120,
        placeholder="Type any prompt here and click Scan..."
    )

    scan_btn = st.button("🔎 Scan Prompt", use_container_width=True, type="primary")

    if scan_btn and user_input.strip():
        result = shield.scan(user_input)

        # ── Verdict ──
        if "ATTACK" in result["final_verdict"]:
            st.error(f"### {result['final_verdict']}")
        else:
            st.success(f"### {result['final_verdict']}")

        # ── Scores ──
        st.markdown("#### 📊 Detection Scores")
        c1, c2 = st.columns(2)
        c1.metric("Pattern Match Score", f"{result['pattern_score']:.0%}")
        c2.metric("ML Attack Probability", f"{result['ml_attack_prob']}%")

        # ── Pattern matches ──
        if result["pattern_matches"]:
            st.markdown("#### ⚠️ Matched Attack Patterns")
            for p in result["pattern_matches"]:
                st.code(p)

        # ── Probability bar ──
        st.markdown("#### 🎯 ML Confidence")
        prob_df = pd.DataFrame({
            "Category": ["Safe", "Attack"],
            "Probability": [
                result["ml_safe_prob"],
                result["ml_attack_prob"]
            ]
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
                    f"{val}%", va='center', fontsize=11)
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('#f8f9fa')
        st.pyplot(fig)

with col2:
    st.subheader("📈 Batch Analysis")
    st.markdown("Scan multiple prompts at once")

    if st.button("🔄 Run All Examples", use_container_width=True):
        all_prompts = (
            [(p, "Attack") for p in ATTACK_EXAMPLES] +
            [(p, "Safe") for p in SAFE_EXAMPLES]
        )
        results = []
        for prompt, true_label in all_prompts:
            r = shield.scan(prompt)
            predicted = "Attack" if "ATTACK" in r["final_verdict"] else "Safe"
            correct = predicted == true_label
            results.append({
                "Prompt": prompt[:40] + "...",
                "True": true_label,
                "Predicted": predicted,
                "ML Score": f"{r['ml_attack_prob']}%",
                "✓": "✅" if correct else "❌"
            })

        df = pd.DataFrame(results)
        correct = sum(1 for r in results if r["✓"] == "✅")
        total = len(results)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Scanned", total)
        col_b.metric("Correct", correct)
        col_c.metric("Accuracy", f"{correct/total*100:.1f}%")

        st.dataframe(df, use_container_width=True, height=400)

# ── Footer ──
st.markdown("---")
st.markdown(
    "🔬 **PromptShield** | Research Project for Agentic AI Security | "
    "Built for Masters Scholarship Application"
)