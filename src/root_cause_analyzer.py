import pandas as pd
import networkx as nx

print("=" * 70)
print("ROOT-CAUSE ANALYSIS ENGINE")
print("=" * 70)

# ============================================================
# LOAD DATA
# ============================================================

predictions = pd.read_csv("data/failure_predictions.csv")
timeline = pd.read_csv("data/incident_timeline.csv")
evidence = pd.read_csv("data/incident_evidence.csv")
failure_specific = pd.read_csv(
    "data/failure_specific_evidence.csv"
)

predictions["timestamp"] = pd.to_datetime(
    predictions["timestamp"]
)

timeline["start_time"] = pd.to_datetime(
    timeline["start_time"]
)

timeline["end_time"] = pd.to_datetime(
    timeline["end_time"]
)

evidence["timestamp"] = pd.to_datetime(
    evidence["timestamp"]
)

failure_specific["evidence_time"] = pd.to_datetime(
    failure_specific["evidence_time"]
)


# ============================================================
# DEPENDENCY GRAPH
# A -> B means A depends on B
# ============================================================

graph = nx.DiGraph()

graph.add_edges_from([
    ("api-gateway", "user-service"),
    ("api-gateway", "payment-service"),
    ("api-gateway", "notification-service"),
    ("user-service", "database"),
    ("payment-service", "database"),
])


# ============================================================
# FAILURE SEVERITY
# ============================================================

severity_score = {
    "cpu_overload": 3,
    "memory_leak": 3,
    "db_connection_saturation": 4
}

results = []


# ============================================================
# ANALYZE EACH INCIDENT
# ============================================================

for _, incident in timeline.iterrows():

    episode_id = incident["episode_id"]
    affected_service = incident["service"]
    failure = incident["failure"]

    start_time = incident["start_time"]
    end_time = incident["end_time"]


    # --------------------------------------------------------
    # Incident evidence
    # --------------------------------------------------------

    incident_evidence = evidence[
        (evidence["service"] == affected_service)
        & (evidence["timestamp"] >= start_time)
        & (evidence["timestamp"] <= end_time)
    ]

    peak_evidence = (
        incident_evidence["total_evidence"].max()
        if not incident_evidence.empty
        else 0
    )


    # --------------------------------------------------------
    # Find dependency candidates
    # --------------------------------------------------------

    dependencies = list(
        graph.successors(affected_service)
    )

    candidates = []


    for dependency in dependencies:

        # ----------------------------------------------------
        # FAILURE-SPECIFIC EVIDENCE
        # ----------------------------------------------------

        specific = failure_specific[
            (failure_specific["episode_id"] == episode_id)
            & (
                failure_specific["dependency"]
                == dependency
            )
        ]

        if specific.empty:

            specific_score = 0
            specific_time = pd.NaT
            specific_reason = ""

        else:

            best_specific = specific.loc[
                specific["evidence_score"].idxmax()
            ]

            specific_score = float(
                best_specific["evidence_score"]
            )

            specific_time = (
                best_specific["evidence_time"]
            )

            specific_reason = (
                best_specific["evidence_reason"]
            )


        # ----------------------------------------------------
        # TEMPORAL RELATIONSHIP
        # ----------------------------------------------------

        temporal_score = 0

        dependency_predictions = predictions[
            (predictions["service"] == dependency)
            & (
                predictions["predicted_failure"]
                != "normal"
            )
            & (
                predictions["timestamp"] < start_time
            )
        ]

        if not dependency_predictions.empty:

            temporal_score = 3


        # Failure-specific evidence occurring before
        # the affected-service incident gives strong
        # temporal precedence.

        if (
            pd.notna(specific_time)
            and specific_time < start_time
        ):

            temporal_score = 5


        # ----------------------------------------------------
        # GENERIC TELEMETRY EVIDENCE
        # ----------------------------------------------------

        dependency_evidence = evidence[
            (evidence["service"] == dependency)
            & (
                evidence["timestamp"] < start_time
            )
            & (
                evidence["timestamp"]
                >= start_time
                - pd.Timedelta(minutes=30)
            )
        ]

        generic_score = (
            dependency_evidence["total_evidence"].max()
            if not dependency_evidence.empty
            else 0
        )

        generic_score = min(
            generic_score,
            3
        )


        # ----------------------------------------------------
        # ARCHITECTURAL DEPENDENCY
        # ----------------------------------------------------

        # Architecture is only a weak prior.
        dependency_score = 1


        # ----------------------------------------------------
        # IMPACT
        # ----------------------------------------------------

        downstream_services = len(
            list(graph.predecessors(dependency))
        )

        impact_score = min(
            downstream_services,
            2
        )


        # ----------------------------------------------------
        # FINAL EVIDENCE SCORE
        # ----------------------------------------------------

        evidence_score = min(
            specific_score,
            5
        )

        # Generic evidence is only fallback evidence.
        if evidence_score == 0:

            evidence_score = min(
                generic_score,
                2
            )


        # ----------------------------------------------------
        # TOTAL RCA SCORE
        # ----------------------------------------------------

        total_score = (
            temporal_score
            + evidence_score
            + dependency_score
            + impact_score
        )


        # ----------------------------------------------------
        # STRONG ROOT-CAUSE VALIDATION
        # ----------------------------------------------------

        # A dependency can become the root cause ONLY when:
        #
        # 1. Evidence occurred before the incident.
        # 2. Failure-specific evidence score >= 2.
        #
        # Generic evidence alone is NOT enough.

        valid_root_cause = (
            temporal_score >= 5
            and specific_score >= 2
        )


        candidates.append({

            "candidate": dependency,

            "temporal_score":
                temporal_score,

            "evidence_score":
                evidence_score,

            "specific_score":
                specific_score,

            "dependency_score":
                dependency_score,

            "impact_score":
                impact_score,

            "total_score":
                total_score,

            "valid_root_cause":
                valid_root_cause,

            "specific_reason":
                specific_reason
        })


    # ========================================================
    # SELECT ROOT CAUSE
    # ========================================================

    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate["valid_root_cause"]
    ]


    if valid_candidates:

        best = max(
            valid_candidates,
            key=lambda x: x["total_score"]
        )

        root_cause = best["candidate"]
        root_score = best["total_score"]

    else:

        # No strong dependency evidence.
        # Do NOT invent a root cause.

        root_cause = affected_service

        root_score = severity_score.get(
            failure,
            1
        )

        best = {
            "temporal_score": 0,
            "evidence_score": peak_evidence,
            "dependency_score": 0,
            "impact_score": 0
        }


    # ========================================================
    # SAVE RESULT
    # ========================================================

    results.append({

        "episode_id":
            episode_id,

        "affected_service":
            affected_service,

        "failure":
            failure,

        "start_time":
            start_time,

        "end_time":
            end_time,

        "root_cause":
            root_cause,

        "root_cause_score":
            root_score,

        "temporal_score":
            best["temporal_score"],

        "evidence_score":
            best["evidence_score"],

        "dependency_score":
            best["dependency_score"],

        "impact_score":
            best["impact_score"],

        "incident_peak_evidence":
            peak_evidence
    })


# ============================================================
# SAVE RCA RESULTS
# ============================================================

rca_df = pd.DataFrame(results)

rca_df = rca_df.sort_values(
    "root_cause_score",
    ascending=False
)


print("\n" + "=" * 70)
print("RCA RESULTS")
print("=" * 70)

if not rca_df.empty:

    print(
        rca_df[
            [
                "episode_id",
                "affected_service",
                "failure",
                "root_cause",
                "root_cause_score",
                "temporal_score",
                "evidence_score",
                "dependency_score",
                "impact_score"
            ]
        ].to_string(index=False)
    )

else:

    print("No incidents found.")


rca_df.to_csv(
    "data/root_cause_analysis.csv",
    index=False
)


print("\n" + "=" * 70)
print("ROOT-CAUSE ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved to:")
print("data/root_cause_analysis.csv")
