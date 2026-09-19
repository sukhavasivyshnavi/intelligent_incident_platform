import numpy as np
import pandas as pd

np.random.seed(42)

SERVICES = [
    "api-gateway",
    "user-service",
    "payment-service",
    "notification-service",
    "database"
]

DAYS = 7
INTERVAL_MINUTES = 5

timestamps = pd.date_range(
    start="2026-01-01",
    periods=(DAYS * 24 * 60) // INTERVAL_MINUTES,
    freq=f"{INTERVAL_MINUTES}min"
)

records = []

# ============================================================
# BASE TELEMETRY
# ============================================================

for timestamp in timestamps:

    for service in SERVICES:

        if service == "api-gateway":
            base_cpu = 45
            base_memory = 55
            base_latency = 120
            base_requests = 900
            base_db_connections = 20

        elif service == "user-service":
            base_cpu = 35
            base_memory = 50
            base_latency = 100
            base_requests = 500
            base_db_connections = 25

        elif service == "payment-service":
            base_cpu = 50
            base_memory = 60
            base_latency = 150
            base_requests = 700
            base_db_connections = 40

        elif service == "notification-service":
            base_cpu = 30
            base_memory = 45
            base_latency = 90
            base_requests = 400
            base_db_connections = 15

        else:
            base_cpu = 55
            base_memory = 65
            base_latency = 80
            base_requests = 1000
            base_db_connections = 60

        # ----------------------------------------------------
        # Daily traffic pattern
        # ----------------------------------------------------

        hour = timestamp.hour

        if 9 <= hour <= 18:
            traffic_multiplier = 1.3
        elif 0 <= hour <= 6:
            traffic_multiplier = 0.7
        else:
            traffic_multiplier = 1.0

        request_rate = (
            base_requests * traffic_multiplier
            + np.random.normal(0, base_requests * 0.05)
        )

        cpu_usage = (
            base_cpu
            + (traffic_multiplier - 1) * 20
            + np.random.normal(0, 4)
        )

        memory_usage = (
            base_memory
            + np.random.normal(0, 3)
        )

        latency = (
            base_latency
            + (request_rate / base_requests) * 20
            + np.random.normal(0, 10)
        )

        db_connections = (
            base_db_connections
            + (request_rate / base_requests) * 10
            + np.random.normal(0, 3)
        )

        error_rate = max(
            0,
            0.2 + np.random.normal(0, 0.05)
        )

        disk_io = max(
            0,
            np.random.normal(50, 10)
        )

        network_traffic = max(
            0,
            request_rate * np.random.uniform(0.8, 1.2)
        )

        restart_count = 0

        records.append({
            "timestamp": timestamp,
            "service": service,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_io": disk_io,
            "network_traffic": network_traffic,
            "request_rate": request_rate,
            "latency_ms": latency,
            "error_rate": error_rate,
            "db_connections": db_connections,
            "restart_count": restart_count,
            "failure_type": "normal"
        })


df = pd.DataFrame(records)


# ============================================================
# INCIDENT INJECTION FUNCTION
# ============================================================

def inject_incident(
    dataframe,
    start,
    end,
    service,
    failure_type
):

    mask = (
        (dataframe["timestamp"] >= pd.Timestamp(start))
        & (dataframe["timestamp"] <= pd.Timestamp(end))
        & (dataframe["service"] == service)
    )

    duration = mask.sum()

    if duration == 0:
        return

    # --------------------------------------------------------
    # Database connection saturation
    # --------------------------------------------------------

    if failure_type == "db_connection_saturation":

        dataframe.loc[mask, "db_connections"] = np.linspace(
            65,
            100,
            duration
        )

        dataframe.loc[mask, "latency_ms"] = np.linspace(
            250,
            1800,
            duration
        )

        dataframe.loc[mask, "error_rate"] = np.linspace(
            1.0,
            8.0,
            duration
        )

    # --------------------------------------------------------
    # Memory leak
    # --------------------------------------------------------

    elif failure_type == "memory_leak":

        dataframe.loc[mask, "memory_usage"] = np.linspace(
            65,
            98,
            duration
        )

        dataframe.loc[mask, "latency_ms"] *= np.linspace(
            1.0,
            2.5,
            duration
        )

        dataframe.loc[mask, "error_rate"] = np.linspace(
            0.3,
            5.0,
            duration
        )

    # --------------------------------------------------------
    # CPU overload
    # --------------------------------------------------------

    elif failure_type == "cpu_overload":

        dataframe.loc[mask, "cpu_usage"] = np.linspace(
            70,
            99,
            duration
        )

        dataframe.loc[mask, "latency_ms"] *= np.linspace(
            1.2,
            3.0,
            duration
        )

        dataframe.loc[mask, "error_rate"] = np.linspace(
            0.5,
            6.0,
            duration
        )

    dataframe.loc[mask, "failure_type"] = failure_type


# ============================================================
# INCIDENT EPISODES
# ============================================================

# ------------------------------------------------------------
# DATABASE SATURATION
# ------------------------------------------------------------

# Training incident
inject_incident(
    df,
    "2026-01-02 14:00",
    "2026-01-02 15:30",
    "payment-service",
    "db_connection_saturation"
)

# Testing incident
inject_incident(
    df,
    "2026-01-06 16:00",
    "2026-01-06 17:00",
    "payment-service",
    "db_connection_saturation"
)


# ------------------------------------------------------------
# MEMORY LEAK
# ------------------------------------------------------------

# Training incident
inject_incident(
    df,
    "2026-01-03 09:00",
    "2026-01-03 12:00",
    "user-service",
    "memory_leak"
)

# Testing incident
inject_incident(
    df,
    "2026-01-06 18:00",
    "2026-01-06 20:00",
    "user-service",
    "memory_leak"
)


# ------------------------------------------------------------
# CPU OVERLOAD
# ------------------------------------------------------------

# Training incident
inject_incident(
    df,
    "2026-01-04 18:00",
    "2026-01-04 19:00",
    "api-gateway",
    "cpu_overload"
)

# Testing incident
inject_incident(
    df,
    "2026-01-07 14:00",
    "2026-01-07 15:00",
    "api-gateway",
    "cpu_overload"
)


# ============================================================
# KEEP VALUES REALISTIC
# ============================================================

df["cpu_usage"] = df["cpu_usage"].clip(0, 100)

df["memory_usage"] = df["memory_usage"].clip(0, 100)

df["error_rate"] = df["error_rate"].clip(0, 100)

numeric_columns = [
    "cpu_usage",
    "memory_usage",
    "disk_io",
    "network_traffic",
    "request_rate",
    "latency_ms",
    "error_rate",
    "db_connections"
]

df[numeric_columns] = df[numeric_columns].round(2)


# ============================================================
# SAVE DATASET
# ============================================================

output_path = "data/telemetry.csv"

df.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("=" * 60)
print("UPDATED TELEMETRY DATASET GENERATED")
print("=" * 60)

print(f"Records: {len(df):,}")

print(f"Services: {df['service'].nunique()}")

print("\nFailure distribution:")
print(df["failure_type"].value_counts())

print("\nIncident episodes:")
print("DB saturation : 2")
print("Memory leaks  : 2")
print("CPU overload  : 2")

print("\nIncident schedule:")
print("TRAIN:")
print("  Jan 02 → DB saturation")
print("  Jan 03 → Memory leak")
print("  Jan 04 → CPU overload")

print("\nTEST:")
print("  Jan 06 → DB saturation")
print("  Jan 06 → Memory leak")
print("  Jan 07 → CPU overload")

print(f"\nSaved to: {output_path}")