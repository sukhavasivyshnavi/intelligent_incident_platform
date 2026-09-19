import pandas as pd
import networkx as nx

telemetry = pd.read_csv("data/engineered_telemetry.csv")
timeline = pd.read_csv("data/incident_timeline.csv")

telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"])
timeline["start_time"] = pd.to_datetime(timeline["start_time"])
timeline["end_time"] = pd.to_datetime(timeline["end_time"])

graph = nx.DiGraph()

dependencies = [
    ("api-gateway", "user-service"),
    ("api-gateway", "payment-service"),
    ("api-gateway", "notification-service"),
    ("user-service", "database"),
    ("payment-service", "database"),
]

graph.add_edges_from(dependencies)


def calculate_evidence(row):

    evidence = 0
    reasons = []

    if row["cpu_usage"] > 80 or row["cpu_usage_change"] > 10:
        evidence += 1
        reasons.append("high_cpu")

    if row["memory_usage"] > 80 or row["memory_usage_change"] > 8:
        evidence += 1
        reasons.append("high_memory")

    if row["latency_ms"] > 300 or row["latency_ms_change"] > 50:
        evidence += 1
        reasons.append("high_latency")

    if row["error_rate"] > 5 or row["error_rate_change"] > 2:
        evidence += 1
        reasons.append("high_error_rate")

    if row["db_connections"] > 80 or row["db_connections_change"] > 10:
        evidence += 1
        reasons.append("high_db_connections")

    return evidence, ",".join(reasons)


evidence_records = []

for _, incident in timeline.iterrows():

    episode_id = incident["episode_id"]
    affected_service = incident["service"]
    incident_start = incident["start_time"]

    dependencies_of_service = list(
        graph.successors(affected_service)
    )

    for dependency in dependencies_of_service:

        window_start = incident_start - pd.Timedelta(minutes=30)

        dependency_data = telemetry[
            (telemetry["service"] == dependency)
            & (telemetry["timestamp"] >= window_start)
            & (telemetry["timestamp"] <= incident_start)
        ].copy()

        if dependency_data.empty:
            continue

        calculated = dependency_data.apply(
            calculate_evidence,
            axis=1
        )

        dependency_data["evidence_score"] = [
            item[0] for item in calculated
        ]

        dependency_data["evidence_reason"] = [
            item[1] for item in calculated
        ]

        peak_row = dependency_data.loc[
            dependency_data["evidence_score"].idxmax()
        ]

        evidence_records.append({

            "episode_id": episode_id,
            "affected_service": affected_service,
            "dependency": dependency,
            "incident_start": incident_start,
            "dependency_peak_evidence": peak_row["evidence_score"],
            "dependency_evidence_time": peak_row["timestamp"],
            "evidence_reason": peak_row["evidence_reason"],
            "cpu_usage": peak_row["cpu_usage"],
            "memory_usage": peak_row["memory_usage"],
            "latency_ms": peak_row["latency_ms"],
            "error_rate": peak_row["error_rate"],
            "db_connections": peak_row["db_connections"]
        })


result = pd.DataFrame(evidence_records)

print("=" * 70)
print("DEPENDENCY TELEMETRY EVIDENCE")
print("=" * 70)

if not result.empty:

    print(
        result[
            [
                "episode_id",
                "affected_service",
                "dependency",
                "dependency_peak_evidence",
                "dependency_evidence_time",
                "evidence_reason"
            ]
        ].to_string(index=False)
    )

else:

    print("No dependency evidence found.")


result.to_csv(
    "data/dependency_evidence.csv",
    index=False
)

print("\n" + "=" * 70)
print("DEPENDENCY EVIDENCE ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved to:")
print("data/dependency_evidence.csv")
