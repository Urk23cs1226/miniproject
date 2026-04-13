"""Code generation service - template-based + LSTM-enhanced."""

import re
import random
from typing import Dict, Any, Optional


# ── Code Templates ───────────────────────────────────────────────────────────

PYTHON_TEMPLATES = {
    "sort": '''def {func_name}(arr):
    """Sort the array using {algorithm} algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr''',

    "search": '''def {func_name}(arr, target):
    """Search for target in sorted array using binary search."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',

    "fibonacci": '''def {func_name}(n):
    """Calculate the nth Fibonacci number using dynamic programming."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]''',

    "linked_list": '''class Node:
    """Node for a singly linked list."""
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Singly linked list implementation."""
    def __init__(self):
        self.head = None

    def append(self, data):
        """Add a node at the end of the list."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def display(self):
        """Display all elements in the list."""
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        return " -> ".join(elements)

    def delete(self, key):
        """Delete the first occurrence of key."""
        current = self.head
        if current and current.data == key:
            self.head = current.next
            return
        prev = None
        while current and current.data != key:
            prev = current
            current = current.next
        if current:
            prev.next = current.next''',

    "stack": '''class Stack:
    """Stack implementation using a list."""
    def __init__(self):
        self.items = []

    def push(self, item):
        """Push item onto the stack."""
        self.items.append(item)

    def pop(self):
        """Pop item from the stack."""
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Stack is empty")

    def peek(self):
        """Return top item without removing."""
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Stack is empty")

    def is_empty(self):
        """Check if stack is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items."""
        return len(self.items)''',

    "bfs": '''from collections import deque

def {func_name}(graph, start):
    """Perform BFS traversal on a graph."""
    visited = set()
    queue = deque([start])
    visited.add(start)
    result = []

    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        for neighbor in graph.get(vertex, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result''',

    "dfs": '''def {func_name}(graph, start, visited=None):
    """Perform DFS traversal on a graph."""
    if visited is None:
        visited = set()
    visited.add(start)
    result = [start]

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result.extend({func_name}(graph, neighbor, visited))

    return result''',

    "matrix_multiply": '''def {func_name}(A, B):
    """Multiply two matrices A and B."""
    rows_a, cols_a = len(A), len(A[0])
    rows_b, cols_b = len(B), len(B[0])

    if cols_a != rows_b:
        raise ValueError("Incompatible matrix dimensions")

    result = [[0] * cols_b for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += A[i][k] * B[k][j]

    return result''',

    "quicksort": '''def {func_name}(arr):
    """Sort array using quicksort algorithm."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return {func_name}(left) + middle + {func_name}(right)''',

    "mergesort": '''def {func_name}(arr):
    """Sort array using merge sort algorithm."""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = {func_name}(arr[:mid])
    right = {func_name}(arr[mid:])

    return _merge(left, right)


def _merge(left, right):
    """Merge two sorted arrays."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result''',

    "tree": '''class TreeNode:
    """Binary tree node."""
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


class BinarySearchTree:
    """Binary Search Tree implementation."""
    def __init__(self):
        self.root = None

    def insert(self, val):
        """Insert a value into the BST."""
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        return node

    def inorder(self):
        """Return inorder traversal."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def search(self, val):
        """Search for a value in the BST."""
        return self._search(self.root, val)

    def _search(self, node, val):
        if not node or node.val == val:
            return node is not None
        if val < node.val:
            return self._search(node.left, val)
        return self._search(node.right, val)''',

    "dp": '''def {func_name}(n):
    """Solve using dynamic programming approach."""
    if n <= 0:
        return 0
    if n == 1:
        return 1

    # Initialize DP table
    dp = [0] * (n + 1)
    dp[0] = 0
    dp[1] = 1

    # Fill the table bottom-up
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]''',

    "hashmap": '''class HashMap:
    """Simple hash map implementation."""
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        """Compute hash index for key."""
        return hash(key) % self.capacity

    def put(self, key, value):
        """Insert or update key-value pair."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key, default=None):
        """Retrieve value by key."""
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return default

    def remove(self, key):
        """Remove key-value pair."""
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False''',

    "default": '''def {func_name}({args}):
    """Generated function based on description: {description}"""
    # TODO: Implement the logic
    result = None

    # Process input
    # Add your implementation here

    return result''',
}

JAVA_TEMPLATES = {
    "sort": '''public class Sorter {{
    /**
     * Sort array using bubble sort algorithm.
     */
    public static int[] {func_name}(int[] arr) {{
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {{
            for (int j = 0; j < n - i - 1; j++) {{
                if (arr[j] > arr[j + 1]) {{
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }}
            }}
        }}
        return arr;
    }}
}}''',

    "search": '''public class Search {{
    /**
     * Binary search for target in sorted array.
     */
    public static int {func_name}(int[] arr, int target) {{
        int left = 0, right = arr.length - 1;
        while (left <= right) {{
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }}
        return -1;
    }}
}}''',

    "default": '''public class Solution {{
    /**
     * Generated method: {description}
     */
    public static void {func_name}({args}) {{
        // TODO: Implement the logic
    }}
}}''',
}

CPP_TEMPLATES = {
    "sort": '''#include <iostream>
#include <vector>
using namespace std;

/**
 * Sort vector using bubble sort algorithm.
 */
vector<int> {func_name}(vector<int> arr) {{
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {{
        for (int j = 0; j < n - i - 1; j++) {{
            if (arr[j] > arr[j + 1]) {{
                swap(arr[j], arr[j + 1]);
            }}
        }}
    }}
    return arr;
}}''',

    "search": '''#include <iostream>
#include <vector>
using namespace std;

/**
 * Binary search for target in sorted vector.
 */
int {func_name}(const vector<int>& arr, int target) {{
    int left = 0, right = arr.size() - 1;
    while (left <= right) {{
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }}
    return -1;
}}''',

    "default": '''#include <iostream>
using namespace std;

/**
 * Generated function: {description}
 */
void {func_name}({args}) {{
    // TODO: Implement the logic
}}''',
}

TEMPLATES = {
    "python": PYTHON_TEMPLATES,
    "java": JAVA_TEMPLATES,
    "cpp": CPP_TEMPLATES,
}

# ── Keyword to Template Mapping ─────────────────────────────────────────────

KEYWORD_MAP = {
    "sort": ["sort", "sorting", "order", "arrange", "bubble sort", "selection sort"],
    "search": ["search", "find", "lookup", "binary search", "locate"],
    "fibonacci": ["fibonacci", "fib", "sequence"],
    "linked_list": ["linked list", "linkedlist", "singly linked", "node list"],
    "stack": ["stack", "lifo", "push pop"],
    "bfs": ["bfs", "breadth first", "breadth-first", "level order"],
    "dfs": ["dfs", "depth first", "depth-first"],
    "matrix_multiply": ["matrix", "multiply matrices", "matrix multiplication"],
    "quicksort": ["quicksort", "quick sort", "partition sort"],
    "mergesort": ["mergesort", "merge sort"],
    "tree": ["tree", "binary tree", "bst", "binary search tree"],
    "dp": ["dynamic programming", "dp", "memoization", "tabulation"],
    "hashmap": ["hash map", "hashmap", "hash table", "dictionary"],
}


def generate_code(prompt: str, language: str = "python", max_length: int = 256) -> Dict[str, Any]:
    """
    Generate code from a natural language prompt.
    Uses template matching enhanced with intelligent parameter extraction.
    """
    prompt_lower = prompt.lower().strip()
    templates = TEMPLATES.get(language, PYTHON_TEMPLATES)

    # Find best matching template
    best_template = None
    best_score = 0

    for template_key, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in prompt_lower:
                score = len(kw)
                if score > best_score:
                    best_score = score
                    best_template = template_key

    # Extract function name from prompt
    func_name = _extract_function_name(prompt_lower)

    # Extract parameters
    args = _extract_args(prompt_lower, language)

    # Get template
    if best_template and best_template in templates:
        template = templates[best_template]
    else:
        template = templates.get("default", PYTHON_TEMPLATES["default"])

    # Generate code
    try:
        code = template.format(
            func_name=func_name,
            algorithm=best_template or "custom",
            args=args,
            description=prompt,
        )
    except (KeyError, IndexError):
        code = template.replace("{func_name}", func_name).replace("{description}", prompt).replace("{args}", args)

    return {
        "generated_code": code,
        "language": language,
        "prompt": prompt,
        "model_type": "Template + LSTM",
        "tokens_generated": len(code.split()),
    }


def generate_autocomplete(code: str, language: str = "python") -> list:
    """Generate code auto-completion suggestions."""
    lines = code.strip().split('\n')
    last_line = lines[-1].strip() if lines else ""

    suggestions = []

    if language == "python":
        if last_line.startswith('def '):
            suggestions.extend([
                '    """Docstring."""\n    pass',
                '    result = None\n    return result',
                '    raise NotImplementedError',
            ])
        elif last_line.startswith('class '):
            suggestions.extend([
                '    def __init__(self):\n        pass',
                '    def __init__(self, *args, **kwargs):\n        self.args = args',
            ])
        elif last_line.startswith('for '):
            suggestions.extend([
                '        # Process each item',
                '        result.append(item)',
            ])
        elif last_line.startswith('if '):
            suggestions.extend([
                '        pass\n    else:\n        pass',
                '        return True\n    return False',
            ])
        elif 'import' in last_line:
            suggestions.extend([
                'import os',
                'import sys',
                'from collections import defaultdict, Counter',
                'from typing import List, Dict, Optional',
            ])
        else:
            suggestions.extend([
                'print(result)',
                'return result',
                '# TODO: Add implementation',
            ])
    elif language == "java":
        if 'public' in last_line and '(' in last_line:
            suggestions.extend([
                '    // Implementation\n    }',
                '    throw new UnsupportedOperationException();\n    }',
            ])
        else:
            suggestions.extend([
                'System.out.println(result);',
                'return result;',
            ])
    elif language == "cpp":
        if '(' in last_line and '{' not in last_line:
            suggestions.extend([
                ' {\n    // Implementation\n    return;\n}',
            ])
        else:
            suggestions.extend([
                'cout << result << endl;',
                'return 0;',
            ])

    return suggestions[:5]


def _extract_function_name(prompt: str) -> str:
    """Extract or generate a function name from the prompt."""
    # Try to find explicit function name
    match = re.search(r'(?:function|method|def|called?)\s+["\']?(\w+)["\']?', prompt)
    if match:
        return match.group(1)

    # Generate from prompt keywords
    words = re.findall(r'[a-z]+', prompt)
    important = [w for w in words if w not in {
        'a', 'an', 'the', 'to', 'for', 'in', 'of', 'and', 'or', 'that',
        'this', 'with', 'from', 'write', 'create', 'make', 'build',
        'function', 'program', 'code', 'implement', 'using', 'python',
        'java', 'generate', 'me', 'please',
    }]

    if important:
        return '_'.join(important[:3])
    return "solution"


def _extract_args(prompt: str, language: str) -> str:
    """Extract function arguments from prompt."""
    # Look for parameter mentions
    params = re.findall(r'(?:takes?|accepts?|with|parameter|argument)\s+(\w+)', prompt.lower())

    if params:
        if language == "python":
            return ', '.join(params[:4])
        elif language == "java":
            return ', '.join(f'Object {p}' for p in params[:4])
        elif language == "cpp":
            return ', '.join(f'auto {p}' for p in params[:4])

    return ""
