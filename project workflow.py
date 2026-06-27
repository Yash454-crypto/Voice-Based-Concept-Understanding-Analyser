import networkx as nx
import matplotlib.pyplot as plt

# Create directed graph
G = nx.DiGraph()

# Workflow Nodes
nodes = [
    "Start",
    "User Login",
    "Upload Audio",
    "Speech-to-Text",
    "Audio Feature Extraction",
    "Reference Concept",
    "Semantic Similarity Analysis",
    "Filler Word Analysis",
    "Evaluation Engine",
    "Understanding Level",
    "Generate Report",
    "Store Database",
    "End"
]

# Add nodes
G.add_nodes_from(nodes)

# Workflow Edges
edges = [
    ("Start", "User Login"),
    ("User Login", "Upload Audio"),
    ("Upload Audio", "Speech-to-Text"),
    ("Upload Audio", "Audio Feature Extraction"),
    ("Speech-to-Text", "Semantic Similarity Analysis"),
    ("Reference Concept", "Semantic Similarity Analysis"),
    ("Speech-to-Text", "Filler Word Analysis"),
    ("Audio Feature Extraction", "Evaluation Engine"),
    ("Semantic Similarity Analysis", "Evaluation Engine"),
    ("Filler Word Analysis", "Evaluation Engine"),
    ("Evaluation Engine", "Understanding Level"),
    ("Understanding Level", "Generate Report"),
    ("Generate Report", "Store Database"),
    ("Store Database", "End")
]

G.add_edges_from(edges)

# Layout
pos = nx.spring_layout(G, k=2.2, seed=42)

# Draw Nodes
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=3000,
    node_color="lightblue",
    edgecolors="black"
)

# Draw Edges
nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    arrowsize=20,
    width=2
)

# Draw Labels
nx.draw_networkx_labels(
    G,
    pos,
    font_size=9,
    font_weight='bold'
)

plt.title("Voice Based Concept Understanding Analyser Workflow", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()