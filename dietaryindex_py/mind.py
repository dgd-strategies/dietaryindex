import pandas as pd

_HEALTHY = [
    "GREEN_LEAFY", "OTHER_VEG", "NUTS", "BERRIES", "BEANS",
    "WHOLE_GRAINS", "FISH", "POULTRY", "OLIVE_OIL", "WINE",
]
_UNHEALTHY = [
    "RED_MEAT", "BUTTER", "CHEESE", "PASTRIES", "FRIED_FOOD",
]

def mind_score(df: pd.DataFrame) -> pd.Series:
    """Compute a simplified MIND diet score.

    Each healthy food group counts as 1 point if the intake column is >0,
    and each unhealthy food group counts as 1 point if the intake is 0.
    The total score ranges from 0 to 15.
    """
    score = pd.Series(0, index=df.index, dtype=float)
    for col in _HEALTHY:
        if col in df.columns:
            score += (df[col] > 0).astype(float)
    for col in _UNHEALTHY:
        if col in df.columns:
            score += (df[col] == 0).astype(float)
    return score
