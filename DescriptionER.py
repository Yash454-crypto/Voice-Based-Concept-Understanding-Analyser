from graphviz import Digraph

# Create ER Diagram
er = Digraph("ER_Diagram", filename="ER_Diagram", format="png")
er.attr(rankdir="LR", splines="ortho", nodesep="0.5", ranksep="0.8")

# -----------------------------
# Entity Definitions
# -----------------------------

def entity(name, fields, color):
    label = f"""<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">
    <TR><TD BGCOLOR="{color}"><B>{name}</B></TD></TR>
    """
    for f in fields:
        label += f"<TR><TD ALIGN='LEFT'>{f}</TD></TR>"
    label += "</TABLE>>"

    er.node(name, label=label, shape="plaintext")


entity("USER", [
    "PK user_id INT",
    "name VARCHAR(100)",
    "email VARCHAR(150)",
    "role VARCHAR(20)",
    "created_at DATETIME"
], "#D6D6FF")

entity("AUDIO_FILE", [
    "PK audio_id INT",
    "FK user_id INT",
    "file_name VARCHAR(255)",
    "file_path VARCHAR(255)",
    "duration_sec FLOAT",
    "uploaded_at DATETIME",
    "status VARCHAR(20)"
], "#FFE4B5")

entity("REFERENCE_CONCEPT", [
    "PK ref_concept_id INT",
    "concept_title VARCHAR(255)",
    "concept_text TEXT",
    "created_at DATETIME"
], "#FFD6D6")

entity("TRANSCRIPT", [
    "PK transcript_id INT",
    "FK audio_id INT",
    "transcript_text TEXT",
    "created_at DATETIME"
], "#D6E6FF")

entity("AUDIO_FEATURE", [
    "PK feature_id INT",
    "FK audio_id INT",
    "pause_ratio FLOAT",
    "rms_energy FLOAT",
    "zero_crossing_rate FLOAT",
    "duration_sec FLOAT",
    "created_at DATETIME"
], "#D6FFFF")

entity("FILLER_WORD_STATS", [
    "PK filler_id INT",
    "FK transcript_id INT",
    "filler_word_count INT",
    "total_words INT",
    "filler_ratio FLOAT",
    "created_at DATETIME"
], "#EEEEEE")

entity("SEMANTIC_SIMILARITY", [
    "PK similarity_id INT",
    "FK transcript_id INT",
    "FK ref_concept_id INT",
    "similarity_score FLOAT",
    "created_at DATETIME"
], "#DCEBFF")

entity("EVALUATION_RESULT", [
    "PK result_id INT",
    "FK audio_id INT",
    "FK ref_concept_id INT",
    "overall_score FLOAT",
    "understanding_level VARCHAR(20)",
    "created_at DATETIME",
    "notes TEXT"
], "#E8F5E9")

entity("REPORT", [
    "PK report_id INT",
    "FK result_id INT",
    "pdf_path VARCHAR(255)",
    "generated_at DATETIME",
    "file_size_kb INT"
], "#E6D6FF")

entity("SESSION", [
    "PK session_id INT",
    "FK user_id INT",
    "started_at DATETIME",
    "ended_at DATETIME",
    "status VARCHAR(20)"
], "#FFE5CC")

# -----------------------------
# Relationship Helper
# -----------------------------

def relation(name):
    er.node(name, label=name, shape="diamond")

# Relationships
relation("uploads")
relation("generates")
relation("used_in")
relation("analyzed_for")
relation("compared_with")
relation("evaluated_as")
relation("belongs_to")
relation("report_gen")

# -----------------------------
# Connections
# -----------------------------

# USER uploads AUDIO_FILE
er.edge("USER", "uploads", label="1")
er.edge("uploads", "AUDIO_FILE", label="N")

# AUDIO_FILE generates TRANSCRIPT
er.edge("AUDIO_FILE", "generates", label="1")
er.edge("generates", "TRANSCRIPT", label="1")

# AUDIO_FILE used in AUDIO_FEATURE
er.edge("AUDIO_FILE", "used_in", label="1")
er.edge("used_in", "AUDIO_FEATURE", label="1")

# TRANSCRIPT analyzed for AUDIO_FEATURE
er.edge("TRANSCRIPT", "analyzed_for", label="1")
er.edge("analyzed_for", "AUDIO_FEATURE", label="1")

# TRANSCRIPT analyzed for FILLER_WORD_STATS
er.edge("TRANSCRIPT", "FILLER_WORD_STATS", label="1")

# TRANSCRIPT compared with SEMANTIC_SIMILARITY
er.edge("TRANSCRIPT", "compared_with", label="1")
er.edge("compared_with", "SEMANTIC_SIMILARITY", label="1")

# REFERENCE_CONCEPT to SEMANTIC_SIMILARITY
er.edge("REFERENCE_CONCEPT", "SEMANTIC_SIMILARITY", label="1")

# AUDIO_FILE evaluated as EVALUATION_RESULT
er.edge("AUDIO_FILE", "evaluated_as", label="1")
er.edge("evaluated_as", "EVALUATION_RESULT", label="N")

# REFERENCE_CONCEPT to EVALUATION_RESULT
er.edge("REFERENCE_CONCEPT", "EVALUATION_RESULT", label="1")

# AUDIO_FEATURE generates REPORT
er.edge("AUDIO_FEATURE", "report_gen", label="1")
er.edge("report_gen", "REPORT", label="1")

# EVALUATION_RESULT to REPORT
er.edge("EVALUATION_RESULT", "REPORT", label="1")

# USER to SESSION
er.edge("USER", "SESSION", label="1")

# SESSION belongs to EVALUATION_RESULT
er.edge("SESSION", "belongs_to", label="N")
er.edge("belongs_to", "EVALUATION_RESULT", label="1")

# -----------------------------
# Generate File
# -----------------------------
er.render(view=True)

print("ER Diagram generated successfully!")