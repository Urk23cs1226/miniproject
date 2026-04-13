"""Code quality scoring service - readability, efficiency, maintainability."""

import re
import math
from typing import Dict, Any


def compute_quality_scores(code: str, ast_data: Dict[str, Any], language: str = "python") -> Dict[str, float]:
    """
    Compute code quality scores.
    Returns readability, efficiency, maintainability, and overall score.
    """
    readability = _compute_readability(code, ast_data, language)
    efficiency = _compute_efficiency(code, ast_data, language)
    maintainability = _compute_maintainability(code, ast_data, language)

    # Weighted overall
    overall = readability * 0.35 + efficiency * 0.35 + maintainability * 0.30

    return {
        "readability": round(readability, 1),
        "efficiency": round(efficiency, 1),
        "maintainability": round(maintainability, 1),
        "overall": round(overall, 1),
    }


def _compute_readability(code: str, ast_data: Dict, language: str) -> float:
    """
    Score readability based on:
    - Naming conventions
    - Comment density
    - Line length
    - Function length
    - Consistent indentation
    """
    score = 100.0
    lines = code.split('\n')
    non_empty = [l for l in lines if l.strip()]

    if not non_empty:
        return 50.0

    # 1. Average line length (penalty for long lines)
    avg_len = sum(len(l) for l in non_empty) / len(non_empty)
    long_lines = sum(1 for l in non_empty if len(l) > 80)
    if avg_len > 60:
        score -= min(15, (avg_len - 60) * 0.5)
    if long_lines > 0:
        score -= min(10, long_lines * 2)

    # 2. Comment density (reward for comments)
    comment_chars = '#' if language == 'python' else '//'
    comments = sum(1 for l in lines if l.strip().startswith(comment_chars))
    comment_ratio = comments / len(non_empty) if non_empty else 0
    if comment_ratio < 0.05 and len(non_empty) > 5:
        score -= 10  # Too few comments
    elif comment_ratio > 0.3:
        score -= 5   # Too many comments

    # 3. Naming conventions
    functions = ast_data.get("functions", [])
    for func in functions:
        name = func["name"]
        if language == "python":
            if not re.match(r'^[a-z_][a-z0-9_]*$', name) and name != '__init__' and not name.startswith('_'):
                score -= 3
        elif language == "java":
            if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                score -= 3

    # 4. Function documentation (Python docstrings)
    if language == "python":
        for func in functions:
            func_line = func.get("line", 0)
            if func_line > 0 and func_line < len(lines):
                # Check if next non-empty line is a docstring
                has_docstring = False
                for i in range(func_line, min(func_line + 3, len(lines))):
                    if '"""' in lines[i] or "'''" in lines[i]:
                        has_docstring = True
                        break
                if not has_docstring:
                    score -= 3

    # 5. Blank line usage (readability aid)
    consecutive_code = 0
    max_consecutive = 0
    for line in lines:
        if line.strip():
            consecutive_code += 1
            max_consecutive = max(max_consecutive, consecutive_code)
        else:
            consecutive_code = 0

    if max_consecutive > 20:
        score -= min(8, (max_consecutive - 20) * 0.5)

    return max(10, min(100, score))


def _compute_efficiency(code: str, ast_data: Dict, language: str) -> float:
    """
    Score efficiency based on:
    - Algorithm complexity indicators
    - Redundant operations
    - Data structure choices
    - Loop efficiency
    """
    score = 100.0
    code_lower = code.lower()

    # 1. Loop nesting penalty
    loops = ast_data.get("loops", [])
    max_depth = ast_data.get("max_depth", 0)
    if max_depth > 3:
        score -= min(25, (max_depth - 3) * 8)
    elif max_depth == 3:
        score -= 10

    # 2. Inefficient patterns
    if 'range(len(' in code:
        score -= 5
    if re.search(r'in\s+\[', code) and language == "python":
        score -= 8  # List for membership test
    if re.search(r'\+=\s*["\']', code) and any(l["type"] == "for" for l in loops):
        score -= 10  # String concat in loop

    # 3. Recursion without memoization
    if ast_data.get("has_recursion") and not any(kw in code_lower for kw in ["memo", "cache", "dp"]):
        score -= 8

    # 4. Redundant variable creation
    assignments = re.findall(r'\b\w+\s*=\s*', code)
    if len(assignments) > len(code.split('\n')) * 0.7:
        score -= 5

    # 5. Efficient data structures bonus
    efficient_structures = ['set(', 'frozenset(', 'defaultdict(', 'Counter(', 'deque(']
    for struct in efficient_structures:
        if struct in code:
            score += 3

    return max(10, min(100, score))


def _compute_maintainability(code: str, ast_data: Dict, language: str) -> float:
    """
    Score maintainability based on:
    - Function size and count
    - Cyclomatic complexity
    - Code modularity
    - Error handling
    """
    score = 100.0
    lines = code.split('\n')
    non_empty = [l for l in lines if l.strip()]
    code_lower = code.lower()

    # 1. Function size
    functions = ast_data.get("functions", [])
    for func in functions:
        body = func.get("body_lines", 0)
        if body > 30:
            score -= min(10, (body - 30) * 0.3)

    # 2. Number of functions (modularity)
    if len(non_empty) > 20 and not functions:
        score -= 15  # No functions in substantial code

    # 3. Cyclomatic complexity proxy
    conditionals = len(ast_data.get("conditionals", []))
    loops = len(ast_data.get("loops", []))
    complexity = conditionals + loops + 1
    if complexity > 10:
        score -= min(20, (complexity - 10) * 2)

    # 4. Error handling
    has_error_handling = any(kw in code_lower for kw in ['try', 'except', 'catch', 'throw', 'raise'])
    if not has_error_handling and len(non_empty) > 15:
        score -= 8

    # 5. Class usage for complex code
    classes = ast_data.get("classes", [])
    if len(functions) > 5 and not classes:
        score -= 5  # Many functions without class organization

    # 6. Magic numbers
    magic_count = 0
    for line in non_empty:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        nums = re.findall(r'(?<!=)\b(\d+)\b', stripped)
        for n in nums:
            if int(n) not in (0, 1, 2, -1, 10, 100):
                magic_count += 1
    if magic_count > 5:
        score -= min(10, magic_count)

    # 7. DRY principle (duplicate code indicator)
    normalized_lines = [re.sub(r'\s+', ' ', l.strip()) for l in non_empty if len(l.strip()) > 10]
    unique_lines = set(normalized_lines)
    if normalized_lines and len(unique_lines) / len(normalized_lines) < 0.7:
        score -= 10

    return max(10, min(100, score))
