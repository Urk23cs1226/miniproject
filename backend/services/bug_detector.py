"""Bug detection engine."""

import re
from typing import Dict, Any, List


def detect_bugs(code: str, ast_data: Dict[str, Any], language: str = "python") -> List[Dict[str, Any]]:
    """
    Detect potential bugs in the code.
    Returns list of bugs with probability and severity.
    """
    bugs = []
    lines = code.split('\n')

    if language == "python":
        bugs.extend(_detect_python_bugs(code, lines, ast_data))
    elif language == "java":
        bugs.extend(_detect_java_bugs(code, lines, ast_data))
    elif language == "cpp":
        bugs.extend(_detect_cpp_bugs(code, lines, ast_data))

    # Language-agnostic checks
    bugs.extend(_detect_common_bugs(code, lines, ast_data, language))

    return bugs


def _detect_python_bugs(code: str, lines: List[str], ast_data: Dict) -> List[Dict]:
    bugs = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Mutable default argument
        if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\}|\(\))', line):
            bugs.append({
                "type": "Mutable Default Argument",
                "description": "Using mutable default argument (list/dict). This is shared across calls.",
                "line": i + 1,
                "probability": 85.0,
                "severity": "high",
            })

        # Bare except
        if re.match(r'\s*except\s*:', line):
            bugs.append({
                "type": "Bare Except",
                "description": "Bare except catches all exceptions including SystemExit and KeyboardInterrupt.",
                "line": i + 1,
                "probability": 75.0,
                "severity": "medium",
            })

        # == None instead of is None
        if re.search(r'==\s*None|!=\s*None', line):
            bugs.append({
                "type": "Identity Check",
                "description": "Use 'is None' or 'is not None' instead of '==' for None comparison.",
                "line": i + 1,
                "probability": 70.0,
                "severity": "low",
            })

        # String concatenation in loop
        if re.search(r'\bfor\b', line) and i + 1 < len(lines):
            for j in range(i + 1, min(i + 10, len(lines))):
                if re.search(r'\w+\s*\+=\s*["\']|str\s*\+\s*str', lines[j]):
                    bugs.append({
                        "type": "Inefficient String Concatenation",
                        "description": "String concatenation in loop. Use ''.join() or list append instead.",
                        "line": j + 1,
                        "probability": 65.0,
                        "severity": "medium",
                    })
                    break

        # Global variable usage
        if stripped.startswith('global '):
            bugs.append({
                "type": "Global Variable",
                "description": "Global variable usage can lead to hard-to-track bugs and reduces testability.",
                "line": i + 1,
                "probability": 55.0,
                "severity": "medium",
            })

    # Unused variables (simple check)
    for func in ast_data.get("functions", []):
        for arg in func.get("args", []):
            if arg != "self" and arg != "cls":
                # Simple check: if arg appears only once in code
                count = len(re.findall(r'\b' + re.escape(arg) + r'\b', code))
                if count <= 1:
                    bugs.append({
                        "type": "Unused Parameter",
                        "description": f"Parameter '{arg}' in function '{func['name']}' may be unused.",
                        "line": func.get("line", 0),
                        "probability": 60.0,
                        "severity": "low",
                    })

    return bugs


def _detect_java_bugs(code: str, lines: List[str], ast_data: Dict) -> List[Dict]:
    bugs = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # String comparison with ==
        if re.search(r'==\s*"[^"]*"|"[^"]*"\s*==', line):
            bugs.append({
                "type": "String Comparison",
                "description": "Comparing strings with == instead of .equals(). This compares references, not values.",
                "line": i + 1,
                "probability": 90.0,
                "severity": "high",
            })

        # Null pointer risk
        if re.search(r'\w+\.\w+\(', line) and 'null' in code.lower():
            if not re.search(r'if\s*\(\s*\w+\s*!=\s*null', code[:code.find(line)]):
                bugs.append({
                    "type": "Potential NullPointerException",
                    "description": "Method called on object that might be null. Add null check.",
                    "line": i + 1,
                    "probability": 60.0,
                    "severity": "high",
                })

        # Empty catch block
        if re.search(r'catch\s*\([^)]+\)\s*\{', line):
            if i + 1 < len(lines) and lines[i + 1].strip() == '}':
                bugs.append({
                    "type": "Empty Catch Block",
                    "description": "Empty catch block silently swallows exceptions.",
                    "line": i + 1,
                    "probability": 80.0,
                    "severity": "high",
                })

        # Resource leak
        if re.search(r'new\s+(FileInputStream|BufferedReader|Scanner|Connection)', line):
            if 'try-with-resources' not in code and 'finally' not in code:
                bugs.append({
                    "type": "Resource Leak",
                    "description": "Resource opened without try-with-resources or finally block.",
                    "line": i + 1,
                    "probability": 72.0,
                    "severity": "high",
                })

    return bugs


def _detect_cpp_bugs(code: str, lines: List[str], ast_data: Dict) -> List[Dict]:
    bugs = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Buffer overflow risk
        if re.search(r'gets\s*\(|scanf\s*\(\s*"%s"', line):
            bugs.append({
                "type": "Buffer Overflow",
                "description": "Using unsafe string input function. Use fgets() or std::getline() instead.",
                "line": i + 1,
                "probability": 95.0,
                "severity": "critical",
            })

        # Memory leak
        if 'new ' in line and 'delete' not in code:
            bugs.append({
                "type": "Memory Leak",
                "description": "Memory allocated with 'new' but no matching 'delete' found. Consider using smart pointers.",
                "line": i + 1,
                "probability": 75.0,
                "severity": "high",
            })

        # Array out of bounds risk
        if re.search(r'\[\s*\w+\s*\]', line) and not re.search(r'if\s*\(.*<.*size|length|\.size\(\)', code):
            if re.search(r'\[\s*[a-zA-Z]', line):
                bugs.append({
                    "type": "Potential Array Out of Bounds",
                    "description": "Array accessed with variable index without apparent bounds checking.",
                    "line": i + 1,
                    "probability": 55.0,
                    "severity": "medium",
                })

    return bugs


def _detect_common_bugs(code: str, lines: List[str], ast_data: Dict, language: str) -> List[Dict]:
    """Language-agnostic bug detection."""
    bugs = []

    # Off-by-one potential
    for i, line in enumerate(lines):
        if re.search(r'<=\s*len\(|<=\s*\.length|<=\s*\.size\(\)', line):
            bugs.append({
                "type": "Off-By-One Error",
                "description": "Using '<=' with collection length may cause index out of range.",
                "line": i + 1,
                "probability": 72.0,
                "severity": "medium",
            })

    # Infinite loop risk
    for loop in ast_data.get("loops", []):
        if loop["type"] == "while":
            line_idx = loop["line"] - 1
            if line_idx < len(lines):
                if re.search(r'while\s*\(\s*true\s*\)|while\s+True\s*:', lines[line_idx]):
                    has_break = False
                    for j in range(line_idx + 1, min(line_idx + 20, len(lines))):
                        if 'break' in lines[j] or 'return' in lines[j]:
                            has_break = True
                            break
                    if not has_break:
                        bugs.append({
                            "type": "Infinite Loop",
                            "description": "while True/while(true) loop without visible break or return statement.",
                            "line": loop["line"],
                            "probability": 68.0,
                            "severity": "high",
                        })

    # Hardcoded credentials
    for i, line in enumerate(lines):
        if re.search(r'(password|passwd|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
            bugs.append({
                "type": "Hardcoded Credentials",
                "description": "Potential hardcoded password or API key. Use environment variables.",
                "line": i + 1,
                "probability": 88.0,
                "severity": "critical",
            })

    # Magic numbers
    magic_count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        numbers = re.findall(r'(?<!=)\b(\d+)\b', stripped)
        for num in numbers:
            if int(num) not in (0, 1, 2, -1, 10, 100, 1000):
                magic_count += 1

    if magic_count > 3:
        bugs.append({
            "type": "Magic Numbers",
            "description": f"Found {magic_count} magic numbers. Consider using named constants for readability.",
            "line": 0,
            "probability": 50.0,
            "severity": "low",
        })

    return bugs
