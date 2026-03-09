import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

# ======================================
# 1. LOAD DATASET
# ======================================
DATA_PATH = "power_line_sensor_data.csv"


df = pd.read_csv(DATA_PATH)

print("Dataset Shape:", df.shape)
print(df.head())

# ======================================
# 2. FEATURE ENGINEERING
# ======================================

# Extra safety feature (physics-based)
df["current_diff"] = df["current_in"] - df["current_out"]

FEATURES = [
    "voltage",
    "current_in",
    "current_out",
    "current_diff",
    "leakage_current",
    "load_kw",
    "power_factor",
    "temperature_c",
    "humidity"
]

TARGET = "fault"

X = df[FEATURES]
y = df[TARGET]

# ======================================
# 3. TRAIN-TEST SPLIT
# ======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ======================================
# 4. MODEL PIPELINE
# ======================================
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_split=8,
        class_weight="balanced",
        random_state=42
    ))
])

# ======================================
# 5. TRAIN MODEL
# ======================================
pipeline.fit(X_train, y_train)

# ======================================
# 6. EVALUATION
# ======================================
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ======================================
# 7. SAVE MODEL
# ======================================
joblib.dump(pipeline, "fault_model.pkl")

print("\n✅ Model saved as fault_model.pkl")
