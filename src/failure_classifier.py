import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================
# 1. LOAD ENGINEERED DATA
# ============================================================

df = pd.read_csv("data/engineered_telemetry.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)

print("=" * 70)
print("FAILURE CLASSIFICATION")
print("=" * 70)


# ============================================================
# 2. DEFINE FEATURES
# ============================================================

target = "failure_type"

drop_columns = [
    "timestamp",
    target
]

X = df.drop(columns=drop_columns)

y = df[target]


# ============================================================
# 3. ONE-HOT ENCODE SERVICE
# ============================================================

X = pd.get_dummies(
    X,
    columns=["service"],
    dtype=int
)


# ============================================================
# 4. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

split_time = df["timestamp"].quantile(0.80)

train_mask = df["timestamp"] < split_time
test_mask = df["timestamp"] >= split_time

X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]


print("\nTraining records:", len(X_train))
print("Testing records: ", len(X_test))

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTesting class distribution:")
print(y_test.value_counts())


# ============================================================
# 5. TRAIN RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ============================================================
# 6. PREDICT
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 7. EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 8. FEATURE IMPORTANCE
# ============================================================

importance = pd.Series(
    model.feature_importances_,
    index=X.columns
)

importance = importance.sort_values(
    ascending=False
)

print("\nTop 15 Features:")

print(
    importance.head(15).to_string()
)


# ============================================================
# 9. CREATE TRUSTWORTHY PREDICTION OUTPUT
# ============================================================

test_context = df.loc[
    test_mask,
    [
        "timestamp",
        "service",
        "failure_type"
    ]
].copy()

test_context["predicted_failure"] = y_pred


# Rename actual failure for clarity

test_context = test_context.rename(
    columns={
        "failure_type": "actual_failure"
    }
)


# ============================================================
# 10. SAVE PREDICTIONS
# ============================================================

test_context.to_csv(
    "data/failure_predictions.csv",
    index=False
)


print("\n" + "=" * 70)
print("PREDICTIONS SAVED")
print("=" * 70)

print("\nColumns:")
print(test_context.columns.tolist())

print("\nSaved to:")
print("data/failure_predictions.csv")