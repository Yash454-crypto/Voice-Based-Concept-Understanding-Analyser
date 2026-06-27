"""
ER Diagram Generator
Voice-Based Concept Understanding Analyser
Uses Graphviz to render entities, attributes, and relationships.
"""

from graphviz import Digraph

dot = Digraph("ER_Diagram", format="png")
dot.attr(rankdir="LR", splines="spline", bgcolor="white")
dot.attr("graph", fontname="Helvetica", label="ER Diagram: Voice-Based Concept Understanding Analyser",
         labelloc="t", fontsize="20")
dot.attr("node", fontname="Helvetica")
dot.attr("edge", fontname="Helvetica", fontsize="10")

# ---------- Entity definitions (PK marked with *) ----------
entities = {
    "STUDENT": ["*student_id", "name", "email", "password", "registration_date"],
    "SUBJECT": ["*subject_id", "subject_name", "description"],
    "TOPIC": ["*topic_id", "subject_id (FK)", "topic_name", "topic_description"],
    "CONCEPT": ["*concept_id", "topic_id (FK)", "concept_name", "concept_definition", "keywords"],
    "SESSION": ["*session_id", "student_id (FK)", "topic_id (FK)", "session_date", "session_status"],
    "AUDIO_RECORDING": ["*audio_id", "session_id (FK)", "file_path", "duration_seconds", "recorded_at", "audio_format"],
    "TRANSCRIPT": ["*transcript_id", "audio_id (FK)", "transcribed_text", "confidence_score", "language", "generated_at"],
    "CONCEPT_ANALYSIS": ["*analysis_id", "transcript_id (FK)", "concept_id (FK)", "understanding_score",
                          "understanding_level", "matched_keywords", "missing_keywords", "analyzed_at"],
    "QUESTION": ["*question_id", "concept_id (FK)", "question_text", "question_type", "difficulty_level"],
    "RESPONSE": ["*response_id", "session_id (FK)", "question_id (FK)", "spoken_answer", "accuracy_score", "response_time"],
    "FEEDBACK": ["*feedback_id", "analysis_id (FK)", "feedback_text", "suggestion", "improvement_area", "created_at"],
    "REPORT": ["*report_id", "student_id (FK)", "session_id (FK)", "overall_score", "strengths", "weaknesses", "generated_on"],
}

# Colors for visual grouping
entity_color = "#E8F0FE"
header_color = "#4285F4"

def make_label(name, attrs):
    """Build an HTML-like table label for an entity box."""
    rows = "".join(
        f'<TR><TD ALIGN="LEFT" BGCOLOR="{entity_color}">{a}</TD></TR>'
        for a in attrs
    )
    return f'''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">
        <TR><TD BGCOLOR="{header_color}"><FONT COLOR="white"><B>{name}</B></FONT></TD></TR>
        {rows}
    </TABLE>
    >'''

# ---------- Add entity nodes ----------
for name, attrs in entities.items():
    dot.node(name, label=make_label(name, attrs), shape="plain")

# ---------- Relationships (with cardinality labels) ----------
relationships = [
    ("STUDENT", "SESSION", "1", "N", "attends"),
    ("SUBJECT", "TOPIC", "1", "N", "contains"),
    ("TOPIC", "CONCEPT", "1", "N", "includes"),
    ("TOPIC", "SESSION", "1", "N", "covered in"),
    ("SESSION", "AUDIO_RECORDING", "1", "N", "generates"),
    ("AUDIO_RECORDING", "TRANSCRIPT", "1", "1", "produces"),
    ("TRANSCRIPT", "CONCEPT_ANALYSIS", "1", "N", "analyzed for"),
    ("CONCEPT", "CONCEPT_ANALYSIS", "1", "N", "evaluated in"),
    ("CONCEPT", "QUESTION", "1", "N", "has"),
    ("SESSION", "RESPONSE", "1", "N", "includes"),
    ("QUESTION", "RESPONSE", "1", "N", "answered in"),
    ("CONCEPT_ANALYSIS", "FEEDBACK", "1", "N", "generates"),
    ("STUDENT", "REPORT", "1", "N", "receives"),
    ("SESSION", "REPORT", "1", "1", "summarized in"),
]

for src, dst, card_src, card_dst, label in relationships:
    dot.edge(src, dst,
              label=f"  {label}  ",
              taillabel=card_src,
              headlabel=card_dst,
              labeldistance="2",
              color="#5F6368",
              fontcolor="#202124")

# ---------- Render ----------
output_path = "/mnt/user-data/outputs/voice_concept_analyser_er_diagram"
dot.render(output_path, cleanup=True)
print(f"Diagram saved to: {output_path}.png")
