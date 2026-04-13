"""Multi-language support utilities."""

import re
from typing import Optional

# Language keyword maps
KEYWORDS = {
    "python": {
        "def", "class", "import", "from", "return", "if", "elif", "else",
        "for", "while", "try", "except", "finally", "with", "as", "yield",
        "lambda", "pass", "break", "continue", "raise", "global", "nonlocal",
        "assert", "del", "True", "False", "None", "and", "or", "not", "in", "is",
        "async", "await",
    },
    "java": {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "enum", "extends", "final", "finally", "float", "for",
        "goto", "if", "implements", "import", "instanceof", "int",
        "interface", "long", "native", "new", "package", "private",
        "protected", "public", "return", "short", "static", "strictfp",
        "super", "switch", "synchronized", "this", "throw", "throws",
        "transient", "try", "void", "volatile", "while",
    },
    "cpp": {
        "alignas", "alignof", "and", "asm", "auto", "bitand", "bitor",
        "bool", "break", "case", "catch", "char", "class", "const",
        "constexpr", "continue", "decltype", "default", "delete", "do",
        "double", "dynamic_cast", "else", "enum", "explicit", "export",
        "extern", "false", "float", "for", "friend", "goto", "if",
        "inline", "int", "long", "mutable", "namespace", "new",
        "noexcept", "nullptr", "operator", "or", "private", "protected",
        "public", "register", "return", "short", "signed", "sizeof",
        "static", "static_cast", "struct", "switch", "template", "this",
        "throw", "true", "try", "typedef", "typeid", "typename",
        "union", "unsigned", "using", "virtual", "void", "volatile", "while",
        "#include", "#define", "#ifdef", "#ifndef", "#endif",
    },
}

# Common data structures by language
DATA_STRUCTURES = {
    "python": ["list", "dict", "set", "tuple", "deque", "defaultdict", "Counter", "heap", "heapq"],
    "java": ["ArrayList", "LinkedList", "HashMap", "TreeMap", "HashSet", "TreeSet", "Stack", "Queue", "PriorityQueue"],
    "cpp": ["vector", "list", "map", "unordered_map", "set", "unordered_set", "stack", "queue", "priority_queue"],
}


def detect_language(code: str, filename: Optional[str] = None) -> str:
    """Detect programming language from code content or filename."""
    if filename:
        ext_map = {
            ".py": "python", ".java": "java",
            ".cpp": "cpp", ".c": "cpp", ".h": "cpp", ".hpp": "cpp",
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang

    # Heuristic detection from content
    scores = {"python": 0, "java": 0, "cpp": 0}

    if "def " in code and ":" in code:
        scores["python"] += 3
    if "import " in code and ";" not in code:
        scores["python"] += 2
    if re.search(r'print\s*\(', code):
        scores["python"] += 1

    if "public class" in code or "public static void main" in code:
        scores["java"] += 5
    if "System.out.println" in code:
        scores["java"] += 3
    if re.search(r'import\s+[\w.]+;', code):
        scores["java"] += 2

    if "#include" in code:
        scores["cpp"] += 5
    if "cout" in code or "cin" in code:
        scores["cpp"] += 3
    if "std::" in code:
        scores["cpp"] += 3
    if "int main(" in code:
        scores["cpp"] += 2

    return max(scores, key=scores.get)


def get_keywords(language: str) -> set:
    """Get keywords for a language."""
    return KEYWORDS.get(language, KEYWORDS["python"])


def get_data_structures(language: str) -> list:
    """Get common data structures for a language."""
    return DATA_STRUCTURES.get(language, DATA_STRUCTURES["python"])
