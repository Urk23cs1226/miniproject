"""Application configuration settings."""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "pretrained")

# Supported languages
SUPPORTED_LANGUAGES = ["python", "java", "cpp"]
FILE_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
}

# Model configuration
MODEL_CONFIG = {
    "vocab_size": 5000,
    "embed_dim": 128,
    "hidden_dim": 256,
    "num_layers": 2,
    "dropout": 0.3,
    "max_seq_length": 512,
}

# Analysis thresholds
ANALYSIS_CONFIG = {
    "min_confidence": 10.0,
    "similarity_threshold": 0.7,
    "bug_probability_threshold": 0.3,
    "max_file_size_kb": 500,
}
