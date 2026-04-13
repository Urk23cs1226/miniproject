"""Code optimization suggestion engine."""

import re
from typing import Dict, Any, List


def suggest_optimizations(code: str, ast_data: Dict[str, Any], language: str = "python") -> List[Dict[str, Any]]:
    """
    Analyze code and suggest optimizations.
    Returns list of suggestions with improvement percentage.
    """
    suggestions = []

    if language == "python":
        suggestions.extend(_python_optimizations(code, ast_data))
    elif language == "java":
        suggestions.extend(_java_optimizations(code, ast_data))
    elif language == "cpp":
        suggestions.extend(_cpp_optimizations(code, ast_data))

    suggestions.extend(_common_optimizations(code, ast_data, language))

    return suggestions


def _python_optimizations(code: str, ast_data: Dict) -> List[Dict]:
    suggestions = []
    lines = code.split('\n')

    # List comprehension opportunity
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('for ') and i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            if '.append(' in next_stripped:
                suggestions.append({
                    "description": "Loop with append pattern can be replaced with a list comprehension for better performance and readability.",
                    "improvement_percentage": 25.0,
                    "category": "performance",
                    "line": i + 1,
                })

    # Use enumerate instead of range(len())
    if 'range(len(' in code:
        suggestions.append({
            "description": "Use enumerate() instead of range(len()) for cleaner iteration with index access.",
            "improvement_percentage": 10.0,
            "category": "readability",
        })

    # Use f-strings instead of format/concat
    if '.format(' in code or '% (' in code:
        suggestions.append({
            "description": "Consider using f-strings instead of .format() or % formatting for better readability.",
            "improvement_percentage": 8.0,
            "category": "readability",
        })

    # Use defaultdict or Counter
    if re.search(r'if\s+\w+\s+(not\s+)?in\s+\w+:.*\n.*\[\w+\]\s*=', code, re.MULTILINE):
        suggestions.append({
            "description": "Use collections.defaultdict or Counter instead of manual dictionary initialization checks.",
            "improvement_percentage": 15.0,
            "category": "readability",
        })

    # Use set for membership testing
    if re.search(r'if\s+\w+\s+in\s+\[', code):
        suggestions.append({
            "description": "Use a set instead of a list for membership testing (O(1) vs O(n) lookup).",
            "improvement_percentage": 30.0,
            "category": "performance",
        })

    # Use generators for large data
    if re.search(r'\blist\s*\(\s*(range|map|filter)\s*\(', code):
        suggestions.append({
            "description": "Use generator expressions instead of wrapping range/map/filter in list() when iterating.",
            "improvement_percentage": 20.0,
            "category": "memory",
        })

    return suggestions


def _java_optimizations(code: str, ast_data: Dict) -> List[Dict]:
    suggestions = []

    # StringBuilder for string concatenation
    if re.search(r'String\s+\w+\s*=.*\+.*\+', code) or re.search(r'\+=\s*"', code):
        suggestions.append({
            "description": "Use StringBuilder instead of string concatenation with + operator for better performance.",
            "improvement_percentage": 35.0,
            "category": "performance",
        })

    # Use enhanced for loop
    if re.search(r'for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\.(length|size)', code):
        suggestions.append({
            "description": "Consider using enhanced for-each loop instead of index-based iteration.",
            "improvement_percentage": 10.0,
            "category": "readability",
        })

    # Use try-with-resources
    if re.search(r'new\s+(FileInputStream|BufferedReader|Scanner)', code) and 'try-with-resources' not in code:
        suggestions.append({
            "description": "Use try-with-resources for automatic resource management.",
            "improvement_percentage": 20.0,
            "category": "reliability",
        })

    return suggestions


def _cpp_optimizations(code: str, ast_data: Dict) -> List[Dict]:
    suggestions = []

    # Use const references
    if re.search(r'void\s+\w+\s*\(\s*(string|vector|map)\s+', code):
        suggestions.append({
            "description": "Pass large objects (string, vector, map) by const reference instead of by value.",
            "improvement_percentage": 30.0,
            "category": "performance",
        })

    # Use reserve for vectors
    if 'push_back' in code and '.reserve(' not in code:
        suggestions.append({
            "description": "Use vector::reserve() before push_back loops to avoid repeated reallocations.",
            "improvement_percentage": 25.0,
            "category": "performance",
        })

    # Use smart pointers
    if 'new ' in code and 'unique_ptr' not in code and 'shared_ptr' not in code:
        suggestions.append({
            "description": "Use smart pointers (unique_ptr/shared_ptr) instead of raw pointers for automatic memory management.",
            "improvement_percentage": 20.0,
            "category": "reliability",
        })

    return suggestions


def _common_optimizations(code: str, ast_data: Dict, language: str) -> List[Dict]:
    """Language-agnostic optimization suggestions."""
    suggestions = []
    lines = code.split('\n')

    # Long function detection
    for func in ast_data.get("functions", []):
        body_lines = func.get("body_lines", 0)
        if body_lines > 50:
            suggestions.append({
                "description": f"Function '{func['name']}' is {body_lines} lines long. Consider breaking it into smaller functions.",
                "improvement_percentage": 20.0,
                "category": "maintainability",
            })

    # Deep nesting
    max_depth = ast_data.get("max_depth", 0)
    if max_depth > 4:
        suggestions.append({
            "description": f"Code has deep nesting (depth={max_depth}). Consider early returns or extracting helper functions.",
            "improvement_percentage": 18.0,
            "category": "readability",
        })

    # Duplicate condition checks
    conditions = []
    for i, line in enumerate(lines):
        if re.search(r'if\s+|elif\s+|else\s+if', line.strip()):
            cond = re.sub(r'\s+', ' ', line.strip())
            if cond in conditions:
                suggestions.append({
                    "description": f"Duplicate condition check at line {i+1}. Consider refactoring.",
                    "improvement_percentage": 12.0,
                    "category": "maintainability",
                })
            conditions.append(cond)

    # Too many parameters
    for func in ast_data.get("functions", []):
        if len(func.get("args", [])) > 5:
            suggestions.append({
                "description": f"Function '{func['name']}' has {len(func['args'])} parameters. Consider using a configuration object.",
                "improvement_percentage": 15.0,
                "category": "maintainability",
            })

    # No error handling
    error_keywords = ['try', 'except', 'catch', 'throw', 'raise']
    has_error_handling = any(kw in code.lower() for kw in error_keywords)
    if not has_error_handling and len(lines) > 10:
        suggestions.append({
            "description": "No error handling detected. Consider adding try-except/try-catch blocks for robustness.",
            "improvement_percentage": 15.0,
            "category": "reliability",
        })

    return suggestions


def calculate_optimization_score(suggestions: List[Dict]) -> float:
    """Calculate overall optimization improvement score."""
    if not suggestions:
        return 95.0  # Already well-optimized

    total_possible = sum(s["improvement_percentage"] for s in suggestions)
    # Score is inverse: fewer suggestions = higher score
    score = max(0, 100 - total_possible * 0.5)
    return round(min(score, 100), 1)
