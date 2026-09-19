import pandas as pd


# ============================================================
# 1. LOAD DATA
# ============================================================

predictions = pd.read_csv(
    "data/failure_predictions.csv"
)

evidence = pd.read_csv(
    "data/incident_evidence.csv"
)

predictions["timestamp"] = pd.to_datetime(
    predictions["timestamp"]
)

evidence["timestamp"] = pd.to_datetime(
    evidence["timestamp"]
)


print("=" * 70)
print("INCIDENT TIMELINE ANALYZER")
print("=" * 70)


# ============================================================
# 2. MERGE PREDICTIONS + EVIDENCE
# ============================================================

df = predictions.merge(
    evidence,
    on=["timestamp", "service"],
    how="left"
)

df = df[
    df["predicted_failure"] != "normal"
].copy()

df = df.sort_values(
    ["service", "timestamp"]
).reset_index(drop=True)


print(f"\nIncident records: {len(df)}")


# ============================================================
# 3. IDENTIFY INCIDENT EPISODES
# ============================================================

episodes = []

episode_id = 0

previous_service = None
previous_failure = None
previous_time = None


for _, row in df.iterrows():

    current_service = row["service"]
    current_failure = row["predicted_failure"]
    current_time = row["timestamp"]


    # Start a new episode when:
    #
    # 1. service changes
    # 2. failure type changes
    # 3. gap between records > 5 minutes

    new_episode = (

        previous_service != current_service

        or previous_failure != current_failure

        or previous_time is None

        or (
            current_time - previous_time
        ).total_seconds() > 300
    )


    if new_episode:

        episode_id += 1


    row_data = row.to_dict()

    row_data["episode_id"] = episode_id

    episodes.append(row_data)


    previous_service = current_service
    previous_failure = current_failure
    previous_time = current_time


episode_df = pd.DataFrame(episodes)


# ============================================================
# 4. SUMMARIZE EPISODES
# ============================================================

summaries = []


for episode_id, group in episode_df.groupby(
    "episode_id"
):

    group = group.sort_values("timestamp")


    start_time = group["timestamp"].min()

    end_time = group["timestamp"].max()


    duration_minutes = (
        end_time - start_time
    ).total_seconds() / 60


    peak_evidence = group[
        "total_evidence"
    ].max()


    peak_latency = group[
        "latency_ms"
    ].max()


    peak_error_rate = group[
        "error_rate"
    ].max()


    summaries.append({

        "episode_id": episode_id,

        "service":
            group["service"].iloc[0],

        "failure":
            group["predicted_failure"].iloc[0],

        "start_time":
            start_time,

        "end_time":
            end_time,

        "duration_minutes":
            duration_minutes,

        "records":
            len(group),

        "peak_evidence":
            peak_evidence,

        "peak_latency_ms":
            peak_latency,

        "peak_error_rate":
            peak_error_rate

    })


# ============================================================
# 5. CREATE SUMMARY DATAFRAME
# ============================================================

timeline_df = pd.DataFrame(
    summaries
)


# ============================================================
# 6. DISPLAY
# ============================================================

print("\n" + "=" * 70)
print("INCIDENT EPISODES")
print("=" * 70)


if not timeline_df.empty:

    print(
        timeline_df.to_string(
            index=False
        )
    )

else:

    print("No incidents found.")


# ============================================================
# 7. SAVE
# ============================================================

timeline_df.to_csv(
    "data/incident_timeline.csv",
    index=False
)


print("\n" + "=" * 70)
print("TIMELINE ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved to:")
print("data/incident_timeline.csv")