"""Time and space complexity prediction service."""

import re
from typing import Dict, Any, Tuple


COMPLEXITY_LEVELS = [
    ("O(1)", "Constant"),
    ("O(log n)", "Logarithmic"),
    ("O(n)", "Linear"),
    ("O(n log n)", "Linearithmic"),
    ("O(n²)", "Quadratic"),
    ("O(n³)", "Cubic"),
    ("O(2ⁿ)", "Exponential"),
    ("O(n!)", "Factorial"),
]


def predict_complexity(code: str, ast_data: Dict[str, Any], language: str = "python") -> Dict[str, Any]:
    """
    Predict time and space complexity of the code.
    Returns complexity notation, confidence, and explanation.
    """
    loops = ast_data.get("loops", [])
    has_recursion = ast_data.get("has_recursion", False)
    functions = ast_data.get("functions", [])
    max_depth = ast_data.get("max_depth", 0)
    code_lower = code.lower()

    # Analyze loop nesting
    loop_depth = _analyze_loop_nesting(code, language)

    # Detect special patterns
    has_binary_search = _detect_binary_pattern(code_lower)
    has_sorting = any(kw in code_lower for kw in ["sort(", ".sort(", "sorted(", "arrays.sort", "collections.sort"])
    has_heap = any(kw in code_lower for kw in ["heapq", "heappush", "priorityqueue", "priority_queue"])
    has_divide_conquer = has_recursion and ("mid" in code_lower or "// 2" in code_lower or "/ 2" in code_lower)
    has_memo = any(kw in code_lower for kw in ["memo", "cache", "dp[", "lru_cache"])
    has_two_recursive_calls = _count_recursive_calls(code, ast_data) >= 2

    # Determine time complexity
    time_complexity, time_confidence, time_explanation = _determine_time_complexity(
        loop_depth, has_recursion, has_binary_search, has_sorting,
        has_divide_conquer, has_memo, has_two_recursive_calls, len(loops)
    )

    # Determine space complexity
    space_complexity, space_confidence, space_explanation = _determine_space_complexity(
        code_lower, ast_data, has_recursion, has_memo, loop_depth
    )

    return {
        "time_complexity": time_complexity,
        "time_confidence": round(time_confidence, 1),
        "time_explanation": time_explanation,
        "space_complexity": space_complexity,
        "space_confidence": round(space_confidence, 1),
        "space_explanation": space_explanation,
        "loop_depth": loop_depth,
        "has_recursion": has_recursion,
    }


def _analyze_loop_nesting(code: str, language: str) -> int:
    """Analyze maximum loop nesting depth."""
    lines = code.split('\n')
    max_nesting = 0
    current_nesting = 0

    if language == "python":
        indent_stack = [0]
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            indent = len(line) - len(stripped)

            while indent_stack and indent <= indent_stack[-1] and len(indent_stack) > 1:
                if indent < indent_stack[-1]:
                    indent_stack.pop()
                    current_nesting = max(0, current_nesting - 1)
                else:
                    break

            if re.match(r'(for|while)\s', stripped):
                current_nesting += 1
                indent_stack.append(indent + 4)
                max_nesting = max(max_nesting, current_nesting)
    else:
        for line in lines:
            stripped = line.strip()
            if re.search(r'\b(for|while)\s*\(', stripped):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            if '}' in stripped:
                current_nesting = max(0, current_nesting - stripped.count('}'))

    return max_nesting


def _detect_binary_pattern(code_lower: str) -> bool:
    """Detect binary search pattern."""
    has_mid = "mid" in code_lower
    has_bounds = ("low" in code_lower and "high" in code_lower) or \
                 ("left" in code_lower and "right" in code_lower)
    has_halving = "// 2" in code_lower or "/ 2" in code_lower or ">> 1" in code_lower
    return has_mid and has_bounds and has_halving


def _count_recursive_calls(code: str, ast_data: Dict) -> int:
    """Count number of recursive calls in functions."""
    if not ast_data.get("has_recursion"):
        return 0

    functions = ast_data.get("functions", [])
    calls = ast_data.get("calls", [])

    count = 0
    func_names = {f["name"] for f in functions}
    for call in calls:
        if call["name"] in func_names:
            count += 1
    return count


def _determine_time_complexity(
    loop_depth, has_recursion, has_binary_search, has_sorting,
    has_divide_conquer, has_memo, has_two_recursive_calls, num_loops
) -> Tuple[str, float, str]:
    """Determine time complexity based on analysis."""

    if has_binary_search:
        return "O(log n)", 88.0, "Binary search pattern detected: halves search space each iteration"

    if has_sorting:
        return "O(n log n)", 85.0, "Uses built-in sorting which is typically O(n log n)"

    if has_divide_conquer and has_recursion:
        if has_two_recursive_calls:
            return "O(n log n)", 78.0, "Divide and conquer with two recursive calls (likely merge sort pattern)"
        return "O(n log n)", 72.0, "Divide and conquer recursive pattern detected"

    if has_two_recursive_calls and not has_memo:
        return "O(2ⁿ)", 75.0, "Multiple recursive calls without memoization suggests exponential time"

    if has_two_recursive_calls and has_memo:
        return "O(n)", 70.0, "Recursive with memoization reduces to linear/polynomial time"

    if loop_depth >= 3:
        return "O(n³)", 82.0, f"Triple nested loops detected (depth={loop_depth})"

    if loop_depth == 2:
        return "O(n²)", 85.0, "Double nested loops detected"

    if loop_depth == 1:
        return "O(n)", 88.0, "Single loop iterating through input"

    if has_recursion and not has_memo:
        return "O(n)", 65.0, "Simple recursion without branching"

    if num_loops == 0 and not has_recursion:
        return "O(1)", 90.0, "No loops or recursion; constant time operations"

    return "O(n)", 50.0, "Default estimation based on code structure"


def _determine_space_complexity(
    code_lower: str, ast_data: Dict, has_recursion: bool, has_memo: bool, loop_depth: int
) -> Tuple[str, float, str]:
    """Determine space complexity."""

    # Check for matrix/2D array creation
    has_2d_array = bool(re.search(r'\[\s*\[.*\]\s*(for|,)|\[\[|new\s+\w+\[.*\]\[', code_lower))

    if has_2d_array:
        return "O(n²)", 80.0, "2D array/matrix allocation detected"

    if has_memo:
        return "O(n)", 78.0, "Memoization/cache storage grows with input size"

    if has_recursion:
        return "O(n)", 72.0, "Recursive call stack depth proportional to input"

    # Check for list/array creation in loops
    has_growing_collection = bool(re.search(r'append\(|\.add\(|push_back\(|\.push\(', code_lower))
    if has_growing_collection:
        return "O(n)", 75.0, "Collection grows proportionally with input"

    if any(kw in code_lower for kw in ["result = []", "result=[]", "new arraylist", "vector<"]):
        return "O(n)", 70.0, "Output collection allocated for results"

    return "O(1)", 82.0, "Constant extra space used"
