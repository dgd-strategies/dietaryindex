"""ACS2020 dietary index utilities."""

try:
    import pandas as pd
except Exception:  # pragma: no cover - pandas may not be installed
    pd = None

import statistics


def _quartiles(values):
    """Return the first, second, and third quartiles of ``values``."""
    if not values:
        return 0.0, 0.0, 0.0
    # ``statistics.quantiles`` with ``method='inclusive'`` matches pandas default
    q = statistics.quantiles(values, n=4, method="inclusive")
    q1 = q[0]
    q2 = statistics.median(values)
    q3 = q[2]
    return q1, q2, q3


def _cut(value, bins, scores):
    """Simple implementation of ``pandas.cut`` for monotonically increasing bins."""
    for upper, score in zip(bins[1:], scores):
        if value <= upper:
            return float(score)
    return float(scores[-1])


def _quintile_scores_list(values, ascending, scores):
    """Assign quintile-based scores for a list of numbers."""
    q1, q2, q3 = _quartiles(sorted(values))
    result = []
    for val in values:
        if ascending:
            result.append(_cut(val, [-float("inf"), q1, q2, q3, float("inf")], scores))
        else:
            result.append(_cut(val, [-float("inf"), q3, q2, q1, float("inf")], scores))
    return result


def _quintile_scores(series, ascending: bool, scores: list):
    """Assign quintile-based scores to a pandas Series or list."""
    if pd is not None and hasattr(series, "quantile"):
        quantiles = series.quantile([0.25, 0.5, 0.75]).tolist()
        q1, q2, q3 = quantiles
        bins = [-float("inf"), q1, q2, q3, float("inf")]
        if not ascending:
            bins = [-float("inf"), q3, q2, q1, float("inf")]
        return pd.cut(series, bins=bins, labels=scores, include_lowest=True).astype(float)
    else:
        return _quintile_scores_list(series, ascending, scores)


def acs2020_v1(df):
    """Compute the ACS2020 Version 1 dietary index.

    Parameters
    ----------
    df : pandas.DataFrame or mapping
        Either a pandas ``DataFrame`` with columns named as in the original R function or
        a mapping of column names to sequences when ``pandas`` is unavailable:
        RESPONDENTID, GENDER, VEG_SERV_ACS2020, VEG_ITEMS_SERV_ACS2020,
        FRT_SERV_ACS2020, FRT_ITEMS_SERV_ACS2020, WGRAIN_SERV_ACS2020,
        REDPROC_MEAT_SERV_ACS2020, HPFRG_RATIO_SERV_ACS2020,
        SSB_FRTJ_SERV_ACS2020

    Returns
    -------
    pandas.DataFrame or dict
        Input with component scores and total score appended. If ``pandas`` is not
        installed, a dictionary mapping column names to lists is returned.
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
    if pd is not None and hasattr(df, "groupby"):
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
    else:
        # expect mapping of columns to lists
        for col in required_cols:
            if col not in df:
                raise KeyError(f"Missing required column: {col}")

        n = len(df["RESPONDENTID"])
        result = {k: list(df[k]) for k in required_cols}

        # build gender groups
        groups = {}
        for i, g in enumerate(df["GENDER"]):
            groups.setdefault(g, []).append(i)

        def assign(col, asc, scores):
            scores_col = [0.0] * n
            for g, idxs in groups.items():
                values = [df[col][j] for j in idxs]
                vals_scores = _quintile_scores_list(values, asc, scores)
                for pos, j in enumerate(idxs):
                    scores_col[j] = vals_scores[pos]
            return scores_col

        result["ACS2020_VEG"] = assign("VEG_SERV_ACS2020", True, [0, 0.25, 0.5, 0.75])
        result["ACS2020_VEG_ITEMS"] = assign(
            "VEG_ITEMS_SERV_ACS2020", True, [0, 0.25, 0.5, 0.75]
        )
        result["ACS2020_FRT"] = assign("FRT_SERV_ACS2020", True, [0, 0.25, 0.5, 0.75])
        result["ACS2020_FRT_ITEMS"] = assign(
            "FRT_ITEMS_SERV_ACS2020", True, [0, 0.25, 0.5, 0.75]
        )
        result["ACS2020_WGRAIN"] = assign("WGRAIN_SERV_ACS2020", True, [0, 1, 2, 3])
        result["ACS2020_REDPROC_MEAT"] = assign(
            "REDPROC_MEAT_SERV_ACS2020", False, [3, 2, 1, 0]
        )
        result["ACS2020_HPFRG_RATIO"] = assign(
            "HPFRG_RATIO_SERV_ACS2020", False, [1.5, 1.0, 0.5, 0.0]
        )

        # outside gender groups
        result["ACS2020_SSB_FRTJ"] = [
            _cut(v, [-float("inf"), 0, 0.428, 1, float("inf")], [1.5, 1, 0.5, 0])
            for v in df["SSB_FRTJ_SERV_ACS2020"]
        ]

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
        result["ACS2020_V1_ALL"] = [
            sum(result[c][i] for c in comp_cols) for i in range(n)
        ]

        return result
