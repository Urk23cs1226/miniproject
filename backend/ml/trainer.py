"""Training pipeline for code models."""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os
import json
from .model import CodeLSTM
from .tokenizer import CodeTokenizer
from .dataset import CodeDataset


def train_model(
    code_samples: list,
    vocab_size: int = 5000,
    embed_dim: int = 128,
    hidden_dim: int = 256,
    num_layers: int = 2,
    epochs: int = 10,
    batch_size: int = 16,
    learning_rate: float = 0.001,
    save_path: str = None,
):
    """
    Train the LSTM code generation model.
    Returns trained model and training history.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on: {device}")

    # Initialize tokenizer
    tokenizer = CodeTokenizer(vocab_size=vocab_size)
    tokenizer.fit(code_samples)

    # Create dataset
    dataset = CodeDataset(code_samples, tokenizer, max_length=256)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = CodeLSTM(
        vocab_size=tokenizer.vocab,
        embed_dim=embed_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
    ).to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    history = {"loss": [], "epoch": []}

    # Training loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0

        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            target_ids = batch["target_ids"].to(device)

            optimizer.zero_grad()
            output, _ = model(input_ids)

            # Reshape for loss calculation
            output = output.view(-1, tokenizer.vocab)
            target = target_ids.view(-1)

            loss = criterion(output, target)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()
            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / max(num_batches, 1)
        history["loss"].append(avg_loss)
        history["epoch"].append(epoch + 1)

        scheduler.step()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    # Save model
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save({
            "model_state": model.state_dict(),
            "vocab_size": tokenizer.vocab,
            "embed_dim": embed_dim,
            "hidden_dim": hidden_dim,
            "num_layers": num_layers,
        }, save_path)

        tokenizer.save(save_path.replace('.pt', '_tokenizer.json'))
        print(f"Model saved to {save_path}")

    return model, tokenizer, history
