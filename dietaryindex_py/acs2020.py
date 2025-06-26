import pandas as pd


def _quintile_scores(series: pd.Series, ascending: bool, scores: list) -> pd.Series:
    """Assign quintile-based scores to a pandas Series."""
    quantiles = series.quantile([0.25, 0.5, 0.75]).tolist()
    q1, q2, q3 = quantiles
    if ascending:
        return pd.cut(
            series,
            bins=[-float('inf'), q1, q2, q3, float('inf')],
            labels=scores,
            include_lowest=True,
        ).astype(float)
    else:
        return pd.cut(
            series,
            bins=[-float('inf'), q3, q2, q1, float('inf')],
            labels=scores,
            include_lowest=True,
        ).astype(float)


def acs2020_v1(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the ACS2020 Version 1 dietary index.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame with columns named as in the original R function:
        RESPONDENTID, GENDER, VEG_SERV_ACS2020, VEG_ITEMS_SERV_ACS2020,
        FRT_SERV_ACS2020, FRT_ITEMS_SERV_ACS2020, WGRAIN_SERV_ACS2020,
        REDPROC_MEAT_SERV_ACS2020, HPFRG_RATIO_SERV_ACS2020,
        SSB_FRTJ_SERV_ACS2020

    Returns
    -------
    pandas.DataFrame
        Input data frame with component scores and total score appended.
    """
    required_cols = [
        "RESPONDENTID",
        "GENDER",
        "VEG_SERV_ACS2020",
        "VEG_ITEMS_SERV_ACS2020",
        "FRT_SERV_ACS2020",
        "FRT_ITEMS_SERV_ACS2020",
        "WGRAIN_SERV_ACS2020",
        "REDPROC_MEAT_SERV_ACS2020",
        "HPFRG_RATIO_SERV_ACS2020",
        "SSB_FRTJ_SERV_ACS2020",
    ]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    result = df.copy()

    # apply quintile scoring within gender groups
    grp = result.groupby("GENDER")
    result["ACS2020_VEG"] = grp["VEG_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, True, [0, 0.25, 0.5, 0.75])
    )
    result["ACS2020_VEG_ITEMS"] = grp["VEG_ITEMS_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, True, [0, 0.25, 0.5, 0.75])
    )
    result["ACS2020_FRT"] = grp["FRT_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, True, [0, 0.25, 0.5, 0.75])
    )
    result["ACS2020_FRT_ITEMS"] = grp["FRT_ITEMS_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, True, [0, 0.25, 0.5, 0.75])
    )
    result["ACS2020_WGRAIN"] = grp["WGRAIN_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, True, [0, 1, 2, 3])
    )
    result["ACS2020_REDPROC_MEAT"] = grp["REDPROC_MEAT_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, False, [3, 2, 1, 0])
    )
    result["ACS2020_HPFRG_RATIO"] = grp["HPFRG_RATIO_SERV_ACS2020"].transform(
        lambda x: _quintile_scores(x, False, [1.5, 1.0, 0.5, 0.0])
    )

    # scoring outside gender groups
    result["ACS2020_SSB_FRTJ"] = pd.cut(
        result["SSB_FRTJ_SERV_ACS2020"],
        bins=[-float("inf"), 0, 0.428, 1, float("inf")],
        labels=[1.5, 1, 0.5, 0],
        include_lowest=True,
    ).astype(float)

    comp_cols = [
        "ACS2020_VEG",
        "ACS2020_VEG_ITEMS",
        "ACS2020_FRT",
        "ACS2020_FRT_ITEMS",
        "ACS2020_WGRAIN",
        "ACS2020_SSB_FRTJ",
        "ACS2020_REDPROC_MEAT",
        "ACS2020_HPFRG_RATIO",
    ]
    result["ACS2020_V1_ALL"] = result[comp_cols].sum(axis=1)

    return result[
        [
            "RESPONDENTID",
            "GENDER",
            "ACS2020_V1_ALL",
            "ACS2020_VEG",
            "ACS2020_VEG_ITEMS",
            "ACS2020_FRT",
            "ACS2020_FRT_ITEMS",
            "ACS2020_WGRAIN",
            "ACS2020_REDPROC_MEAT",
            "ACS2020_HPFRG_RATIO",
            "ACS2020_SSB_FRTJ",
        ]
    ]
