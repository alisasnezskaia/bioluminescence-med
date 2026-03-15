"""
Spatial block cross-validation for ocean data.

Why this matters: ocean observations are spatially autocorrelated.
A point at (40°N, 10°E) is very similar to one at (40.1°N, 10.1°E).
Random train/test splits leak this information — you end up measuring
how well the model interpolates nearby points, not how well it generalises
to new areas. Spatial block CV holds out entire geographic chunks.

Reference:
    Roberts et al. (2017). Cross-validation strategies for data with
    temporal, spatial, hierarchical, or phylogenetic structure.
    Ecography, 40(8), 913-929.
"""

import numpy as np
import pandas as pd
from typing import Iterator, Tuple


def make_spatial_blocks(
    df: pd.DataFrame,
    block_size_deg: float = 4.0,
    n_folds: int = 5,
    lat_col: str = "lat",
    lon_col: str = "lon",
) -> list[np.ndarray]:
    """
    Assign each observation to a geographic block, then group blocks into folds.

    Args:
        df:             DataFrame with lat/lon columns
        block_size_deg: size of each spatial block in degrees (default 4°×4°)
        n_folds:        number of CV folds
        lat_col:        name of latitude column
        lon_col:        name of longitude column

    Returns:
        list of n_folds arrays, each containing the indices of the test set
    """
    lat_blocks = np.floor(df[lat_col] / block_size_deg).astype(int)
    lon_blocks = np.floor(df[lon_col] / block_size_deg).astype(int)
    block_ids = lat_blocks.astype(str) + "_" + lon_blocks.astype(str)

    unique_blocks = block_ids.unique()
    np.random.shuffle(unique_blocks)

    block_folds = np.array_split(unique_blocks, n_folds)

    test_indices = []
    for fold_blocks in block_folds:
        mask = block_ids.isin(fold_blocks)
        test_indices.append(df.index[mask].to_numpy())

    return test_indices


def spatial_cv_split(
    df: pd.DataFrame,
    block_size_deg: float = 4.0,
    n_folds: int = 5,
) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """
    Generator yielding (train_idx, test_idx) tuples for spatial CV.

    Usage:
        for train_idx, test_idx in spatial_cv_split(df):
            X_train = df.iloc[train_idx][feature_cols]
            X_test  = df.iloc[test_idx][feature_cols]
            ...
    """
    all_indices = np.arange(len(df))
    test_folds = make_spatial_blocks(df, block_size_deg, n_folds)

    for test_idx in test_folds:
        # Convert to positional indices
        test_pos = np.where(np.isin(all_indices, test_idx))[0]
        train_pos = np.where(~np.isin(all_indices, test_idx))[0]
        yield train_pos, test_pos


def report_fold_sizes(df: pd.DataFrame, block_size_deg: float = 4.0, n_folds: int = 5):
    """Print a summary of how many observations land in each fold."""
    folds = list(spatial_cv_split(df, block_size_deg, n_folds))
    print(f"Spatial block CV — {n_folds} folds, block size {block_size_deg}°")
    print(f"Total observations: {len(df)}")
    for i, (train_idx, test_idx) in enumerate(folds):
        print(f"  Fold {i+1}: train={len(train_idx)}, test={len(test_idx)}")
