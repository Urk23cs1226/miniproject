"""Master code analysis orchestrator - runs all analysis services."""

from typing import Dict, Any
from ..utils.ast_parser import ASTParser, count_lines
from ..utils.language_support import detect_language
from .algorithm_detector import detect_algorithm
from .complexity_predictor import predict_complexity
from .bug_detector import detect_bugs
from .similarity_checker import check_similarity
from .optimizer import suggest_optimizations, calculate_optimization_score
from .duplicate_detector import detect_duplicates
from .pattern_recognizer import recognize_patterns
from .quality_scorer import compute_quality_scores


def analyze_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Run the full analysis pipeline on the given code.
    Returns comprehensive analysis results.
    """
    # Auto-detect language if needed
    if not language or language == "auto":
        language = detect_language(code)

    # Parse AST
    ast_data = ASTParser.parse(code, language)

    # Line metrics
    line_metrics = count_lines(code)

    # Run all analysis services
    # 1. Algorithm detection
    algorithms = detect_algorithm(code, ast_data, language)
    top_algorithm = algorithms[0] if algorithms else {"name": "General Purpose", "confidence": 50.0, "description": "No specific algorithm pattern detected"}

    # 2. Complexity prediction
    complexity = predict_complexity(code, ast_data, language)

    # 3. Bug detection
    bugs = detect_bugs(code, ast_data, language)
    bug_risk = _calculate_bug_risk(bugs)

    # 4. Optimization suggestions
    optimizations = suggest_optimizations(code, ast_data, language)
    optimization_score = calculate_optimization_score(optimizations)

    # 5. Duplicate detection
    duplicates = detect_duplicates(code, language)

    # 6. Pattern recognition
    patterns = recognize_patterns(code, ast_data, language)

    # 7. Quality scores
    quality = compute_quality_scores(code, ast_data, language)

    # Compile final response
    return {
        # Overall quality
        "code_quality_score": quality["overall"],
        "readability_score": quality["readability"],
        "efficiency_score": quality["efficiency"],
        "maintainability_score": quality["maintainability"],

        # Algorithm detection
        "algorithm_detected": top_algorithm["name"],
        "algorithm_confidence": top_algorithm["confidence"],
        "algorithm_details": top_algorithm.get("description", ""),
        "all_algorithms": algorithms,

        # Complexity
        "time_complexity": complexity["time_complexity"],
        "space_complexity": complexity["space_complexity"],
        "complexity_confidence": complexity["time_confidence"],
        "complexity_details": complexity["time_explanation"],

        # Bug detection
        "bug_risk_level": bug_risk,
        "bugs": [
            {
                "type": b["type"],
                "description": b["description"],
                "line": b.get("line", 0),
                "probability": b["probability"],
                "severity": b["severity"],
            }
            for b in bugs
        ],

        # Optimization
        "optimization_score": optimization_score,
        "optimization_suggestions": [
            {
                "description": s["description"],
                "improvement_percentage": s["improvement_percentage"],
                "category": s["category"],
            }
            for s in optimizations
        ],

        # Duplicates
        "duplicate_blocks": [
            {
                "start_line": d["start_line"],
                "end_line": d["end_line"],
                "duplicate_of_start": d["duplicate_of_start"],
                "duplicate_of_end": d["duplicate_of_end"],
                "similarity": d["similarity"],
            }
            for d in duplicates
        ],
        "has_duplicates": len(duplicates) > 0,

        # Patterns
        "patterns": [
            {
                "name": p["name"],
                "confidence": p["confidence"],
                "description": p["description"],
            }
            for p in patterns
        ],

        # Metadata
        "language": language,
        "lines_of_code": line_metrics["code"],
        "num_functions": len(ast_data.get("functions", [])),
        "num_classes": len(ast_data.get("classes", [])),
    }


def _calculate_bug_risk(bugs: list) -> float:
    """Calculate overall bug risk level (0-100)."""
    if not bugs:
        return 5.0  # Small baseline risk

    severity_weights = {"critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}
    total_weight = 0
    weighted_prob = 0

    for bug in bugs:
        weight = severity_weights.get(bug.get("severity", "medium"), 1.0)
        total_weight += weight
        weighted_prob += bug["probability"] * weight

    risk = weighted_prob / total_weight if total_weight > 0 else 0
    # Scale by number of bugs
    risk = min(100, risk * (1 + len(bugs) * 0.1))

    return round(risk, 1)
