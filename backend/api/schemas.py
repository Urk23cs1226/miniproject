"""Pydantic request/response schemas for all API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ── Request Schemas ──────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of the code to generate")
    language: str = Field(default="python", description="Target language: python, java, cpp")
    max_length: int = Field(default=256, description="Maximum token length for generation")


class AnalyzeRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(default="python", description="Language of the source code")


class AutocompleteRequest(BaseModel):
    code: str = Field(..., description="Partial code to complete")
    language: str = Field(default="python", description="Language of the source code")
    cursor_position: int = Field(default=-1, description="Cursor position in the code")


class SimilarityRequest(BaseModel):
    code1: str = Field(..., description="First code snippet")
    code2: str = Field(..., description="Second code snippet")
    language: str = Field(default="python", description="Language of the source code")


# ── Response Schemas ─────────────────────────────────────────────────────────

class BugInfo(BaseModel):
    type: str
    description: str
    line: Optional[int] = None
    probability: float = Field(..., ge=0, le=100)
    severity: str = "medium"


class OptimizationSuggestion(BaseModel):
    description: str
    improvement_percentage: float = Field(..., ge=0, le=100)
    category: str = "general"


class DuplicateBlock(BaseModel):
    start_line: int
    end_line: int
    duplicate_of_start: int
    duplicate_of_end: int
    similarity: float


class PatternInfo(BaseModel):
    name: str
    confidence: float = Field(..., ge=0, le=100)
    description: str


class GenerateResponse(BaseModel):
    generated_code: str
    language: str
    prompt: str
    model_type: str = "LSTM"
    tokens_generated: int = 0


class AnalysisResponse(BaseModel):
    # Overall quality
    code_quality_score: float = Field(..., ge=0, le=100)
    readability_score: float = Field(..., ge=0, le=100)
    efficiency_score: float = Field(..., ge=0, le=100)
    maintainability_score: float = Field(..., ge=0, le=100)

    # Algorithm detection
    algorithm_detected: str = "Unknown"
    algorithm_confidence: float = Field(default=0, ge=0, le=100)
    algorithm_details: str = ""

    # Complexity
    time_complexity: str = "Unknown"
    space_complexity: str = "Unknown"
    complexity_confidence: float = Field(default=0, ge=0, le=100)

    # Bug detection
    bug_risk_level: float = Field(default=0, ge=0, le=100)
    bugs: List[BugInfo] = []

    # Optimization
    optimization_score: float = Field(default=0, ge=0, le=100)
    optimization_suggestions: List[OptimizationSuggestion] = []

    # Duplicates
    duplicate_blocks: List[DuplicateBlock] = []
    has_duplicates: bool = False

    # Patterns
    patterns: List[PatternInfo] = []

    # Metadata
    language: str = "python"
    lines_of_code: int = 0
    num_functions: int = 0
    num_classes: int = 0


class AutocompleteResponse(BaseModel):
    suggestions: List[str]
    language: str


class SimilarityResponse(BaseModel):
    similarity_percentage: float = Field(..., ge=0, le=100)
    token_similarity: float = Field(..., ge=0, le=100)
    structural_similarity: float = Field(..., ge=0, le=100)
    details: str = ""


class LanguagesResponse(BaseModel):
    languages: List[str]
    file_extensions: Dict[str, str]
