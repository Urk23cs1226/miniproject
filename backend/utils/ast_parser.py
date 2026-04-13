"""Multi-language AST parsing utilities."""

import ast
import re
import tokenize
import io
from typing import Dict, List, Any, Optional


class ASTParser:
    """Unified AST parser supporting Python, Java, and C++."""

    @staticmethod
    def parse_python(code: str) -> Dict[str, Any]:
        """Parse Python code using the ast module."""
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "loops": [],
            "conditionals": [],
            "variables": [],
            "returns": [],
            "calls": [],
            "errors": [],
            "node_count": 0,
            "max_depth": 0,
            "has_recursion": False,
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result["errors"].append(f"SyntaxError: {e.msg} at line {e.lineno}")
            return result

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.depth = 0
                self.max_depth = 0
                self.node_count = 0
                self.function_names = set()

            def generic_visit(self, node):
                self.node_count += 1
                self.depth += 1
                self.max_depth = max(self.max_depth, self.depth)
                super().generic_visit(node)
                self.depth -= 1

            def visit_FunctionDef(self, node):
                self.function_names.add(node.name)
                result["functions"].append({
                    "name": node.name,
                    "args": [a.arg for a in node.args.args],
                    "line": node.lineno,
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node)),
                    "body_lines": node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                })
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)

            def visit_ClassDef(self, node):
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                result["classes"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "bases": [self._get_name(b) for b in node.bases],
                })
                self.generic_visit(node)

            def visit_Import(self, node):
                for alias in node.names:
                    result["imports"].append(alias.name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{module}.{alias.name}")
                self.generic_visit(node)

            def visit_For(self, node):
                result["loops"].append({"type": "for", "line": node.lineno})
                self.generic_visit(node)

            def visit_While(self, node):
                result["loops"].append({"type": "while", "line": node.lineno})
                self.generic_visit(node)

            def visit_If(self, node):
                result["conditionals"].append({"line": node.lineno})
                self.generic_visit(node)

            def visit_Return(self, node):
                result["returns"].append({"line": node.lineno})
                self.generic_visit(node)

            def visit_Call(self, node):
                name = self._get_name(node.func)
                result["calls"].append({"name": name, "line": node.lineno})
                self.generic_visit(node)

            def _get_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self._get_name(node.value)}.{node.attr}"
                return "unknown"

            def _get_decorator_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Call):
                    return self._get_name(node.func)
                elif isinstance(node, ast.Attribute):
                    return self._get_name(node)
                return "unknown"

        visitor = Visitor()
        visitor.visit(tree)

        result["node_count"] = visitor.node_count
        result["max_depth"] = visitor.max_depth

        # Check for recursion
        for func in result["functions"]:
            for call in result["calls"]:
                if call["name"] == func["name"]:
                    result["has_recursion"] = True
                    break

        return result

    @staticmethod
    def parse_java(code: str) -> Dict[str, Any]:
        """Parse Java code using regex-based analysis."""
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "loops": [],
            "conditionals": [],
            "variables": [],
            "returns": [],
            "calls": [],
            "errors": [],
            "node_count": 0,
            "max_depth": 0,
            "has_recursion": False,
        }

        lines = code.split("\n")

        # Find imports
        for i, line in enumerate(lines):
            m = re.match(r'\s*import\s+([\w.]+);', line)
            if m:
                result["imports"].append(m.group(1))

        # Find classes
        for i, line in enumerate(lines):
            m = re.match(r'\s*(?:public|private|protected)?\s*(?:static\s+)?(?:abstract\s+)?class\s+(\w+)', line)
            if m:
                result["classes"].append({"name": m.group(1), "line": i + 1, "methods": [], "bases": []})

        # Find methods
        method_pattern = re.compile(
            r'\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+(?:<[\w<>,\s]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        )
        func_names = set()
        for i, line in enumerate(lines):
            m = method_pattern.match(line)
            if m and m.group(1) not in ('if', 'for', 'while', 'switch', 'catch'):
                name = m.group(1)
                func_names.add(name)
                args = [a.strip().split()[-1] for a in m.group(2).split(",") if a.strip()] if m.group(2).strip() else []
                result["functions"].append({
                    "name": name, "args": args, "line": i + 1,
                    "decorators": [], "has_return": True, "body_lines": 0
                })

        # Find loops
        for i, line in enumerate(lines):
            if re.search(r'\bfor\s*\(', line):
                result["loops"].append({"type": "for", "line": i + 1})
            if re.search(r'\bwhile\s*\(', line):
                result["loops"].append({"type": "while", "line": i + 1})

        # Find conditionals
        for i, line in enumerate(lines):
            if re.search(r'\bif\s*\(', line):
                result["conditionals"].append({"line": i + 1})

        # Detect recursion
        for func in result["functions"]:
            pattern = re.compile(r'\b' + re.escape(func["name"]) + r'\s*\(')
            for i, line in enumerate(lines):
                if i + 1 != func["line"] and pattern.search(line):
                    result["has_recursion"] = True
                    break

        result["node_count"] = len(lines)
        result["max_depth"] = _count_max_nesting(code)

        return result

    @staticmethod
    def parse_cpp(code: str) -> Dict[str, Any]:
        """Parse C++ code using regex-based analysis."""
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "loops": [],
            "conditionals": [],
            "variables": [],
            "returns": [],
            "calls": [],
            "errors": [],
            "node_count": 0,
            "max_depth": 0,
            "has_recursion": False,
        }

        lines = code.split("\n")

        # Find includes
        for i, line in enumerate(lines):
            m = re.match(r'\s*#include\s+[<"]([^>"]+)[>"]', line)
            if m:
                result["imports"].append(m.group(1))

        # Find classes
        for i, line in enumerate(lines):
            m = re.match(r'\s*class\s+(\w+)', line)
            if m:
                result["classes"].append({"name": m.group(1), "line": i + 1, "methods": [], "bases": []})

        # Find functions
        func_pattern = re.compile(
            r'\s*(?:\w+(?:::)?)*\s*(?:\w+(?:<[\w<>,\s]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*\{'
        )
        func_names = set()
        for i, line in enumerate(lines):
            m = func_pattern.match(line)
            if m and m.group(1) not in ('if', 'for', 'while', 'switch', 'catch', 'class'):
                name = m.group(1)
                func_names.add(name)
                args_str = m.group(2).strip()
                args = [a.strip().split()[-1] for a in args_str.split(",") if a.strip()] if args_str else []
                result["functions"].append({
                    "name": name, "args": args, "line": i + 1,
                    "decorators": [], "has_return": True, "body_lines": 0
                })

        # Find loops
        for i, line in enumerate(lines):
            if re.search(r'\bfor\s*\(', line):
                result["loops"].append({"type": "for", "line": i + 1})
            if re.search(r'\bwhile\s*\(', line):
                result["loops"].append({"type": "while", "line": i + 1})

        # Find conditionals
        for i, line in enumerate(lines):
            if re.search(r'\bif\s*\(', line):
                result["conditionals"].append({"line": i + 1})

        result["node_count"] = len(lines)
        result["max_depth"] = _count_max_nesting(code)

        return result

    @classmethod
    def parse(cls, code: str, language: str = "python") -> Dict[str, Any]:
        """Parse code in the specified language."""
        parsers = {
            "python": cls.parse_python,
            "java": cls.parse_java,
            "cpp": cls.parse_cpp,
        }
        parser = parsers.get(language, cls.parse_python)
        return parser(code)


def _count_max_nesting(code: str) -> int:
    """Count maximum nesting depth by tracking braces / indentation."""
    depth = 0
    max_depth = 0
    for char in code:
        if char == '{':
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == '}':
            depth = max(0, depth - 1)
    if max_depth == 0:
        # Python-style: use indentation
        for line in code.split('\n'):
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                d = indent // 4
                max_depth = max(max_depth, d)
    return max_depth


def count_lines(code: str) -> Dict[str, int]:
    """Count various line metrics."""
    lines = code.split('\n')
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comment = sum(1 for l in lines if l.strip().startswith('#') or l.strip().startswith('//'))
    return {"total": total, "blank": blank, "comment": comment, "code": total - blank - comment}
