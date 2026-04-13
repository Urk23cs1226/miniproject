"""Algorithm detection service using AST pattern matching."""

import re
from typing import Dict, Any, List, Tuple


# Algorithm signatures - patterns that indicate specific algorithms
ALGORITHM_PATTERNS = {
    "Bubble Sort": {
        "indicators": ["nested_loops", "swap_pattern", "comparison"],
        "keywords": ["swap", "temp", "bubble"],
        "loop_pattern": "nested_for",
        "description": "Comparison-based sorting using adjacent element swaps",
    },
    "Selection Sort": {
        "indicators": ["nested_loops", "min_tracking"],
        "keywords": ["min", "minimum", "selection"],
        "loop_pattern": "nested_for",
        "description": "Finds minimum element and places it at beginning",
    },
    "Insertion Sort": {
        "indicators": ["nested_loops", "shift_pattern"],
        "keywords": ["insert", "key", "insertion"],
        "loop_pattern": "for_while",
        "description": "Builds sorted array one item at a time",
    },
    "Merge Sort": {
        "indicators": ["recursion", "merge_function", "divide"],
        "keywords": ["merge", "mid", "left", "right"],
        "loop_pattern": "recursive",
        "description": "Divide and conquer sorting using merge operations",
    },
    "Quick Sort": {
        "indicators": ["recursion", "pivot", "partition"],
        "keywords": ["pivot", "partition", "quick"],
        "loop_pattern": "recursive",
        "description": "Divide and conquer sorting using pivot partitioning",
    },
    "Binary Search": {
        "indicators": ["loop_or_recursion", "midpoint", "half_elimination"],
        "keywords": ["mid", "low", "high", "left", "right", "binary", "search"],
        "loop_pattern": "single_while",
        "description": "Searches sorted array by repeatedly dividing in half",
    },
    "Linear Search": {
        "indicators": ["single_loop", "comparison"],
        "keywords": ["search", "find", "target"],
        "loop_pattern": "single_for",
        "description": "Sequential search through each element",
    },
    "BFS (Breadth-First Search)": {
        "indicators": ["queue", "visited", "graph_traversal"],
        "keywords": ["queue", "visited", "bfs", "breadth", "deque", "neighbor", "adj"],
        "loop_pattern": "while_with_queue",
        "description": "Graph traversal exploring neighbors level by level",
    },
    "DFS (Depth-First Search)": {
        "indicators": ["stack_or_recursion", "visited", "graph_traversal"],
        "keywords": ["stack", "visited", "dfs", "depth", "neighbor", "adj"],
        "loop_pattern": "recursive_or_stack",
        "description": "Graph traversal exploring as far as possible before backtracking",
    },
    "Dynamic Programming": {
        "indicators": ["memoization", "table", "subproblems"],
        "keywords": ["dp", "memo", "table", "cache", "bottom_up", "top_down", "opt", "tab"],
        "loop_pattern": "nested_loops_with_table",
        "description": "Optimizes by storing results of overlapping subproblems",
    },
    "Dijkstra's Algorithm": {
        "indicators": ["priority_queue", "distances", "graph"],
        "keywords": ["dist", "dijkstra", "priority", "heap", "shortest", "weight"],
        "loop_pattern": "while_with_heap",
        "description": "Finds shortest paths from source in weighted graph",
    },
    "Fibonacci": {
        "indicators": ["recursion_or_loop", "two_previous"],
        "keywords": ["fib", "fibonacci"],
        "loop_pattern": "single_loop_or_recursive",
        "description": "Computes Fibonacci sequence numbers",
    },
    "Linked List Operations": {
        "indicators": ["node_class", "next_pointer"],
        "keywords": ["node", "next", "head", "linked", "list"],
        "loop_pattern": "while_traversal",
        "description": "Operations on linked list data structure",
    },
    "Tree Traversal": {
        "indicators": ["tree_node", "left_right", "recursion"],
        "keywords": ["root", "left", "right", "tree", "inorder", "preorder", "postorder"],
        "loop_pattern": "recursive",
        "description": "Traverses tree structure (inorder/preorder/postorder)",
    },
    "Hash Map Operations": {
        "indicators": ["dictionary", "key_value"],
        "keywords": ["hash", "map", "dict", "table", "key", "bucket"],
        "loop_pattern": "varies",
        "description": "Key-value storage and retrieval operations",
    },
}


def detect_algorithm(code: str, ast_data: Dict[str, Any], language: str = "python") -> List[Dict[str, Any]]:
    """
    Detect algorithms in the given code.
    Returns list of detected algorithms with confidence scores.
    """
    code_lower = code.lower()
    results = []

    for algo_name, pattern in ALGORITHM_PATTERNS.items():
        confidence = 0.0
        matches = []

        # Check keyword matches (up to 40%)
        keyword_hits = 0
        for kw in pattern["keywords"]:
            if kw.lower() in code_lower:
                keyword_hits += 1
                matches.append(f"Keyword '{kw}' found")
        if pattern["keywords"]:
            keyword_score = min(40, (keyword_hits / len(pattern["keywords"])) * 40)
            confidence += keyword_score

        # Check structural indicators (up to 40%)
        indicator_score = _check_indicators(pattern["indicators"], ast_data, code_lower)
        confidence += indicator_score * 0.4
        if indicator_score > 0:
            matches.append(f"Structural pattern match ({indicator_score:.0f}%)")

        # Check loop pattern (up to 20%)
        loop_score = _check_loop_pattern(pattern["loop_pattern"], ast_data)
        confidence += loop_score * 0.2
        if loop_score > 0:
            matches.append(f"Loop pattern match")

        # Minimum threshold
        if confidence >= 15:
            results.append({
                "name": algo_name,
                "confidence": round(min(confidence, 98), 1),
                "description": pattern["description"],
                "matches": matches,
            })

    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:5]  # Top 5


def _check_indicators(indicators: List[str], ast_data: Dict, code_lower: str) -> float:
    """Check structural indicators against AST data."""
    score = 0
    total = len(indicators) * 100

    for indicator in indicators:
        if indicator == "nested_loops":
            if len(ast_data.get("loops", [])) >= 2:
                score += 100
        elif indicator == "recursion":
            if ast_data.get("has_recursion"):
                score += 100
        elif indicator == "single_loop":
            if len(ast_data.get("loops", [])) == 1:
                score += 100
        elif indicator == "loop_or_recursion":
            if ast_data.get("loops") or ast_data.get("has_recursion"):
                score += 100
        elif indicator == "swap_pattern":
            if re.search(r'temp\s*=|, \w+ = \w+, |\.swap\(|swap\(', code_lower):
                score += 100
        elif indicator == "comparison":
            if ">" in code_lower or "<" in code_lower:
                score += 100
        elif indicator == "min_tracking":
            if "min" in code_lower:
                score += 100
        elif indicator == "shift_pattern":
            if re.search(r'\[.*-\s*1\]|\[.*\+\s*1\]', code_lower):
                score += 100
        elif indicator == "merge_function":
            if "merge" in code_lower:
                score += 100
        elif indicator == "divide":
            if "mid" in code_lower or "//" in code_lower or "/ 2" in code_lower:
                score += 100
        elif indicator == "pivot":
            if "pivot" in code_lower:
                score += 100
        elif indicator == "partition":
            if "partition" in code_lower:
                score += 100
        elif indicator == "midpoint":
            if "mid" in code_lower or "(low + high)" in code_lower or "(left + right)" in code_lower:
                score += 100
        elif indicator == "half_elimination":
            if re.search(r'low\s*=\s*mid|left\s*=\s*mid|high\s*=\s*mid|right\s*=\s*mid', code_lower):
                score += 100
        elif indicator == "queue":
            if any(kw in code_lower for kw in ["queue", "deque", "appendleft", "popleft"]):
                score += 100
        elif indicator == "visited":
            if "visited" in code_lower:
                score += 100
        elif indicator == "graph_traversal":
            if any(kw in code_lower for kw in ["adj", "neighbor", "graph", "edge", "vertex"]):
                score += 100
        elif indicator == "stack_or_recursion":
            if "stack" in code_lower or ast_data.get("has_recursion"):
                score += 100
        elif indicator == "memoization":
            if any(kw in code_lower for kw in ["memo", "cache", "dp[", "dp =", "lru_cache"]):
                score += 100
        elif indicator == "table":
            if re.search(r'\[\s*\[.*\]\s*\]|dp\s*=|table\s*=', code_lower):
                score += 100
        elif indicator == "subproblems":
            if ast_data.get("has_recursion") or len(ast_data.get("loops", [])) >= 1:
                score += 80
        elif indicator == "priority_queue":
            if any(kw in code_lower for kw in ["heapq", "heappush", "heappop", "priorityqueue", "priority_queue"]):
                score += 100
        elif indicator == "distances":
            if any(kw in code_lower for kw in ["dist", "distance", "cost", "weight"]):
                score += 100
        elif indicator == "graph":
            if any(kw in code_lower for kw in ["graph", "adj", "edge", "vertex", "node"]):
                score += 100
        elif indicator == "two_previous":
            if re.search(r'\w+\s*-\s*1\].*\w+\s*-\s*2\]|\w+\s*-\s*2\].*\w+\s*-\s*1\]', code_lower):
                score += 100
        elif indicator == "recursion_or_loop":
            if ast_data.get("has_recursion") or ast_data.get("loops"):
                score += 100
        elif indicator == "node_class":
            if "node" in code_lower or "listnode" in code_lower:
                score += 100
        elif indicator == "next_pointer":
            if ".next" in code_lower:
                score += 100
        elif indicator == "tree_node":
            if any(kw in code_lower for kw in ["treenode", "tree_node", "bst", "binary"]):
                score += 100
        elif indicator == "left_right":
            if ".left" in code_lower and ".right" in code_lower:
                score += 100
        elif indicator == "dictionary":
            if any(kw in code_lower for kw in ["dict(", "{}", "hashmap", "map<", "unordered_map"]):
                score += 100
        elif indicator == "key_value":
            if any(kw in code_lower for kw in ["key", "value", "[key]", ".get("]):
                score += 100

    return (score / total * 100) if total > 0 else 0


def _check_loop_pattern(pattern: str, ast_data: Dict) -> float:
    """Check if loop structure matches expected pattern."""
    loops = ast_data.get("loops", [])
    has_recursion = ast_data.get("has_recursion", False)

    if pattern == "nested_for":
        return 100 if len(loops) >= 2 else 0
    elif pattern == "for_while":
        has_for = any(l["type"] == "for" for l in loops)
        has_while = any(l["type"] == "while" for l in loops)
        return 100 if (has_for and has_while) or len(loops) >= 2 else 0
    elif pattern == "recursive":
        return 100 if has_recursion else 0
    elif pattern == "single_while":
        return 100 if any(l["type"] == "while" for l in loops) else 50 if loops else 0
    elif pattern == "single_for":
        return 100 if len(loops) == 1 and loops[0]["type"] == "for" else 0
    elif pattern == "while_with_queue":
        return 100 if any(l["type"] == "while" for l in loops) else 50 if loops else 0
    elif pattern == "recursive_or_stack":
        return 100 if has_recursion else 50 if loops else 0
    elif pattern == "while_with_heap":
        return 100 if any(l["type"] == "while" for l in loops) else 0
    elif pattern == "while_traversal":
        return 100 if any(l["type"] == "while" for l in loops) else 0

    return 50 if loops else 0
