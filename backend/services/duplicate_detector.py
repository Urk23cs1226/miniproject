"""Duplicate code detection service."""

import re
from typing import Dict, Any, List
from collections import defaultdict


def detect_duplicates(code: str, language: str = "python", min_lines: int = 3) -> List[Dict[str, Any]]:
    """
    Detect duplicate or near-duplicate code blocks.
    Returns list of duplicate pairs with similarity scores.
    """
    lines = code.split('\n')
    blocks = _extract_blocks(lines, min_lines)
    duplicates = []
    seen = set()

    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            key = (blocks[i]["start"], blocks[j]["start"])
            if key in seen:
                continue

            sim = _block_similarity(blocks[i]["content"], blocks[j]["content"])
            if sim > 70:
                seen.add(key)
                duplicates.append({
                    "start_line": blocks[i]["start"],
                    "end_line": blocks[i]["end"],
                    "duplicate_of_start": blocks[j]["start"],
                    "duplicate_of_end": blocks[j]["end"],
                    "similarity": round(sim, 1),
                    "suggestion": _suggest_refactoring(blocks[i], blocks[j]),
                })

    return duplicates


def _extract_blocks(lines: List[str], min_lines: int) -> List[Dict]:
    """Extract meaningful code blocks from source."""
    blocks = []
    i = 0

    while i < len(lines):
        # Skip blank and comment lines
        if not lines[i].strip() or lines[i].strip().startswith('#') or lines[i].strip().startswith('//'):
            i += 1
            continue

        # Extract a block of min_lines consecutive non-empty lines
        block_lines = []
        start = i
        while i < len(lines) and len(block_lines) < min_lines + 5:
            if lines[i].strip():
                block_lines.append(lines[i])
            i += 1

        if len(block_lines) >= min_lines:
            blocks.append({
                "start": start + 1,
                "end": start + len(block_lines),
                "content": '\n'.join(block_lines),
                "normalized": _normalize_block('\n'.join(block_lines)),
            })

        # Slide window
        i = start + 1

    return blocks


def _normalize_block(code: str) -> str:
    """Normalize code for comparison (remove variable names, whitespace)."""
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', code.strip())
    # Replace variable names with placeholder
    normalized = re.sub(r'\b[a-z_]\w*\b', 'VAR', normalized)
    # Replace numbers
    normalized = re.sub(r'\b\d+\b', 'NUM', normalized)
    # Replace strings
    normalized = re.sub(r'"[^"]*"', 'STR', normalized)
    normalized = re.sub(r"'[^']*'", 'STR', normalized)
    return normalized


def _block_similarity(block1: str, block2: str) -> float:
    """Calculate similarity between two code blocks."""
    norm1 = _normalize_block(block1)
    norm2 = _normalize_block(block2)

    if norm1 == norm2:
        return 100.0

    tokens1 = norm1.split()
    tokens2 = norm2.split()

    if not tokens1 or not tokens2:
        return 0.0

    # Token overlap
    set1, set2 = set(tokens1), set(tokens2)
    if not (set1 | set2):
        return 0.0

    jaccard = len(set1 & set2) / len(set1 | set2) * 100
    return jaccard


def _suggest_refactoring(block1: Dict, block2: Dict) -> str:
    """Generate refactoring suggestion for duplicate blocks."""
    return (
        f"Extract lines {block1['start']}-{block1['end']} and "
        f"{block2['start']}-{block2['end']} into a shared function "
        f"to eliminate code duplication."
    )
