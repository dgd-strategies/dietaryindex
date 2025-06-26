"""ACS2020 Version 2 scoring without external dependencies."""

from typing import Iterable, List, Dict, Any
import statistics

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:  # pragma: no cover - pandas may not be installed
    HAVE_PANDAS = False

from .acs2020 import _quantiles, _score_value, _ssb_score


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


def _acs2020_v2_rows(data: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [dict(r) for r in data]
    required = [
        "RESPONDENTID",
        "GENDER",
        "TOTALKCAL_ACS2020",
        "VEG_SERV_ACS2020",
        "VEG_ITEMS_SERV_ACS2020",
        "FRT_SERV_ACS2020",
        "FRT_ITEMS_SERV_ACS2020",
        "WGRAIN_SERV_ACS2020",
        "REDPROC_MEAT_SERV_ACS2020",
        "HPFRG_SERV_ACS2020",
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

    groups: Dict[Any, List[int]] = {}
    for idx, row in enumerate(rows):
        groups.setdefault(row["GENDER"], []).append(idx)
    for indices in groups.values():
        vals = [rows[i]["HPFRG_SERV_ACS2020"] / (rows[i]["TOTALKCAL_ACS2020"] / 1000) for i in indices]
        q1, q2, q3 = _quantiles(vals)
        for idx, val in zip(indices, vals):
            rows[idx]["ACS2020_HPFRG"] = float(_score_value(val, q1, q2, q3, False, [0, 0.5, 1.0, 1.5]))

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
            row["ACS2020_HPFRG"],
        ]
        row["ACS2020_V2_ALL"] = sum(comps)
    return rows


def acs2020_v2(data: Any):
    """Compute the ACS2020 Version 2 index (servings per kcal)."""
    if HAVE_PANDAS and isinstance(data, pd.DataFrame):
        rows = _acs2020_v2_rows(data.to_dict("records"))
        return pd.DataFrame(rows)
    return _acs2020_v2_rows(data)
