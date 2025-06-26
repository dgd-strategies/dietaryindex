"""Pure Python implementation of ACS2020 scoring."""

from typing import Iterable, List, Dict, Any
import statistics

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:  # pragma: no cover - pandas may not be installed
    HAVE_PANDAS = False


def _quantiles(values: List[float]) -> List[float]:
    """Return the 25th, 50th and 75th percentiles for the provided values."""
    if not values:
        return [0.0, 0.0, 0.0]
    sorted_vals = sorted(values)
    if len(sorted_vals) < 2:
        val = sorted_vals[0]
        return [val, val, val]
    return statistics.quantiles(sorted_vals, n=4)


def _score_value(val: float, q1: float, q2: float, q3: float, ascending: bool, scores: List[float]) -> float:
    if ascending:
        if val <= q1:
            return scores[0]
        elif val <= q2:
            return scores[1]
        elif val <= q3:
            return scores[2]
        else:
            return scores[3]
    else:
        if val <= q3:
            return scores[3]
        elif val <= q2:
            return scores[2]
        elif val <= q1:
            return scores[1]
        else:
            return scores[0]


def _apply_quintile(rows: List[Dict[str, Any]], group_key: str, value_key: str, out_key: str,
                    ascending: bool, scores: List[float]) -> None:
    groups: Dict[Any, List[int]] = {}
    for idx, row in enumerate(rows):
        groups.setdefault(row[group_key], []).append(idx)
    for indices in groups.values():
        vals = [rows[i][value_key] for i in indices]
        q1, q2, q3 = _quantiles(vals)
        for i in indices:
            rows[i][out_key] = float(_score_value(rows[i][value_key], q1, q2, q3, ascending, scores))


def _ssb_score(val: float) -> float:
    if val <= 0:
        return 1.5
    if val < 0.428:
        return 1.0
    if val < 1:
        return 0.5
    return 0.0


def _acs2020_v1_rows(data: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [dict(row) for row in data]
    required = [
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
    for r in rows:
        for c in required:
            if c not in r:
                raise KeyError(f"Missing required column: {c}")

    _apply_quintile(rows, "GENDER", "VEG_SERV_ACS2020", "ACS2020_VEG", True, [0, 0.25, 0.5, 0.75])
    _apply_quintile(rows, "GENDER", "VEG_ITEMS_SERV_ACS2020", "ACS2020_VEG_ITEMS", True, [0, 0.25, 0.5, 0.75])
    _apply_quintile(rows, "GENDER", "FRT_SERV_ACS2020", "ACS2020_FRT", True, [0, 0.25, 0.5, 0.75])
    _apply_quintile(rows, "GENDER", "FRT_ITEMS_SERV_ACS2020", "ACS2020_FRT_ITEMS", True, [0, 0.25, 0.5, 0.75])
    _apply_quintile(rows, "GENDER", "WGRAIN_SERV_ACS2020", "ACS2020_WGRAIN", True, [0, 1, 2, 3])
    _apply_quintile(rows, "GENDER", "REDPROC_MEAT_SERV_ACS2020", "ACS2020_REDPROC_MEAT", False, [3, 2, 1, 0])
    _apply_quintile(rows, "GENDER", "HPFRG_RATIO_SERV_ACS2020", "ACS2020_HPFRG_RATIO", False, [1.5, 1.0, 0.5, 0.0])

    for row in rows:
        row["ACS2020_SSB_FRTJ"] = _ssb_score(row["SSB_FRTJ_SERV_ACS2020"])
        comps = [
            row["ACS2020_VEG"],
            row["ACS2020_VEG_ITEMS"],
            row["ACS2020_FRT"],
            row["ACS2020_FRT_ITEMS"],
            row["ACS2020_WGRAIN"],
            row["ACS2020_SSB_FRTJ"],
            row["ACS2020_REDPROC_MEAT"],
            row["ACS2020_HPFRG_RATIO"],
        ]
        row["ACS2020_V1_ALL"] = sum(comps)
    return rows


def acs2020_v1(data: Any):
    """Compute the ACS2020 Version 1 index.

    Accepts either a pandas DataFrame or an iterable of dictionaries and returns
    the same type with additional score columns.
    """
    if HAVE_PANDAS and isinstance(data, pd.DataFrame):
        rows = _acs2020_v1_rows(data.to_dict("records"))
        return pd.DataFrame(rows)
    return _acs2020_v1_rows(data)
