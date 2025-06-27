import pandas as pd
from math import erf, sqrt

# Map variable -> (overall_inflammatory_score, global_mean, sd)
_DII_DATA = {
    "ALCOHOL_DII": (-0.278, 13.98, 3.72),
    "VITB12_DII": (0.106, 5.15, 2.7),
    "VITB6_DII": (-0.365, 1.47, 0.74),
    "BCAROTENE_DII": (-0.584, 3718, 1720),
    "CAFFEINE_DII": (-0.11, 8.05, 6.67),
    "CARB_DII": (0.097, 272.2, 40),
    "CHOLES_DII": (0.11, 279.4, 51.2),
    "KCAL_DII": (0.18, 2056, 338),
    "EUGENOL_DII": (-0.14, 0.01, 0.08),
    "TOTALFAT_DII": (0.298, 71.4, 19.4),
    "FIBER_DII": (-0.663, 18.8, 4.9),
    "FOLICACID_DII": (-0.19, 273, 70.7),
    "GARLIC_DII": (-0.412, 4.35, 2.9),
    "GINGER_DII": (-0.453, 59, 63.2),
    "IRON_DII": (0.032, 13.35, 3.71),
    "MG_DII": (-0.484, 310.1, 139.4),
    "MUFA_DII": (-0.009, 27, 6.1),
    "NIACIN_DII": (-0.246, 25.9, 11.77),
    "N3FAT_DII": (-0.436, 1.06, 1.06),
    "N6FAT_DII": (-0.159, 10.8, 7.5),
    "ONION_DII": (-0.301, 35.9, 18.4),
    "PROTEIN_DII": (0.021, 79.4, 13.9),
    "PUFA_DII": (-0.337, 13.88, 3.76),
    "RIBOFLAVIN_DII": (-0.068, 1.7, 0.79),
    "SAFFRON_DII": (-0.14, 0.37, 1.78),
    "SATFAT_DII": (0.373, 28.6, 8),
    "SE_DII": (-0.191, 67, 25.1),
    "THIAMIN_DII": (-0.098, 1.7, 0.66),
    "TRANSFAT_DII": (0.229, 3.75, 3.75),
    "TURMERIC_DII": (-0.785, 533.6, 754.3),
    "VITA_DII": (-0.401, 983.9, 518.6),
    "VITC_DII": (-0.424, 118.2, 43.46),
    "VITD_DII": (-0.446, 6.26, 2.21),
    "VITE_DII": (-0.419, 8.73, 1.49),
    "ZN_DII": (-0.313, 9.84, 2.19),
    "TEA_DII": (-0.536, 1.69, 1.53),
    "FLA3OL_DII": (-0.415, 95.8, 85.9),
    "FLAVONES_DII": (-0.616, 1.55, 0.07),
    "FLAVONOLS_DII": (-0.467, 17.7, 6.79),
    "FLAVONONES_DII": (-0.25, 11.7, 3.82),
    "ANTHOC_DII": (-0.131, 18.05, 21.14),
    "ISOFLAVONES_DII": (-0.593, 1.2, 0.2),
    "PEPPER_DII": (-0.131, 10, 7.07),
    "THYME_DII": (-0.102, 0.33, 0.99),
    "ROSEMARY_DII": (-0.013, 1, 15),
}

def _pnorm(z: pd.Series) -> pd.Series:
    """Normal CDF using the error function."""
    return (1.0 + (z / sqrt(2)).apply(erf)) / 2.0


def dii_score(df: pd.DataFrame) -> pd.Series:
    """Compute a simplified Dietary Inflammatory Index.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame containing columns named as in `_DII_DATA`.

    Returns
    -------
    pandas.Series
        Total DII score for each row.
    """
    score = pd.Series(0.0, index=df.index)
    for var, (coef, mean, sd) in _DII_DATA.items():
        if var in df.columns:
            z = (df[var] - mean) / sd
            perc = _pnorm(z) * 2 - 1
            score += perc * coef
    return score
