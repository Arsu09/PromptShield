# detector.py — PromptShield v2.1 — Severity Level Added

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# ─────────────────────────────────────────
# LAYER 1: Pattern Matcher
# ─────────────────────────────────────────

# HIGH severity — seedha system control lene ki koshish
HIGH_PATTERNS = [
    r"ignore (all |previous |above |prior )?instructions?",
    r"(system override|admin override|root access)",
    r"###.*(end|override|system|new)###",
    r"\[system\].*override",
    r"(jailbreak|dan mode|evil mode|god mode)",
    r"forget (everything|all previous instructions)",
    r"your (real|actual|true|new) (task|goal|instructions?)",
    r"(disable|bypass|remove) (all )?(restrictions?|filters?|guidelines?)",
]

# MEDIUM severity — suspicious but not direct attack
MEDIUM_PATTERNS = [
    r"(new|override|updated?) (system |prompt |instructions?|directive)",
    r"disregard (your |all |previous )?",
    r"(no restrictions?|no (safety |content )?filter)",
    r"(act|pretend|simulate|behave) as if (you have no|without)",
    r"(from now on|starting now) you (are|will|must)",
    r"(developer mode|maintenance mode|test mode)",
    r"forget (the above|previous)",
]

# LOW severity — mildly suspicious
LOW_PATTERNS = [
    r"ignore (this|that|it)",
    r"(pretend|imagine|roleplay|act as)",
    r"(hypothetically|theoretically) (speaking)?",
    r"what (would|could) you do if (there were no|without) rules",
    r"(secret|hidden|real) (mode|instructions?|purpose)",
]

def pattern_scan(text: str) -> dict:
    text_lower = text.lower()

    # Check HIGH first
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "severity": "HIGH",
                "score": 1.0,
                "matched_pattern": pattern,
                "flagged": True
            }

    # Check MEDIUM
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "severity": "MEDIUM",
                "score": 0.6,
                "matched_pattern": pattern,
                "flagged": True
            }

    # Check LOW
    for pattern in LOW_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "severity": "LOW",
                "score": 0.3,
                "matched_pattern": pattern,
                "flagged": True
            }

    return {
        "severity": "NONE",
        "score": 0.0,
        "matched_pattern": None,
        "flagged": False
    }

# ─────────────────────────────────────────
# LAYER 2: Random Forest ML
# ─────────────────────────────────────────

class MLDetector:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=5000)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        self._train()

    def _train(self):
        try:
            train_df = pd.read_csv("train_dataset.csv")
            X = train_df["text"]
            y = train_df["label"]
            print(f"✅ Real dataset loaded: {len(X)} examples")
        except:
            from dataset import get_training_data
            X, y = get_training_data()
            print("⚠️ Using basic dataset")
        self.model.fit(X, y)
        print("✅ Random Forest trained!")

    def predict(self, text: str) -> dict:
        prob = self.model.predict_proba([text])[0]
        return {
            "safe_prob": round(prob[0] * 100, 1),
            "attack_prob": round(prob[1] * 100, 1),
            "verdict": "ATTACK" if prob[1] > 0.5 else "SAFE"
        }

# ─────────────────────────────────────────
# SEVERITY CALCULATOR
# ─────────────────────────────────────────

def calculate_severity(pattern_result: dict, ml_attack_prob: float) -> dict:
    """Pattern + ML dono milake final severity decide karo"""

    pattern_sev = pattern_result["severity"]
    ml_prob = ml_attack_prob

    # HIGH: Pattern HIGH ya ML > 85%
    if pattern_sev == "HIGH" or ml_prob >= 85:
        return {
            "level": "HIGH",
            "emoji": "🔴",
            "color": "#e74c3c",
            "label": "HIGH RISK",
            "description": "Direct prompt injection attack detected. Immediate threat.",
            "recommendation": "Block this prompt. Do not process further."
        }

    # MEDIUM: Pattern MEDIUM ya ML 60-85%
    elif pattern_sev == "MEDIUM" or ml_prob >= 60:
        return {
            "level": "MEDIUM",
            "emoji": "🟠",
            "color": "#f39c12",
            "label": "MEDIUM RISK",
            "description": "Suspicious patterns found. Possible injection attempt.",
            "recommendation": "Review carefully before processing."
        }

    # LOW: Pattern LOW ya ML 40-60%
    elif pattern_sev == "LOW" or ml_prob >= 40:
        return {
            "level": "LOW",
            "emoji": "🟡",
            "color": "#f1c40f",
            "label": "LOW RISK",
            "description": "Mildly suspicious. Could be benign but worth checking.",
            "recommendation": "Monitor and log this prompt."
        }

    # SAFE
    else:
        return {
            "level": "SAFE",
            "emoji": "🟢",
            "color": "#2ecc71",
            "label": "SAFE",
            "description": "No injection patterns detected.",
            "recommendation": "Safe to process."
        }

# ─────────────────────────────────────────
# COMBINED PIPELINE
# ─────────────────────────────────────────

class PromptShield:
    def __init__(self):
        print("🛡️ Loading PromptShield v3.0...")
        self.ml = MLDetector()
        # Self-learning engine
        from self_learning import SelfLearningEngine
        self.learner = SelfLearningEngine()
        # Gemini
        try:
            from llm_judge import GeminiJudge
            self.gemini = GeminiJudge()
            self.gemini_available = True
        except:
            self.gemini_available = False

    def scan(self, prompt: str, use_gemini: bool = False) -> dict:
        pattern_result = pattern_scan(prompt)
        ml_result = self.ml.predict(prompt)

        # Online model ka prediction bhi lo
        online_result = self.learner.get_online_prediction(prompt)

        # Combined ML score
        combined_prob = round(
            (ml_result["attack_prob"] * 0.6 +
             online_result["attack_prob"] * 0.4), 1
        )

        severity = calculate_severity(pattern_result, combined_prob)

        if severity["level"] in ["HIGH", "MEDIUM"]:
            final = "🚨 ATTACK DETECTED"
        elif severity["level"] == "LOW":
            final = "⚠️ SUSPICIOUS"
        else:
            final = "✅ SAFE"

        is_attack = severity["level"] in ["HIGH", "MEDIUM", "LOW"]

        # Har scan ke baad seekho
        self.learner.on_scan(prompt, is_attack)

        result = {
            "final_verdict": final,
            "severity": severity,
            "pattern_severity": pattern_result["severity"],
            "matched_pattern": pattern_result["matched_pattern"],
            "ml_attack_prob": ml_result["attack_prob"],
            "ml_safe_prob": ml_result["safe_prob"],
            "online_attack_prob": online_result["attack_prob"],
            "combined_prob": combined_prob,
            "pattern_score": pattern_result["score"],
            "pattern_matches": [pattern_result["matched_pattern"]]
                                if pattern_result["matched_pattern"] else [],
            "gemini_result": None
        }

        if use_gemini and self.gemini_available:
            gemini_result = self.gemini.evaluate(prompt)
            result["gemini_result"] = gemini_result

        return result

    def give_feedback(self, prompt: str, verdict: str,
                      feedback: str, true_label: int):
        """User feedback process karo"""
        self.learner.on_feedback(prompt, verdict, feedback, true_label)

    def get_learning_stats(self):
        return self.learner.get_dashboard_stats()

    def get_recent_feedback(self):
        return self.learner.get_recent_feedback()