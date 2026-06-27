"""
init_project_structure.py
===========================
Initializes the folder/file structure for the
Voice-Based Concept Understanding Analyser project.

Usage:
    python init_project_structure.py [project_root]

If project_root is omitted, it defaults to the current directory.

What it does:
    1. Creates a clean, modular folder layout (src, data, models, tests, etc.)
    2. Creates placeholder/starter files (__init__.py, config.py, .env.example, etc.)
    3. Creates a .gitignore tuned for Python + audio/ML projects
    4. Creates a starter README.md
    5. Skips anything that already exists (safe to re-run)
"""

import os
import sys

# ---------------------------------------------------------
# Project layout definition
# ---------------------------------------------------------
FOLDERS = [
    "src",
    "src/audio",            # recording, audio preprocessing
    "src/speech_to_text",   # Whisper / Vosk wrappers
    "src/nlp",              # concept extraction, keyword matching
    "src/analysis",         # understanding-score logic
    "src/database",         # models, connection, migrations
    "src/api",              # Flask/FastAPI routes
    "src/reports",          # report/feedback generation
    "src/utils",            # shared helpers (logging, config)
    "data/raw_audio",
    "data/transcripts",
    "data/concepts",        # concept/keyword definition files
    "models",               # downloaded/fine-tuned ML models
    "notebooks",            # exploration / prototyping
    "tests",
    "logs",
    "config",
    "docs",
]

# Files to create, mapped to their starter content (empty string = blank file)
FILES = {
    # Package init files so folders are importable modules
    "src/__init__.py": "",
    "src/audio/__init__.py": "",
    "src/speech_to_text/__init__.py": "",
    "src/nlp/__init__.py": "",
    "src/analysis/__init__.py": "",
    "src/database/__init__.py": "",
    "src/api/__init__.py": "",
    "src/reports/__init__.py": "",
    "src/utils/__init__.py": "",
    "tests/__init__.py": "",

    # Entry point
    "src/main.py": (
        '"""\n'
        "Entry point for the Voice-Based Concept Understanding Analyser.\n"
        '"""\n\n'
        "from src.utils.config import load_config\n"
        "from src.utils.logger import get_logger\n\n"
        'logger = get_logger(__name__)\n\n\n'
        "def main():\n"
        "    config = load_config()\n"
        '    logger.info("Application started.")\n'
        "    # TODO: wire up audio capture -> STT -> NLP analysis pipeline\n\n\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    ),

    # Config loader
    "src/utils/config.py": (
        '"""\n'
        "Loads environment variables and app configuration.\n"
        '"""\n\n'
        "import os\n"
        "from dotenv import load_dotenv\n\n\n"
        "def load_config():\n"
        '    """Load .env variables and return a config dict."""\n'
        "    load_dotenv()\n"
        "    return {\n"
        '        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///data/app.db"),\n'
        '        "WHISPER_MODEL": os.getenv("WHISPER_MODEL", "base"),\n'
        '        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),\n'
        "    }\n"
    ),

    # Logger utility
    "src/utils/logger.py": (
        '"""\n'
        "Centralized logger configuration.\n"
        '"""\n\n'
        "import logging\n"
        "import os\n\n"
        'LOG_DIR = "logs"\n'
        "os.makedirs(LOG_DIR, exist_ok=True)\n\n\n"
        "def get_logger(name: str) -> logging.Logger:\n"
        "    logger = logging.getLogger(name)\n"
        "    if not logger.handlers:\n"
        "        logger.setLevel(logging.INFO)\n"
        "        formatter = logging.Formatter(\n"
        '            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"\n'
        "        )\n\n"
        "        file_handler = logging.FileHandler(os.path.join(LOG_DIR, \"app.log\"))\n"
        "        file_handler.setFormatter(formatter)\n\n"
        "        console_handler = logging.StreamHandler()\n"
        "        console_handler.setFormatter(formatter)\n\n"
        "        logger.addHandler(file_handler)\n"
        "        logger.addHandler(console_handler)\n"
        "    return logger\n"
    ),

    # Placeholder module files (so the structure is immediately runnable/importable)
    "src/audio/recorder.py": (
        '"""Handles microphone input and audio file capture."""\n\n\n'
        "def record_audio(duration_seconds: int = 10, output_path: str = None):\n"
        '    """TODO: implement audio recording (e.g., using sounddevice / pyaudio)."""\n'
        "    raise NotImplementedError\n"
    ),
    "src/speech_to_text/transcriber.py": (
        '"""Converts audio recordings into text using Whisper or Vosk."""\n\n\n'
        "def transcribe_audio(audio_path: str) -> str:\n"
        '    """TODO: implement speech-to-text transcription."""\n'
        "    raise NotImplementedError\n"
    ),
    "src/nlp/concept_matcher.py": (
        '"""Extracts and matches concepts/keywords from transcribed text."""\n\n\n'
        "def match_concepts(transcript: str, concept_keywords: list) -> dict:\n"
        '    """TODO: implement keyword/embedding-based concept matching."""\n'
        "    raise NotImplementedError\n"
    ),
    "src/analysis/scorer.py": (
        '"""Computes understanding scores from concept analysis results."""\n\n\n'
        "def compute_understanding_score(matched: list, missing: list) -> float:\n"
        '    """TODO: implement scoring logic."""\n'
        "    raise NotImplementedError\n"
    ),
    "src/database/models.py": (
        '"""SQLAlchemy ORM models for the analyser database."""\n\n'
        "from sqlalchemy import Column, Integer, String, Float, DateTime\n"
        "from sqlalchemy.orm import declarative_base\n\n"
        "Base = declarative_base()\n\n\n"
        "class Student(Base):\n"
        '    __tablename__ = "students"\n'
        "    student_id = Column(Integer, primary_key=True)\n"
        "    name = Column(String, nullable=False)\n"
        "    email = Column(String, unique=True, nullable=False)\n"
    ),
    "src/api/routes.py": (
        '"""API route definitions (FastAPI)."""\n\n'
        "from fastapi import APIRouter\n\n"
        "router = APIRouter()\n\n\n"
        '@router.get("/health")\n'
        "def health_check():\n"
        '    return {"status": "ok"}\n'
    ),
    "src/reports/report_generator.py": (
        '"""Generates student performance reports from analysis data."""\n\n\n'
        "def generate_report(student_id: int, session_id: int) -> dict:\n"
        '    """TODO: implement report generation."""\n'
        "    raise NotImplementedError\n"
    ),

    # Tests
    "tests/test_sample.py": (
        '"""Sample test to verify the test suite runs."""\n\n\n'
        "def test_sample():\n"
        "    assert 1 + 1 == 2\n"
    ),

    # Config / env
    "config/settings.yaml": (
        "app_name: Voice-Based Concept Understanding Analyser\n"
        "version: 0.1.0\n"
        "whisper_model: base\n"
        "log_level: INFO\n"
    ),
    ".env.example": (
        "DATABASE_URL=sqlite:///data/app.db\n"
        "WHISPER_MODEL=base\n"
        "LOG_LEVEL=INFO\n"
    ),

    # Git / docs
    ".gitignore": (
        "# Byte-compiled / cache\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*.so\n\n"
        "# Virtual environment\n"
        "venv/\n"
        ".venv/\n\n"
        "# Environment variables\n"
        ".env\n\n"
        "# Data & models (often large / sensitive)\n"
        "data/raw_audio/*\n"
        "data/transcripts/*\n"
        "models/*\n"
        "!data/raw_audio/.gitkeep\n"
        "!data/transcripts/.gitkeep\n"
        "!models/.gitkeep\n\n"
        "# Logs\n"
        "logs/*.log\n\n"
        "# IDE\n"
        ".vscode/\n"
        ".idea/\n\n"
        "# OS\n"
        ".DS_Store\n"
    ),
    "README.md": (
        "# Voice-Based Concept Understanding Analyser\n\n"
        "Analyses spoken responses to assess a learner's conceptual understanding.\n\n"
        "## Project Structure\n\n"
        "```\n"
        "src/                 Application source code\n"
        "  audio/              Audio capture & preprocessing\n"
        "  speech_to_text/     Speech-to-text transcription\n"
        "  nlp/                Concept/keyword extraction & matching\n"
        "  analysis/           Understanding scoring logic\n"
        "  database/           ORM models & DB access\n"
        "  api/                REST API routes\n"
        "  reports/            Report & feedback generation\n"
        "  utils/              Shared utilities (config, logging)\n"
        "data/                 Raw audio, transcripts, concept definitions\n"
        "models/               ML models (Whisper, embeddings, etc.)\n"
        "notebooks/            Prototyping / exploration notebooks\n"
        "tests/                Unit & integration tests\n"
        "config/               YAML configuration files\n"
        "logs/                 Application logs\n"
        "docs/                 Documentation\n"
        "```\n\n"
        "## Setup\n\n"
        "```bash\n"
        "python setup_environment.py\n"
        "source venv/bin/activate\n"
        "cp .env.example .env\n"
        "python src/main.py\n"
        "```\n"
    ),
}

# Empty data/model directories need a placeholder so git tracks them
GITKEEP_DIRS = ["data/raw_audio", "data/transcripts", "models", "logs"]


def create_folders(root: str):
    print("Creating folders...")
    for folder in FOLDERS:
        path = os.path.join(root, folder)
        os.makedirs(path, exist_ok=True)
        print(f"  [OK] {path}/")
    print()


def create_files(root: str):
    print("Creating files...")
    for rel_path, content in FILES.items():
        path = os.path.join(root, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            print(f"  [SKIP] {path} (already exists)")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] {path}")
    print()


def create_gitkeep_files(root: str):
    print("Adding .gitkeep placeholders for empty data folders...")
    for folder in GITKEEP_DIRS:
        path = os.path.join(root, folder, ".gitkeep")
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()
            print(f"  [OK] {path}")
    print()


def print_tree(root: str):
    print("=" * 60)
    print("PROJECT STRUCTURE")
    print("=" * 60)
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden/venv folders from the printed tree for readability
        dirnames[:] = [d for d in dirnames if d not in (".git", "venv", ".venv", "__pycache__")]
        depth = dirpath.replace(root, "").count(os.sep)
        indent = "  " * depth
        print(f"{indent}{os.path.basename(dirpath) or root}/")
        for f in sorted(filenames):
            print(f"{indent}  {f}")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)
    print(f"Initializing project structure at: {root}\n")

    create_folders(root)
    create_files(root)
    create_gitkeep_files(root)
    print_tree(root)

    print("\nDone. Next steps:")
    print("  1. python setup_environment.py")
    print("  2. cp .env.example .env   (then fill in real values)")
    print("  3. python src/main.py")


if __name__ == "__main__":
    main()