# train_model.py — Purane model vs Naye model comparison

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ── Data load karo ──
print("📂 Dataset load ho rahi hai...")
train_df = pd.read_csv("train_dataset.csv")
test_df = pd.read_csv("test_dataset.csv")

X_train = train_df["text"]
y_train = train_df["label"]
X_test = test_df["text"]
y_test = test_df["label"]

print(f"✅ Train: {len(X_train)} | Test: {len(X_test)}")

# ── 4 Models define karo ──
models = {
    "Logistic Regression (Purana)": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100),
    "SVM": SVC(kernel="linear", probability=True),
}

# ── Har model train aur test karo ──
results = {}
print("\n🔥 Models train ho rahe hain...\n")

for name, clf in models.items():
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1,3), max_features=5000)),
        ('clf', clf)
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred) * 100
    results[name] = round(acc, 2)
    print(f"{'✅' if acc > 85 else '📊'} {name}: {acc:.1f}%")
    print(classification_report(y_test, y_pred,
          target_names=["Safe", "Attack"]))
    print("-" * 50)

# ── Graph banao ──
print("\n📊 Graph ban raha hai...")
fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12"]
bars = ax.bar(results.keys(), results.values(), color=colors, width=0.5)

for bar, val in zip(bars, results.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val}%", ha='center', fontsize=12, fontweight='bold')

ax.set_ylabel("Accuracy (%)", fontsize=13)
ax.set_title("PromptShield — Model Comparison", fontsize=15, fontweight='bold')
ax.set_ylim(0, 110)
ax.axhline(y=85, color='gray', linestyle='--', alpha=0.5, label='85% baseline')
ax.legend()
plt.xticks(rotation=15, ha='right')
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=150)
plt.show()

print("\n✅ Graph save ho gaya — model_comparison.png")
print("\n🏆 Best Model:", max(results, key=results.get),
      f"— {max(results.values())}%")