import pandas as pd

# ============================================================
# LOAD DATA
# ============================================================

input_path = "data/telemetry.csv"
output_path = "data/engineered_telemetry.csv"

df = pd.read_csv(input_path)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort chronologically within each service
df = df.sort_values(
    ["service", "timestamp"]
).reset_index(drop=True)


# ============================================================
# TEMPORAL FEATURES
# ============================================================

metrics = [
    "cpu_usage",
    "memory_usage",
    "latency_ms",
    "error_rate",
    "db_connections"
]

for metric in metrics:

    # --------------------------------------------------------
    # Previous observation
    # --------------------------------------------------------

    df[f"{metric}_lag"] = (
        df.groupby("service")[metric]
        .shift(1)
    )

    # --------------------------------------------------------
    # Change from previous observation
    # --------------------------------------------------------

    df[f"{metric}_change"] = (
        df[metric] - df[f"{metric}_lag"]
    )

    # --------------------------------------------------------
    # Past rolling mean
    #
    # shift(1) ensures the current observation is NOT included
    # --------------------------------------------------------

    df[f"{metric}_rolling_mean"] = (
        df.groupby("service")[metric]
        .transform(
            lambda x: x.shift(1).rolling(
                window=3,
                min_periods=1
            ).mean()
        )
    )

    # --------------------------------------------------------
    # Past rolling standard deviation
    # --------------------------------------------------------

    df[f"{metric}_rolling_std"] = (
        df.groupby("service")[metric]
        .transform(
            lambda x: x.shift(1).rolling(
                window=3,
                min_periods=1
            ).std()
        )
    )


# ============================================================
# HANDLE INITIAL MISSING VALUES
# ============================================================

temporal_columns = []

for metric in metrics:
    temporal_columns.extend([
        f"{metric}_lag",
        f"{metric}_change",
        f"{metric}_rolling_mean",
        f"{metric}_rolling_std"
    ])

df[temporal_columns] = (
    df[temporal_columns]
    .fillna(0)
)


# ============================================================
# SAVE ENGINEERED DATA
# ============================================================

df.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("=" * 60)
print("TEMPORAL FEATURE ENGINEERING COMPLETE")
print("=" * 60)

print(f"Records: {len(df):,}")
print(f"Features: {df.shape[1]}")

print("\nNew temporal features:")

for column in temporal_columns:
    print(f"- {column}")

print("\nImportant design:")
print("- Lag features use previous observations")
print("- Rolling features use previous 3 observations")
print("- Current observation is excluded from rolling statistics")

print(f"\nSaved to: {output_path}")