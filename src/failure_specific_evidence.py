import pandas as pd
import networkx as nx
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

TELEMETRY_FILE = BASE_DIR / "data" / "engineered_telemetry.csv"
PREDICTIONS_FILE = BASE_DIR / "data" / "failure_predictions.csv"
TIMELINE_FILE = BASE_DIR / "data" / "incident_timeline.csv"

OUTPUT_FILE = BASE_DIR / "data" / "failure_specific_evidence.csv"


telemetry = pd.read_csv(TELEMETRY_FILE)
predictions = pd.read_csv(PREDICTIONS_FILE)
timeline = pd.read_csv(TIMELINE_FILE)

telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"])
predictions["timestamp"] = pd.to_datetime(predictions["timestamp"])
timeline["start_time"] = pd.to_datetime(timeline["start_time"])
timeline["end_time"] = pd.to_datetime(timeline["end_time"])


# Handle either column name
if "failure_type" in timeline.columns:
    failure_column = "failure_type"
elif "failure" in timeline.columns:
    failure_column = "failure"
else:
    raise ValueError(
        "incident_timeline.csv must contain either "
        "'failure_type' or 'failure'."
    )


# ============================================================
# DEPENDENCY GRAPH
# A -> B means A depends on B
# ============================================================

G = nx.DiGraph()

G.add_edges_from([
    ("api-gateway", "user-service"),
    ("api-gateway", "payment-service"),
    ("api-gateway", "notification-service"),
    ("user-service", "database"),
    ("payment-service", "database"),
])


# ============================================================
# FAILURE-SPECIFIC EVIDENCE
# ============================================================

def calculate_failure_specific_evidence(row, failure):

    score = 0
    reasons = []

    # CPU OVERLOAD
    if failure == "cpu_overload":

        if row["cpu_usage"] > 80:
            score += 3
            reasons.append("high_cpu")

        # Rapid CPU increase counts ONLY when CPU
        # is already high.
        if (
            row["cpu_usage"] > 80
            and row["cpu_usage_change"] > 10
        ):
            score += 2
            reasons.append("rapid_cpu_increase")


    # MEMORY LEAK
    elif failure == "memory_leak":

        if row["memory_usage"] > 80:
            score += 3
            reasons.append("high_memory")

        if row["memory_usage_change"] > 8:
            score += 2
            reasons.append("rapid_memory_increase")

        if row["memory_usage_change"] > 3:
            score += 1
            reasons.append("memory_deterioration")


    # DATABASE CONNECTION SATURATION
    elif failure == "db_connection_saturation":

        if row["db_connections"] > 80:
            score += 3
            reasons.append("high_db_connections")

        if row["db_connections_change"] > 10:
            score += 2
            reasons.append("rapid_db_connection_increase")

        if row["latency_ms"] > 300:
            score += 2
            reasons.append("high_latency")

        if row["error_rate"] > 5:
            score += 2
            reasons.append("high_error_rate")

        if row["db_connections_change"] > 2:
            score += 1
            reasons.append("db_connection_deterioration")

        if row["latency_ms_change"] > 30:
            score += 1
            reasons.append("latency_deterioration")

        if row["error_rate_change"] > 0.2:
            score += 1
            reasons.append("error_rate_deterioration")


    return score, reasons


# ============================================================
# BUILD EVIDENCE
# ============================================================

evidence_records = []


for _, episode in timeline.iterrows():

    episode_id = episode["episode_id"]
    affected_service = episode["service"]
    failure = episode[failure_column]
    incident_start = episode["start_time"]

    dependencies = list(G.successors(affected_service))

    if not dependencies:
        continue

    # 30 minutes before incident
    evidence_start = (
        incident_start - pd.Timedelta(minutes=30)
    )

    for dependency in dependencies:

        dependency_data = telemetry[
            (telemetry["service"] == dependency)
            &
            (telemetry["timestamp"] >= evidence_start)
            &
            (telemetry["timestamp"] < incident_start)
        ].copy()

        if dependency_data.empty:
            continue

        best_score = 0
        best_time = None
        best_reasons = []

        for _, row in dependency_data.iterrows():

            score, reasons = calculate_failure_specific_evidence(
                row,
                failure
            )

            if score > best_score:
                best_score = score
                best_time = row["timestamp"]
                best_reasons = reasons

        evidence_records.append({
            "episode_id": episode_id,
            "affected_service": affected_service,
            "failure": failure,
            "dependency": dependency,
            "evidence_score": best_score,
            "evidence_time": best_time,
            "evidence_reason": ",".join(best_reasons)
        })


# ============================================================
# SAVE OUTPUT
# ============================================================

evidence_df = pd.DataFrame(evidence_records)

if evidence_df.empty:

    print("No dependency-specific evidence found.")

else:

    evidence_df = evidence_df.sort_values(
        ["episode_id", "evidence_score"],
        ascending=[True, False]
    )

    evidence_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("FAILURE-SPECIFIC EVIDENCE ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print(f"Records: {len(evidence_df)}")

    print()
    print("Evidence results:")

    print(
        evidence_df[
            [
                "episode_id",
                "affected_service",
                "failure",
                "dependency",
                "evidence_score",
                "evidence_time",
                "evidence_reason"
            ]
        ].to_string(index=False)
    )

    print()
    print("Saved to:")
    print(OUTPUT_FILE)

    print()
    print("=" * 70)
