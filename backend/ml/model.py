"""LSTM model definition for code generation (PyTorch)."""

import torch
import torch.nn as nn


class CodeLSTM(nn.Module):
    """
    LSTM-based sequence model for source code generation.
    Encoder-decoder architecture with attention mechanism.
    """

    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3):
        super(CodeLSTM, self).__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=False,
        )

        # Attention layer
        self.attention = nn.Linear(hidden_dim, hidden_dim)
        self.attention_combine = nn.Linear(hidden_dim * 2, hidden_dim)

        # Output layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim, vocab_size)

        self._init_weights()

    def _init_weights(self):
        """Initialize weights with Xavier uniform."""
        for name, param in self.named_parameters():
            if 'weight' in name and param.dim() > 1:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)

    def forward(self, x, hidden=None):
        """
        Forward pass.
        Args:
            x: Input tensor of shape (batch_size, seq_length)
            hidden: Optional initial hidden state
        Returns:
            output: Logits of shape (batch_size, seq_length, vocab_size)
            hidden: Final hidden state
        """
        batch_size, seq_len = x.size()

        # Embedding
        embedded = self.embedding(x)  # (batch, seq, embed_dim)
        embedded = self.dropout(embedded)

        # LSTM
        if hidden is None:
            hidden = self.init_hidden(batch_size, x.device)

        lstm_out, hidden = self.lstm(embedded, hidden)  # (batch, seq, hidden_dim)

        # Self-attention
        attn_weights = torch.softmax(self.attention(lstm_out), dim=-1)
        attn_applied = attn_weights * lstm_out
        combined = torch.cat([lstm_out, attn_applied], dim=-1)
        attended = self.attention_combine(combined)

        # Output projection
        out = self.fc1(attended)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)  # (batch, seq, vocab_size)

        return out, hidden

    def init_hidden(self, batch_size, device):
        """Initialize hidden state."""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        return (h0, c0)

    def generate(self, start_tokens, max_length=100, temperature=0.8):
        """
        Generate a sequence of tokens.
        Args:
            start_tokens: Starting token IDs (list or tensor)
            max_length: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
        """
        self.eval()
        device = next(self.parameters()).device

        if isinstance(start_tokens, list):
            tokens = torch.tensor([start_tokens], device=device)
        else:
            tokens = start_tokens.unsqueeze(0) if start_tokens.dim() == 1 else start_tokens

        generated = list(start_tokens) if isinstance(start_tokens, list) else start_tokens.tolist()
        hidden = None

        with torch.no_grad():
            for _ in range(max_length):
                output, hidden = self(tokens, hidden)
                logits = output[:, -1, :] / temperature

                # Top-k sampling
                top_k = 50
                top_logits, top_indices = torch.topk(logits, top_k, dim=-1)
                probs = torch.softmax(top_logits, dim=-1)
                next_token_idx = torch.multinomial(probs, 1)
                next_token = top_indices.gather(1, next_token_idx)

                generated.append(next_token.item())
                tokens = next_token

                # Stop at end token (token id 2)
                if next_token.item() == 2:
                    break

        return generated


class CodeTransformer(nn.Module):
    """
    Simplified Transformer model for code understanding.
    Used for classification tasks (algorithm detection, complexity prediction).
    """

    def __init__(self, vocab_size, embed_dim=128, num_heads=4, num_layers=2, num_classes=10, dropout=0.3):
        super(CodeTransformer, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.pos_encoding = nn.Embedding(512, embed_dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, num_classes),
        )

    def forward(self, x):
        """Forward pass for classification."""
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)

        embedded = self.embedding(x) + self.pos_encoding(positions)
        encoded = self.transformer(embedded)

        # Use mean pooling
        pooled = encoded.mean(dim=1)
        return self.classifier(pooled)
