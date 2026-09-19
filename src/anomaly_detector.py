import pandas as pd
from sklearn.ensemble import IsolationForest

# -----------------------------------
# Load telemetry
# -----------------------------------
df = pd.read_csv("data/telemetry.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

# -----------------------------------
# Features used for anomaly detection
# -----------------------------------
features = [
    "cpu_usage",
    "memory_usage",
    "disk_io",
    "network_traffic",
    "request_rate",
    "latency_ms",
    "error_rate",
    "db_connections",
]

X = df[features]

# -----------------------------------
# Train Isolation Forest
# -----------------------------------
model = IsolationForest(
    n_estimators=200,
    contamination=0.01,
    random_state=42
)

model.fit(X)

# -----------------------------------
# Predict anomalies
# -----------------------------------
df["anomaly_prediction"] = model.predict(X)

# Isolation Forest:
#  1  = normal
# -1  = anomaly

df["anomaly"] = (
    df["anomaly_prediction"] == -1
).astype(int)

# -----------------------------------
# Compare with actual incidents
# -----------------------------------
print("=" * 60)
print("ANOMALY DETECTION RESULTS")
print("=" * 60)

print("\nPredicted anomalies:")
print(df["anomaly"].value_counts())

print("\nActual failure types:")
print(df["failure_type"].value_counts())

print("\nAnomalies by actual failure type:")
print(
    pd.crosstab(
        df["failure_type"],
        df["anomaly"]
    )
)

# -----------------------------------
# Save results
# -----------------------------------
output_path = "data/anomaly_results.csv"

df.to_csv(output_path, index=False)

print(f"\nResults saved to: {output_path}")