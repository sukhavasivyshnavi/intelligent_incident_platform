from pathlib import Path
import sys

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RCA_FILE = BASE_DIR / "data" / "root_cause_analysis.csv"

RAG_PROJECT = Path(r"C:\Users\91852\it_incident_rag")

RAG_DATA = RAG_PROJECT / "data"
RAG_DB = RAG_PROJECT / "chroma_db"


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

print("=" * 70)
print("INCIDENT RAG INTEGRATION")
print("=" * 70)

print("\nChecking RCA output...")

if not RCA_FILE.exists():
    print("ERROR: root_cause_analysis.csv not found.")
    print("Run:")
    print("python src\\root_cause_analyzer.py")
    sys.exit(1)

print("RCA output found.")


print("\nChecking RAG project...")

if not RAG_PROJECT.exists():
    print(f"ERROR: RAG project not found: {RAG_PROJECT}")
    sys.exit(1)

print("RAG project found.")


print("\nChecking RAG knowledge base...")

required_files = [
    RAG_DATA / "incidents" / "INC-1001.txt",
    RAG_DATA / "runbooks" / "payment_api_503_runbook.md",
    RAG_DATA / "deployments" / "payment-api-v2.4.1.txt",
    RAG_DATA / "logs" / "payment_api_incident_1001.log",
    RAG_DATA / "architecture" / "payment_api_architecture.md",
]

for file in required_files:

    if file.exists():
        print(f"[OK] {file.name}")
    else:
        print(f"[MISSING] {file}")


# ============================================================
# SHOW RCA INCIDENTS
# ============================================================

import pandas as pd

rca = pd.read_csv(RCA_FILE)

print("\n" + "=" * 70)
print("AVAILABLE RCA INCIDENTS")
print("=" * 70)

print(
    rca[
        [
            "episode_id",
            "affected_service",
            "failure",
            "root_cause",
            "root_cause_score"
        ]
    ].to_string(index=False)
)


# ============================================================
# BUILD RAG QUERY FOR STRONG RCA
# ============================================================

valid_rca = rca[
    rca["root_cause_score"] >= 5
].copy()


if valid_rca.empty:

    print("\nNo high-confidence RCA incidents found.")

else:

    print("\n" + "=" * 70)
    print("INCIDENTS READY FOR RAG ANALYSIS")
    print("=" * 70)

    for _, row in valid_rca.iterrows():

        query = f"""
Investigate this IT incident.

Affected service:
{row["affected_service"]}

Detected failure:
{row["failure"]}

Machine-learning root cause:
{row["root_cause"]}

RCA confidence score:
{row["root_cause_score"]}

Temporal evidence score:
{row["temporal_score"]}

Dependency evidence score:
{row["evidence_score"]}

Explain:
1. What happened?
2. What evidence supports the root cause?
3. What runbook or historical incident is relevant?
4. What should the engineer investigate next?
5. What remediation steps are supported by the available IT documents?

Use only evidence from the RAG knowledge base.
"""

        print("\n" + "-" * 70)
        print(f"EPISODE {row['episode_id']}")
        print("-" * 70)
        print(query)


print("\n" + "=" * 70)
print("RAG INTEGRATION CHECK COMPLETE")
print("=" * 70)
