"""Logic pattern recognition service."""

import re
from typing import Dict, Any, List


PATTERNS = {
    "Iterator Pattern": {
        "indicators": [r'\b(iter|__iter__|__next__|next\(|Iterator|Iterable)\b'],
        "description": "Provides sequential access to elements without exposing underlying structure",
    },
    "Singleton Pattern": {
        "indicators": [r'_instance\s*=|getInstance|__new__\s*\(.*cls'],
        "description": "Ensures a class has only one instance with global access point",
    },
    "Factory Pattern": {
        "indicators": [r'(create_|factory|make_|build_)\w+|Factory\w*'],
        "description": "Creates objects without specifying exact class to instantiate",
    },
    "Observer Pattern": {
        "indicators": [r'(observer|listener|subscribe|notify|publish|on_event|addEventListener)'],
        "description": "Defines one-to-many dependency between objects for event handling",
    },
    "Strategy Pattern": {
        "indicators": [r'(strategy|set_strategy|execute|algorithm)\b.*=\s*\w+\('],
        "description": "Defines family of interchangeable algorithms",
    },
    "Decorator Pattern": {
        "indicators": [r'(@\w+|def\s+\w+\(func\)|wrapper|wraps|decorator)'],
        "description": "Dynamically adds behavior to objects without modifying their class",
    },
    "Recursion": {
        "indicators": [r'def\s+(\w+).*\n(?:.*\n)*?.*\1\s*\('],
        "description": "Function calls itself to solve sub-problems",
    },
    "Two Pointer": {
        "indicators": [r'(left|right|lo|hi|start|end)\s*=.*\n.*while\s+(left|lo|start)\s*<\s*(right|hi|end)'],
        "description": "Uses two pointers to traverse data structure from different positions",
    },
    "Sliding Window": {
        "indicators": [r'(window|slide|window_size|window_start|window_end)\b'],
        "description": "Maintains a window of elements for efficient subarray/substring processing",
    },
    "Divide and Conquer": {
        "indicators": [r'(mid\s*=.*//\s*2|mid\s*=.*>>\s*1).*\n(?:.*\n)*?.*(left|right)\s*=\s*\w+\('],
        "description": "Breaks problem into smaller subproblems, solves recursively, combines results",
    },
    "Backtracking": {
        "indicators": [r'(backtrack|backtracking)\b|def\s+\w+.*\n(?:.*\n)*?.*\.append\(.*\n.*\w+\(.*\n.*\.pop\('],
        "description": "Explores all possibilities by building candidates and abandoning invalid ones",
    },
    "Memoization": {
        "indicators": [r'(memo|cache|@lru_cache|@cache|dp\[)\b'],
        "description": "Caches computed results to avoid redundant calculations",
    },
    "Guard Clause": {
        "indicators": [r'^\s*(if\s+.*:\s*\n\s*(return|raise|throw|continue|break))'],
        "description": "Early return pattern that simplifies nested conditionals",
    },
    "Builder Pattern": {
        "indicators": [r'(\.set_\w+\(|\.with_\w+\(|\.build\(\)|Builder)'],
        "description": "Constructs complex objects step by step with fluent interface",
    },
}


def recognize_patterns(code: str, ast_data: Dict[str, Any], language: str = "python") -> List[Dict[str, Any]]:
    """
    Recognize logic and design patterns in the code.
    Returns list of detected patterns with confidence.
    """
    results = []

    for pattern_name, pattern_info in PATTERNS.items():
        confidence = 0.0
        matches = 0

        for indicator in pattern_info["indicators"]:
            try:
                found = re.findall(indicator, code, re.MULTILINE | re.IGNORECASE)
                if found:
                    matches += len(found)
            except re.error:
                continue

        if matches > 0:
            # Base confidence from matches
            confidence = min(95, 40 + matches * 15)

            # Bonus for structural alignment
            if pattern_name == "Recursion" and ast_data.get("has_recursion"):
                confidence = min(95, confidence + 15)
            elif pattern_name == "Memoization" and ast_data.get("has_recursion"):
                confidence = min(95, confidence + 10)

            results.append({
                "name": pattern_name,
                "confidence": round(confidence, 1),
                "description": pattern_info["description"],
            })

    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:6]
