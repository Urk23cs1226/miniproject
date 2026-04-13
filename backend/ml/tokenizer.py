"""Code-aware tokenizer for source code."""

import re
import json
import os
from typing import List, Dict, Optional
from collections import Counter


class CodeTokenizer:
    """
    Tokenizer for source code that handles keywords, operators, identifiers.
    """

    SPECIAL_TOKENS = {
        "<PAD>": 0,
        "<UNK>": 1,
        "<EOS>": 2,
        "<BOS>": 3,
        "<NEWLINE>": 4,
        "<INDENT>": 5,
        "<DEDENT>": 6,
    }

    def __init__(self, vocab_size: int = 5000):
        self.vocab_size = vocab_size
        self.token_to_id: Dict[str, int] = dict(self.SPECIAL_TOKENS)
        self.id_to_token: Dict[int, str] = {v: k for k, v in self.SPECIAL_TOKENS.items()}
        self.next_id = len(self.SPECIAL_TOKENS)
        self.fitted = False

    def fit(self, code_samples: List[str]):
        """Build vocabulary from code samples."""
        counter = Counter()
        for code in code_samples:
            tokens = self._raw_tokenize(code)
            counter.update(tokens)

        # Add most common tokens to vocab
        for token, _ in counter.most_common(self.vocab_size - len(self.SPECIAL_TOKENS)):
            if token not in self.token_to_id:
                self.token_to_id[token] = self.next_id
                self.id_to_token[self.next_id] = token
                self.next_id += 1

        self.fitted = True

    def encode(self, code: str, max_length: int = 512) -> List[int]:
        """Encode code string to token IDs."""
        tokens = self._raw_tokenize(code)
        ids = [self.SPECIAL_TOKENS["<BOS>"]]

        for token in tokens[:max_length - 2]:
            ids.append(self.token_to_id.get(token, self.SPECIAL_TOKENS["<UNK>"]))

        ids.append(self.SPECIAL_TOKENS["<EOS>"])

        # Pad
        while len(ids) < max_length:
            ids.append(self.SPECIAL_TOKENS["<PAD>"])

        return ids[:max_length]

    def decode(self, ids: List[int]) -> str:
        """Decode token IDs back to code string."""
        tokens = []
        for id in ids:
            if id in (0, 2, 3):  # Skip PAD, EOS, BOS
                continue
            token = self.id_to_token.get(id, "<UNK>")
            if token == "<NEWLINE>":
                tokens.append("\n")
            elif token == "<INDENT>":
                tokens.append("    ")
            elif token == "<DEDENT>":
                pass
            else:
                tokens.append(token)
        return " ".join(tokens)

    def _raw_tokenize(self, code: str) -> List[str]:
        """Tokenize source code into raw tokens."""
        tokens = []

        for line in code.split('\n'):
            # Handle indentation
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            indent_level = indent // 4
            for _ in range(indent_level):
                tokens.append("<INDENT>")

            # Tokenize the line content
            line_tokens = re.findall(
                r'""".*?"""|\'\'\'.*?\'\'\'|"[^"]*"|\'[^\']*\'|'  # strings
                r'#.*$|//.*$|'  # comments
                r'\d+\.\d+|\d+|'  # numbers
                r'[a-zA-Z_]\w*|'  # identifiers
                r'[+\-*/=<>!&|%^~]=?|'  # operators
                r'[{}\[\]();:,.]|'  # delimiters
                r'\S',  # any other non-whitespace
                stripped
            )
            tokens.extend(line_tokens)
            tokens.append("<NEWLINE>")

        return tokens

    @property
    def vocab(self) -> int:
        """Return current vocabulary size."""
        return len(self.token_to_id)

    def save(self, path: str):
        """Save tokenizer vocabulary to file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "token_to_id": self.token_to_id,
            "vocab_size": self.vocab_size,
            "next_id": self.next_id,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, path: str):
        """Load tokenizer vocabulary from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.token_to_id = data["token_to_id"]
        self.id_to_token = {int(v): k for k, v in self.token_to_id.items()}
        self.vocab_size = data["vocab_size"]
        self.next_id = data["next_id"]
        self.fitted = True
