# detector.py — PromptShield Detection Engine

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from dataset import get_training_data

# ─────────────────────────────────────────
# LAYER 1: Pattern Matcher (Fast Rules)
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
    r"repeat (the word|this) .{1,30} (times|\d+)",
]

def pattern_scan(text: str) -> dict:
    """Fast rule-based detection"""
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
# LAYER 2: ML Classifier (TF-IDF + LR)
# ─────────────────────────────────────────

class MLDetector:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=5000)),
            ('clf', LogisticRegression(max_iter=1000))
        ])
        self._train()

    def _train(self):
        texts, labels = get_training_data()
        self.model.fit(texts, labels)
        print("✅ ML model trained!")

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
        print("🛡️ Loading PromptShield...")
        self.ml = MLDetector()

    def scan(self, prompt: str) -> dict:
        # Layer 1
        pattern_result = pattern_scan(prompt)
        # Layer 2
        ml_result = self.ml.predict(prompt)

        # Combined decision
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