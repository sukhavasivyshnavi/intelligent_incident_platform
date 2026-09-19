import pandas as pd
import matplotlib.pyplot as plt

# Load telemetry
df = pd.read_csv("data/telemetry.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Focus on payment-service
payment = df[df["service"] == "payment-service"].copy()

# Plot latency
plt.figure(figsize=(14, 5))

plt.plot(
    payment["timestamp"],
    payment["latency_ms"],
    label="Latency"
)

# Highlight failure periods
failure = payment[payment["failure_type"] != "normal"]

plt.scatter(
    failure["timestamp"],
    failure["latency_ms"],
    label="Failure"
)

plt.title("Payment Service — Latency Over Time")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("reports/payment_latency.png")

plt.show()