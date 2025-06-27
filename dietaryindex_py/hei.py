import pandas as pd

_COMPONENTS = [
    "TOTAL_FRT", "WHOLE_FRT", "TOTAL_VEG", "GREENS_BEANS", "WHOLE_GRAIN",
    "DAIRY", "TOTAL_PROTEIN", "SEA_PLANT_PROTEIN", "FATTY_ACID",
    "REFINED_GRAIN", "SODIUM", "ADDED_SUGARS", "SAT_FAT",
]

_MAX_SCORES = {
    "TOTAL_FRT": 5, "WHOLE_FRT": 5, "TOTAL_VEG": 5, "GREENS_BEANS": 5,
    "WHOLE_GRAIN": 10, "DAIRY": 10, "TOTAL_PROTEIN": 5,
    "SEA_PLANT_PROTEIN": 5, "FATTY_ACID": 10, "REFINED_GRAIN": 10,
    "SODIUM": 10, "ADDED_SUGARS": 10, "SAT_FAT": 10,
}

def hei_score(df: pd.DataFrame) -> pd.Series:
    """Compute a very simplified HEI-style score.

    This function expects columns named as in `_COMPONENTS`. The component
    scores are assumed to be pre-scaled from 0 to the component maximum.
    The total score is the sum of available component columns and may
    range up to 100.
    """
    score = pd.Series(0.0, index=df.index)
    for comp in _COMPONENTS:
        if comp in df.columns:
            score += df[comp].clip(lower=0, upper=_MAX_SCORES[comp])
    return score
