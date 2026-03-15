"""
LSTM autoencoder for bioluminescence anomaly detection.

Approach: train the autoencoder on "normal" seasonal patterns.
High reconstruction error on a given cell/day = the pattern doesn't
fit what the model learned as typical. That's the bloom event signal.

Architecture: encoder (2-layer LSTM) → bottleneck → decoder (2-layer LSTM)
Input: time series of P(biolum) per grid cell, sliding window of 30 days
Output: same window reconstructed
Anomaly score: MSE between input and reconstruction
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class BiolumAutoencoder(nn.Module):
    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 32,
        num_layers: int = 2,
        bottleneck_size: int = 8,
        window_size: int = 30,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.window_size = window_size

        self.encoder = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout
        )
        self.bottleneck = nn.Linear(hidden_size, bottleneck_size)
        self.expand = nn.Linear(bottleneck_size, hidden_size)
        self.decoder = nn.LSTM(
            hidden_size, input_size, num_layers,
            batch_first=True, dropout=dropout
        )

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        _, (h, _) = self.encoder(x)
        compressed = self.bottleneck(h[-1])
        expanded = self.expand(compressed)
        # Repeat across time steps for decoder input
        dec_input = expanded.unsqueeze(1).repeat(1, self.window_size, 1)
        output, _ = self.decoder(dec_input)
        return output


def make_windows(series: np.ndarray, window_size: int = 30) -> np.ndarray:
    """Convert a 1D time series to sliding windows of shape (n, window, 1)."""
    n = len(series) - window_size + 1
    windows = np.stack([series[i:i+window_size] for i in range(n)], axis=0)
    return windows[:, :, np.newaxis].astype(np.float32)


def train_autoencoder(
    series: np.ndarray,
    window_size: int = 30,
    hidden_size: int = 32,
    epochs: int = 50,
    lr: float = 1e-3,
    batch_size: int = 64,
    device: str = "cpu",
) -> tuple[BiolumAutoencoder, list[float]]:
    """Train the autoencoder on a bioluminescence probability time series."""
    windows = make_windows(series, window_size)
    dataset = TensorDataset(torch.from_numpy(windows))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = BiolumAutoencoder(window_size=window_size, hidden_size=hidden_size).to(device)
    optimiser = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    losses = []
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for (batch,) in loader:
            batch = batch.to(device)
            recon = model(batch)
            loss = criterion(recon, batch)
            optimiser.zero_grad()
            loss.backward()
            optimiser.step()
            epoch_loss += loss.item()
        avg = epoch_loss / len(loader)
        losses.append(avg)
        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{epochs} — loss: {avg:.5f}")

    return model, losses


def compute_anomaly_scores(
    model: BiolumAutoencoder,
    series: np.ndarray,
    window_size: int = 30,
    device: str = "cpu",
) -> np.ndarray:
    """
    Compute per-timestep anomaly score (reconstruction MSE).
    Returns an array of the same length as `series`, with NaN for
    the first window_size - 1 positions.
    """
    model.eval()
    windows = torch.from_numpy(make_windows(series, window_size)).to(device)

    with torch.no_grad():
        recons = model(windows).cpu().numpy()

    # Score = MSE per window, assigned to the last timestep of each window
    scores = np.full(len(series), np.nan)
    mse = np.mean((windows.cpu().numpy() - recons) ** 2, axis=(1, 2))
    scores[window_size - 1:] = mse

    return scores


def flag_bloom_events(
    scores: np.ndarray,
    dates,
    threshold_percentile: float = 95.0,
    min_duration_days: int = 3,
) -> list[dict]:
    """
    Flag bloom events: consecutive days where anomaly score exceeds threshold.

    Args:
        scores:                per-day anomaly scores
        dates:                 corresponding date index (pandas DatetimeIndex)
        threshold_percentile:  score percentile above which a day is anomalous
        min_duration_days:     minimum consecutive days to count as an event

    Returns:
        list of dicts with keys: start, end, duration, peak_score
    """
    threshold = np.nanpercentile(scores, threshold_percentile)
    above = ~np.isnan(scores) & (scores > threshold)

    events = []
    in_event = False
    start_idx = None

    for i, is_above in enumerate(above):
        if is_above and not in_event:
            in_event = True
            start_idx = i
        elif not is_above and in_event:
            duration = i - start_idx
            if duration >= min_duration_days:
                events.append({
                    "start":      dates[start_idx],
                    "end":        dates[i - 1],
                    "duration":   duration,
                    "peak_score": float(scores[start_idx:i].max()),
                })
            in_event = False

    return events
