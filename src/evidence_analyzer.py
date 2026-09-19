import pandas as pd


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("data/engineered_telemetry.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(
    ["service", "timestamp"]
).reset_index(drop=True)


print("=" * 70)
print("INCIDENT EVIDENCE ANALYZER")
print("=" * 70)


# ============================================================
# 2. LOAD PREDICTIONS
# ============================================================

predictions = pd.read_csv(
    "data/failure_predictions.csv"
)

predictions["timestamp"] = pd.to_datetime(
    predictions["timestamp"]
)


# ============================================================
# 3. MERGE PREDICTIONS WITH TELEMETRY
# ============================================================

incident_data = predictions.merge(
    df,
    on=["timestamp", "service"],
    how="left"
)


incident_data = incident_data[
    incident_data["predicted_failure"] != "normal"
].copy()


print(
    f"\nDetected incidents: {len(incident_data)}"
)


# ============================================================
# 4. ANALYZE EVIDENCE
# ============================================================

results = []


for _, incident in incident_data.iterrows():

    service = incident["service"]

    timestamp = incident["timestamp"]

    failure = incident["predicted_failure"]


    # --------------------------------------------------------
    # Current telemetry
    # --------------------------------------------------------

    current_cpu = incident["cpu_usage"]

    current_memory = incident["memory_usage"]

    current_latency = incident["latency_ms"]

    current_error = incident["error_rate"]

    current_db = incident["db_connections"]


    # --------------------------------------------------------
    # Temporal changes
    # --------------------------------------------------------

    cpu_change = incident["cpu_usage_change"]

    memory_change = incident["memory_usage_change"]

    latency_change = incident["latency_ms_change"]

    error_change = incident["error_rate_change"]

    db_change = incident["db_connections_change"]


    # ========================================================
    # EVIDENCE SCORES
    # ========================================================

    cpu_evidence = 0

    memory_evidence = 0

    latency_evidence = 0

    error_evidence = 0

    database_evidence = 0


    # CPU evidence

    if current_cpu > 80 or cpu_change > 10:

        cpu_evidence = 1


    # Memory evidence

    if current_memory > 80 or memory_change > 8:

        memory_evidence = 1


    # Latency evidence

    if current_latency > 300 or latency_change > 50:

        latency_evidence = 1


    # Error evidence

    if current_error > 5 or error_change > 2:

        error_evidence = 1


    # Database evidence

    if current_db > 80 or db_change > 10:

        database_evidence = 1


    # ========================================================
    # TOTAL EVIDENCE
    # ========================================================

    total_evidence = (
        cpu_evidence
        + memory_evidence
        + latency_evidence
        + error_evidence
        + database_evidence
    )


    results.append({

        "timestamp": timestamp,

        "service": service,

        "failure": failure,

        "cpu_usage": current_cpu,

        "memory_usage": current_memory,

        "latency_ms": current_latency,

        "error_rate": current_error,

        "db_connections": current_db,

        "cpu_change": cpu_change,

        "memory_change": memory_change,

        "latency_change": latency_change,

        "error_change": error_change,

        "db_connections_change": db_change,

        "cpu_evidence": cpu_evidence,

        "memory_evidence": memory_evidence,

        "latency_evidence": latency_evidence,

        "error_evidence": error_evidence,

        "database_evidence": database_evidence,

        "total_evidence": total_evidence

    })


# ============================================================
# 5. SAVE RESULTS
# ============================================================

evidence_df = pd.DataFrame(results)


evidence_df.to_csv(
    "data/incident_evidence.csv",
    index=False
)


# ============================================================
# 6. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("INCIDENT EVIDENCE")
print("=" * 70)


if not evidence_df.empty:

    print(
        evidence_df[
            [
                "timestamp",
                "service",
                "failure",
                "cpu_evidence",
                "memory_evidence",
                "latency_evidence",
                "error_evidence",
                "database_evidence",
                "total_evidence"
            ]
        ].head(30).to_string(index=False)
    )


print("\n" + "=" * 70)
print("EVIDENCE ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved to:")
print("data/incident_evidence.csv")