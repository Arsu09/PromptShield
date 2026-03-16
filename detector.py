# detector.py — PromptShield v2.0 — Real Dataset + Random Forest

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# ─────────────────────────────────────────
# LAYER 1: Pattern Matcher
# ─────────────────────────────────────────

ATTACK_PATTERNS = [
    r"ignore (all |previous |above |prior )?instructions?",
    r"forget (everything|all|the above|previous)",
    r"(new|override|updated?) (system |prompt |instructions?|directive)",
    r"disregard (your |all |previous )?",
    r"(jailbreak|dan mode|evil mode|developer mode|god mode)",
    r"(no restrictions?|no (safety |content )?filter)",
    r"your (real|actual|true|new) (task|goal|instructions?|purpose)",
    r"(act|pretend|simulate|behave) as if (you have no|without)",
    r"(system override|admin override|root access)",
    r"(lift|remove|disable|bypass) (all )?(restrictions?|filters?|guidelines?)",
    r"(from now on|starting now|henceforth) you (are|will|must)",
    r"###.*(end|override|system|new)###",
    r"\[system\]",
]

def pattern_scan(text: str) -> dict:
    text_lower = text.lower()
    matched = []
    for pattern in ATTACK_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(pattern)
    score = min(len(matched) * 0.3, 1.0)
    return {
        "score": score,
        "matched_patterns": matched,
        "flagged": score > 0.0
    }

# ─────────────────────────────────────────
# LAYER 2: Random Forest (New & Better!)
# ─────────────────────────────────────────

class MLDetector:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=5000)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        self._train()

    def _train(self):
        # Real dataset use karo
        try:
            train_df = pd.read_csv("train_dataset.csv")
            X = train_df["text"]
            y = train_df["label"]
            print(f"✅ Real dataset loaded: {len(X)} examples")
        except:
            # Fallback to basic examples
            from dataset import get_training_data
            X, y = get_training_data()
            print("⚠️ Using basic dataset")

        self.model.fit(X, y)
        print("✅ Random Forest model trained!")

    def predict(self, text: str) -> dict:
        prob = self.model.predict_proba([text])[0]
        return {
            "safe_prob": round(prob[0] * 100, 1),
            "attack_prob": round(prob[1] * 100, 1),
            "verdict": "ATTACK" if prob[1] > 0.5 else "SAFE"
        }

# ─────────────────────────────────────────
# COMBINED PIPELINE
# ─────────────────────────────────────────

class PromptShield:
    def __init__(self):
        print("🛡️ Loading PromptShield v2.0...")
        self.ml = MLDetector()

    def scan(self, prompt: str) -> dict:
        pattern_result = pattern_scan(prompt)
        ml_result = self.ml.predict(prompt)

        if pattern_result["flagged"] or ml_result["verdict"] == "ATTACK":
            final = "🚨 ATTACK DETECTED"
            color = "red"
        else:
            final = "✅ SAFE"
            color = "green"

        return {
            "final_verdict": final,
            "color": color,
            "pattern_score": pattern_result["score"],
            "pattern_matches": pattern_result["matched_patterns"],
            "ml_attack_prob": ml_result["attack_prob"],
            "ml_safe_prob": ml_result["safe_prob"],
        }