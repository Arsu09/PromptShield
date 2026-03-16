# self_learning.py — PromptShield Self-Learning Engine v3.0

import pandas as pd
import numpy as np
import json
import os
import re
import pickle
from datetime import datetime
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

FEEDBACK_FILE = "feedback_data.csv"
LEARNED_PATTERNS_FILE = "learned_patterns.json"
ONLINE_MODEL_FILE = "online_model.pkl"
STATS_FILE = "learning_stats.json"

class OnlineLearner:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1,3), max_features=5000)
        self.model = SGDClassifier(loss='log_loss', random_state=42, max_iter=1000)
        self.is_fitted = False
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(ONLINE_MODEL_FILE):
            try:
                with open(ONLINE_MODEL_FILE, 'rb') as f:
                    saved = pickle.load(f)
                    self.vectorizer = saved['vectorizer']
                    self.model = saved['model']
                    self.is_fitted = saved['is_fitted']
                print("✅ Online model loaded from disk!")
            except:
                self._init_with_base_data()
        else:
            self._init_with_base_data()

    def _init_with_base_data(self):
        try:
            df = pd.read_csv("train_dataset.csv")
            X = df["text"].tolist()
            y = df["label"].tolist()
            X_vec = self.vectorizer.fit_transform(X)
            self.model.partial_fit(X_vec, y, classes=[0,1])
            self.is_fitted = True
            self.save()
            print(f"✅ Online model initialized: {len(X)} examples")
        except Exception as e:
            print(f"⚠️ Init error: {e}")

    def learn_from_example(self, text: str, label: int):
        try:
            X_vec = self.vectorizer.transform([text])
            self.model.partial_fit(X_vec, [label], classes=[0,1])
            self.save()
            return True
        except Exception as e:
            print(f"Learning error: {e}")
            return False

    def predict(self, text: str) -> dict:
        if not self.is_fitted:
            return {"attack_prob": 50.0, "safe_prob": 50.0}
        try:
            X_vec = self.vectorizer.transform([text])
            prob = self.model.predict_proba(X_vec)[0]
            return {
                "safe_prob": round(prob[0]*100, 1),
                "attack_prob": round(prob[1]*100, 1)
            }
        except:
            return {"attack_prob": 50.0, "safe_prob": 50.0}

    def save(self):
        with open(ONLINE_MODEL_FILE, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'model': self.model,
                'is_fitted': self.is_fitted
            }, f)


class FeedbackSystem:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(FEEDBACK_FILE):
            df = pd.DataFrame(columns=[
                'timestamp', 'prompt', 'model_verdict',
                'user_feedback', 'true_label', 'learned'
            ])
            df.to_csv(FEEDBACK_FILE, index=False)

    def save_feedback(self, prompt, model_verdict, user_feedback, true_label):
        new_row = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prompt': prompt,
            'model_verdict': model_verdict,
            'user_feedback': user_feedback,
            'true_label': true_label,
            'learned': True
        }
        df = pd.read_csv(FEEDBACK_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(FEEDBACK_FILE, index=False)
        return True

    def get_stats(self) -> dict:
        if not os.path.exists(FEEDBACK_FILE):
            return {"total": 0, "correct": 0, "incorrect": 0, "accuracy": 0}
        df = pd.read_csv(FEEDBACK_FILE)
        if len(df) == 0:
            return {"total": 0, "correct": 0, "incorrect": 0, "accuracy": 0}
        correct = len(df[df['user_feedback'] == 'correct'])
        incorrect = len(df[df['user_feedback'] == 'incorrect'])
        return {
            "total": len(df),
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": round(correct/len(df)*100, 1) if len(df) > 0 else 0
        }

    def get_recent_feedback(self, n=10):
        if not os.path.exists(FEEDBACK_FILE):
            return pd.DataFrame()
        df = pd.read_csv(FEEDBACK_FILE)
        return df.tail(n)


class PatternDiscovery:
    def __init__(self):
        self.learned_patterns = self._load_patterns()

    def _load_patterns(self):
        if os.path.exists(LEARNED_PATTERNS_FILE):
            with open(LEARNED_PATTERNS_FILE, 'r') as f:
                return json.load(f)
        return []

    def discover_patterns(self, text: str, is_attack: bool):
        if not is_attack:
            return
        attack_phrases = [
            r'\b(ignore|forget|disregard|override)\b.{0,20}\b(instructions?|rules?|guidelines?)\b',
            r'\b(you are now|act as|pretend to be|simulate)\b',
            r'\b(no restrictions?|no limits?|unrestricted)\b',
            r'\b(system|admin|root|developer)\b.{0,10}\b(mode|access|override)\b',
            r'\b(jailbreak|bypass|hack|exploit)\b',
        ]
        new_found = False
        for pattern in attack_phrases:
            if re.search(pattern, text.lower()):
                if pattern not in self.learned_patterns:
                    self.learned_patterns.append(pattern)
                    new_found = True
        if new_found:
            self._save_patterns()

    def _save_patterns(self):
        with open(LEARNED_PATTERNS_FILE, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)

    def get_learned_patterns(self):
        return self.learned_patterns

    def get_count(self):
        return len(self.learned_patterns)


class SelfLearningEngine:
    def __init__(self):
        print("🧠 Loading Self-Learning Engine...")
        self.online_learner = OnlineLearner()
        self.feedback_system = FeedbackSystem()
        self.pattern_discovery = PatternDiscovery()
        self.stats = self._load_stats()
        print("✅ Self-Learning Engine ready!")

    def _load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {
            "total_scans": 0,
            "total_learned": 0,
            "patterns_discovered": 0,
            "feedback_count": 0
        }

    def _save_stats(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def on_scan(self, prompt: str, is_attack: bool):
        self.stats["total_scans"] = self.stats.get("total_scans", 0) + 1
        label = 1 if is_attack else 0
        try:
            learned = self.online_learner.learn_from_example(prompt, label)
            if learned:
                self.stats["total_learned"] = self.stats.get("total_learned", 0) + 1
        except Exception as e:
            print(f"Online learning error: {e}")
        try:
            self.pattern_discovery.discover_patterns(prompt, is_attack)
        except Exception as e:
            print(f"Pattern discovery error: {e}")
        self._save_stats()

    def on_feedback(self, prompt, model_verdict, feedback, true_label):
        self.feedback_system.save_feedback(prompt, model_verdict, feedback, true_label)
        self.online_learner.learn_from_example(prompt, true_label)
        self.stats["feedback_count"] = self.stats.get("feedback_count", 0) + 1
        self._save_stats()

    def get_online_prediction(self, text: str) -> dict:
        try:
            return self.online_learner.predict(text)
        except Exception as e:
            print(f"Online prediction error: {e}")
            return {"attack_prob": 50.0, "safe_prob": 50.0}

    def get_dashboard_stats(self) -> dict:
        try:
            feedback_stats = self.feedback_system.get_stats()
            return {
                "total_scans": self.stats.get("total_scans", 0),
                "total_learned": self.stats.get("total_learned", 0),
                "patterns_found": self.pattern_discovery.get_count(),
                "feedback_count": feedback_stats["total"],
                "feedback_accuracy": feedback_stats.get("accuracy", 0),
                "learned_patterns": self.pattern_discovery.get_learned_patterns()
            }
        except Exception as e:
            print(f"Dashboard stats error: {e}")
            return {
                "total_scans": 0,
                "total_learned": 0,
                "patterns_found": 0,
                "feedback_count": 0,
                "feedback_accuracy": 0,
                "learned_patterns": []
            }

    def get_recent_feedback(self):
        return self.feedback_system.get_recent_feedback()