from pathlib import Path
import re
import pandas as pd

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RCA_FILE = PROJECT_ROOT / "data" / "root_cause_analysis.csv"

RAG_PROJECT = Path(r"C:\Users\91852\it_incident_rag")
CHROMA_DB = RAG_PROJECT / "chroma_db"

COLLECTION_NAME = "it_incident_knowledge"


# ============================================================
# CHECK RCA
# ============================================================

print("=" * 70)
print("INCIDENT RAG ANALYZER")
print("=" * 70)

if not RCA_FILE.exists():
    raise FileNotFoundError(f"RCA file not found: {RCA_FILE}")

if not CHROMA_DB.exists():
    raise FileNotFoundError(f"Chroma database not found: {CHROMA_DB}")


# ============================================================
# LOAD ROOT CAUSE ANALYSIS
# ============================================================

rca_df = pd.read_csv(RCA_FILE)

high_confidence = rca_df[
    rca_df["root_cause_score"] >= 5
].copy()

if high_confidence.empty:
    print("No high-confidence incidents found.")
    raise SystemExit


print(f"High-confidence incidents: {len(high_confidence)}")


# ============================================================
# EMBEDDINGS
# ============================================================

print("\nLoading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# CONNECT TO EXISTING CHROMA
# ============================================================

print("\nConnecting to incident knowledge base...")

vectorstore = Chroma(
    persist_directory=str(CHROMA_DB),
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings
)

print("Chroma database connected.")


# ============================================================
# LOCAL LLM
# ============================================================

print("\nInitializing local LLM...")

llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

print("LLM initialized.")


# ============================================================
# RETRIEVAL FUNCTION
# ============================================================

def retrieve_evidence(affected_service, failure, root_cause):

    queries = {
        "incident": (
            f"{affected_service} {failure} database "
            f"historical incident 503 errors root cause"
        ),

        "runbook": (
            f"{failure} troubleshooting runbook "
            f"{affected_service} database connections remediation"
        ),

        "deployment": (
            f"{affected_service} deployment database "
            f"configuration version release changes"
        ),

        "log": (
            f"{affected_service} database connection errors "
            f"PostgreSQL logs HTTP 503"
        ),

        "architecture": (
            f"{affected_service} architecture database "
            f"service dependencies PostgreSQL"
        )
    }

    retrieved = []

    print("\nRetrieving evidence by document type...")

    for document_type, query in queries.items():

        try:
            docs = vectorstore.similarity_search(
                query,
                k=3,
                filter={"document_type": document_type}
            )
        except Exception as e:
            print(
                f"Warning: metadata filter failed for "
                f"{document_type}: {e}"
            )
            docs = vectorstore.similarity_search(query, k=3)

        for doc in docs:

            file_name = doc.metadata.get(
                "file_name",
                Path(doc.metadata.get("source", "unknown")).name
            )

            doc_type = doc.metadata.get(
                "document_type",
                "unknown"
            )

            retrieved.append(
                (doc_type, file_name, doc)
            )


    # --------------------------------------------------------
    # Deduplicate by source file
    # --------------------------------------------------------

    unique_sources = {}

    for doc_type, file_name, doc in retrieved:

        if file_name not in unique_sources:
            unique_sources[file_name] = (
                doc_type,
                doc
            )

    return unique_sources


# ============================================================
# ANALYZE INCIDENTS
# ============================================================

for _, incident in high_confidence.iterrows():

    episode_id = int(incident["episode_id"])
    affected_service = incident["affected_service"]
    failure = incident["failure"]
    root_cause = incident["root_cause"]

    rca_score = float(incident["root_cause_score"])
    temporal_score = float(incident["temporal_score"])
    evidence_score = float(incident["evidence_score"])
    dependency_score = float(incident["dependency_score"])

    print("\n")
    print("=" * 70)
    print(f"INCIDENT EPISODE {episode_id}")
    print("=" * 70)

    print(f"Affected Service : {affected_service}")
    print(f"Detected Failure : {failure}")
    print(f"ML Root Cause    : {root_cause}")
    print(f"RCA Score        : {rca_score}")
    print(f"Temporal Score   : {temporal_score}")
    print(f"Evidence Score   : {evidence_score}")
    print(f"Dependency Score : {dependency_score}")


    # ========================================================
    # RETRIEVE
    # ========================================================

    sources = retrieve_evidence(
        affected_service,
        failure,
        root_cause
    )

    if not sources:
        print("\nNo evidence retrieved.")
        continue


    # ========================================================
    # DISPLAY SOURCES
    # ========================================================

    print("\n")
    print("-" * 70)
    print("RETRIEVED SOURCES")
    print("-" * 70)

    for i, (file_name, (doc_type, doc)) in enumerate(
        sources.items(),
        start=1
    ):

        print(f"\n[{i}] {file_name}")
        print(f"    Type: {doc_type}")
        print("    Content preview:")
        print(
            doc.page_content[:500]
            .replace("\n", " ")
        )


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context_parts = []

    for file_name, (doc_type, doc) in sources.items():

        context_parts.append(
            f"""
SOURCE FILE: {file_name}
DOCUMENT TYPE: {doc_type}

CONTENT:
{doc.page_content}
"""
        )

    context = "\n".join(context_parts)

    available_sources = list(sources.keys())


    # ========================================================
    # GROUNDED PROMPT
    # ========================================================

    prompt = f"""
You are an IT incident investigation assistant.

You are analyzing one machine-learning-detected incident.

INCIDENT INFORMATION
--------------------
Episode ID: {episode_id}
Affected Service: {affected_service}
Detected Failure: {failure}
ML Root Cause: {root_cause}
Internal RCA Score: {rca_score}
Temporal Evidence Score: {temporal_score}
Evidence Score: {evidence_score}
Dependency Score: {dependency_score}


IMPORTANT SOURCE-GROUNDING RULES
--------------------------------

1. The ML root cause is a SYSTEM OUTPUT.
   Treat it as a model conclusion, not as documentary evidence.

2. Use ONLY the retrieved source content below for
   documentary evidence.

3. You may mention ONLY these source filenames:

{available_sources}

4. NEVER invent:
   - filenames
   - incident IDs
   - runbook IDs
   - log filenames
   - database IDs
   - deployment IDs
   - configuration names

5. If a requested piece of information is not present
   in the retrieved evidence, say:

   "Not available in the retrieved evidence."

6. Do not use outside knowledge.

7. Clearly separate:
   - ML finding
   - documented evidence
   - investigation/remediation guidance

8. The RCA score is an internal scoring value.
   Do NOT describe it as a probability or percentage.

9. At the end, provide an "Evidence Sources" section.
   Every filename in that section MUST come from the
   allowed source list above.


RETRIEVED IT EVIDENCE
---------------------

{context}


TASK
----

Produce an engineer-friendly incident report with:

1. Incident Summary
2. ML Root Cause Finding
3. Supporting Evidence
4. Relevant Historical/Operational Evidence
5. Recommended Investigation Steps
6. Recommended Remediation Steps
7. Evidence Sources

Keep the report factual and concise.

If the evidence is insufficient for a conclusion,
explicitly state that.


INCIDENT REPORT
"""


    # ========================================================
    # LLM
    # ========================================================

    print("\n")
    print("-" * 70)
    print("GENERATING GROUNDED INCIDENT REPORT")
    print("-" * 70)

    response = llm.invoke(prompt)

    report = response.content


    # ========================================================
    # BASIC SOURCE VALIDATION
    # ========================================================

    allowed_sources = set(available_sources)

    referenced_files = set(
        re.findall(
            r'[\w.\-]+(?:\.txt|\.md|\.log|\.csv)',
            report
        )
    )

    unknown_files = referenced_files - allowed_sources

    print("\n")
    print("=" * 70)
    print("SOURCE VALIDATION")
    print("=" * 70)

    if unknown_files:

        print("WARNING: Possible hallucinated source filenames:")
        for file_name in sorted(unknown_files):
            print(" -", file_name)

    else:

        print("PASS: No unknown source filenames detected.")


    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL GROUNDED INCIDENT REPORT")
    print("=" * 70)

    print(report)

    print("\n")
    print("=" * 70)
    print("RAG ANALYSIS COMPLETE")
    print("=" * 70)
