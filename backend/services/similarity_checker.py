"""Code similarity checker using token-based and structural comparison."""

import re
from typing import Dict, Any, List, Tuple
from collections import Counter


def check_similarity(code1: str, code2: str, language: str = "python") -> Dict[str, Any]:
    """
    Compare two code snippets for similarity.
    Returns token similarity, structural similarity, and overall percentage.
    """
    # Tokenize both snippets
    tokens1 = _tokenize(code1, language)
    tokens2 = _tokenize(code2, language)

    # Token-based similarity (Jaccard + sequence)
    token_sim = _token_similarity(tokens1, tokens2)

    # Structural similarity
    struct_sim = _structural_similarity(code1, code2, language)

    # Weighted overall
    overall = token_sim * 0.5 + struct_sim * 0.5

    # Generate details
    details = _generate_details(token_sim, struct_sim, tokens1, tokens2)

    return {
        "similarity_percentage": round(overall, 1),
        "token_similarity": round(token_sim, 1),
        "structural_similarity": round(struct_sim, 1),
        "details": details,
    }


def _tokenize(code: str, language: str) -> List[str]:
    """Tokenize code into meaningful tokens."""
    # Remove comments
    if language == "python":
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    else:
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    # Remove string literals
    code = re.sub(r'"[^"]*"', 'STR', code)
    code = re.sub(r"'[^']*'", 'STR', code)

    # Tokenize
    tokens = re.findall(r'[a-zA-Z_]\w*|[+\-*/=<>!&|%^~]+|[{}\[\]();,.]|\d+', code)

    return tokens


def _token_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Calculate token similarity using Jaccard index and sequence matching."""
    if not tokens1 and not tokens2:
        return 100.0
    if not tokens1 or not tokens2:
        return 0.0

    # Jaccard similarity
    set1, set2 = set(tokens1), set(tokens2)
    jaccard = len(set1 & set2) / len(set1 | set2) * 100

    # Frequency-based similarity
    counter1 = Counter(tokens1)
    counter2 = Counter(tokens2)
    all_tokens = set(counter1.keys()) | set(counter2.keys())
    freq_sim = 0
    total = 0
    for tok in all_tokens:
        c1, c2 = counter1.get(tok, 0), counter2.get(tok, 0)
        freq_sim += min(c1, c2)
        total += max(c1, c2)
    freq_score = (freq_sim / total * 100) if total > 0 else 0

    # LCS ratio (approximate)
    lcs_len = _lcs_length(tokens1[:200], tokens2[:200])  # Limit for performance
    lcs_score = (2 * lcs_len / (len(tokens1) + len(tokens2))) * 100

    return jaccard * 0.3 + freq_score * 0.4 + lcs_score * 0.3


def _structural_similarity(code1: str, code2: str, language: str) -> float:
    """Compare structural elements of two code snippets."""
    struct1 = _extract_structure(code1, language)
    struct2 = _extract_structure(code2, language)

    if not struct1 and not struct2:
        return 100.0

    scores = []

    # Compare number of functions
    f1, f2 = struct1.get("num_functions", 0), struct2.get("num_functions", 0)
    if f1 + f2 > 0:
        scores.append(1 - abs(f1 - f2) / max(f1, f2, 1))

    # Compare number of loops
    l1, l2 = struct1.get("num_loops", 0), struct2.get("num_loops", 0)
    if l1 + l2 > 0:
        scores.append(1 - abs(l1 - l2) / max(l1, l2, 1))

    # Compare nesting depth
    d1, d2 = struct1.get("max_depth", 0), struct2.get("max_depth", 0)
    if d1 + d2 > 0:
        scores.append(1 - abs(d1 - d2) / max(d1, d2, 1))

    # Compare number of conditionals
    c1, c2 = struct1.get("num_conditionals", 0), struct2.get("num_conditionals", 0)
    if c1 + c2 > 0:
        scores.append(1 - abs(c1 - c2) / max(c1, c2, 1))

    # Compare line count ratio
    lc1, lc2 = struct1.get("line_count", 1), struct2.get("line_count", 1)
    scores.append(1 - abs(lc1 - lc2) / max(lc1, lc2, 1))

    return (sum(scores) / len(scores) * 100) if scores else 50.0


def _extract_structure(code: str, language: str) -> Dict[str, int]:
    """Extract structural metrics from code."""
    lines = code.split('\n')
    structure = {
        "line_count": len(lines),
        "num_functions": 0,
        "num_loops": 0,
        "num_conditionals": 0,
        "max_depth": 0,
    }

    depth = 0
    for line in lines:
        stripped = line.strip()
        if language == "python":
            if re.match(r'def\s+', stripped):
                structure["num_functions"] += 1
            if re.match(r'(for|while)\s+', stripped):
                structure["num_loops"] += 1
            if re.match(r'(if|elif)\s+', stripped):
                structure["num_conditionals"] += 1
        else:
            if re.search(r'\b(for|while)\s*\(', stripped):
                structure["num_loops"] += 1
            if re.search(r'\bif\s*\(', stripped):
                structure["num_conditionals"] += 1
            if '{' in stripped:
                depth += stripped.count('{')
            if '}' in stripped:
                depth -= stripped.count('}')
            structure["max_depth"] = max(structure["max_depth"], depth)

    if language == "python":
        for line in lines:
            indent = len(line) - len(line.lstrip())
            structure["max_depth"] = max(structure["max_depth"], indent // 4)

    return structure


def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
    """Compute length of Longest Common Subsequence (optimized)."""
    m, n = len(seq1), len(seq2)
    if m == 0 or n == 0:
        return 0

    # Use two rows for space optimization
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev, curr = curr, [0] * (n + 1)

    return prev[n]


def _generate_details(token_sim: float, struct_sim: float, tokens1: List, tokens2: List) -> str:
    """Generate human-readable similarity analysis."""
    overall = (token_sim + struct_sim) / 2

    if overall > 90:
        verdict = "Very High Similarity - Code snippets are nearly identical"
    elif overall > 70:
        verdict = "High Similarity - Significant overlap in logic and structure"
    elif overall > 50:
        verdict = "Moderate Similarity - Some shared patterns but notable differences"
    elif overall > 30:
        verdict = "Low Similarity - Different approaches with minor commonalities"
    else:
        verdict = "Very Low Similarity - Distinctly different implementations"

    details = f"{verdict}. "
    details += f"Token overlap: {token_sim:.1f}% ({len(tokens1)} vs {len(tokens2)} tokens). "
    details += f"Structure match: {struct_sim:.1f}%."

    return details
