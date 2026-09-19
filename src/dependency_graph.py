import networkx as nx
import matplotlib.pyplot as plt


# ============================================================
# SERVICE DEPENDENCY GRAPH
# ============================================================

graph = nx.DiGraph()

# ------------------------------------------------------------
# Services
# ------------------------------------------------------------

services = [
    "api-gateway",
    "user-service",
    "payment-service",
    "notification-service",
    "database"
]

graph.add_nodes_from(services)


# ------------------------------------------------------------
# Dependencies
#
# A -> B means:
# A depends on B
# ------------------------------------------------------------

dependencies = [
    ("api-gateway", "user-service"),
    ("api-gateway", "payment-service"),
    ("api-gateway", "notification-service"),

    ("user-service", "database"),
    ("payment-service", "database")
]

graph.add_edges_from(dependencies)


# ============================================================
# DISPLAY GRAPH
# ============================================================

print("=" * 60)
print("SERVICE DEPENDENCY GRAPH")
print("=" * 60)

print("\nServices:")
for service in graph.nodes:
    print(f"- {service}")

print("\nDependencies:")

for source, target in graph.edges:
    print(f"- {source} -> {target}")


# ============================================================
# SAVE GRAPH VISUALIZATION
# ============================================================

plt.figure(figsize=(10, 7))

position = nx.spring_layout(
    graph,
    seed=42
)

nx.draw(
    graph,
    position,
    with_labels=True,
    node_size=3000,
    arrows=True,
    font_size=9
)

plt.title("IT Service Dependency Graph")

plt.tight_layout()

plt.savefig(
    "reports/service_dependency_graph.png",
    dpi=300
)

plt.show()


print("\nGraph saved to:")
print("reports/service_dependency_graph.png")