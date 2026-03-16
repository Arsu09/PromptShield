# download_dataset.py
# HuggingFace se real prompt injection dataset download karo

from datasets import load_dataset
import pandas as pd

print("📥 Dataset download ho raha hai...")

# Real prompt injection dataset — free on HuggingFace
dataset = load_dataset("deepset/prompt-injections")

# Train aur test split
train_data = dataset["train"]
test_data = dataset["test"]

# Pandas DataFrame mein convert karo
train_df = pd.DataFrame(train_data)
test_df = pd.DataFrame(test_data)

# CSV mein save karo
train_df.to_csv("train_dataset.csv", index=False)
test_df.to_csv("test_dataset.csv", index=False)

print(f"✅ Train examples: {len(train_df)}")
print(f"✅ Test examples: {len(test_df)}")
print(f"✅ Columns: {train_df.columns.tolist()}")
print("\n📊 Label distribution:")
print(train_df["label"].value_counts())
print("\n🔍 Sample data:")
print(train_df.head())

print("\n✅ Dataset save ho gaya — train_dataset.csv aur test_dataset.csv")