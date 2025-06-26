"""Alternative Healthy Eating Index implemented with only the Python standard library."""

from typing import Iterable, List, Dict, Any
import statistics

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:  # pragma: no cover - pandas may not be installed
    HAVE_PANDAS = False


def _score_linear(val: float, min_serv: float, max_serv: float, min_score: float, max_score: float) -> float:
    if val >= max_serv:
        return max_score
    if val <= min_serv:
        return min_score
    return min_score + (val - min_serv) * (max_score - min_score) / (max_serv - min_serv)


def _quantiles_list(values: List[float], probs: List[float]) -> List[float]:
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    result = []
    for p in probs:
        k = p * (n - 1)
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            result.append(sorted_vals[f])
        else:
            d = k - f
            result.append(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * d)
    return result


def _ahei_rows(data: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [dict(r) for r in data]
    required = [
        "RESPONDENTID",
        "GENDER",
        "TOTALKCAL_AHEI",
        "VEG_SERV_AHEI",
        "FRT_SERV_AHEI",
        "WGRAIN_SERV_AHEI",
        "NUTSLEG_SERV_AHEI",
        "N3FAT_SERV_AHEI",
        "PUFA_SERV_AHEI",
        "SSB_FRTJ_SERV_AHEI",
        "REDPROC_MEAT_SERV_AHEI",
        "TRANS_SERV_AHEI",
        "SODIUM_SERV_AHEI",
        "ALCOHOL_SERV_AHEI",
    ]
    for r in rows:
        for c in required:
            if c not in r:
                raise KeyError(f"Missing required column: {c}")

    for r in rows:
        r["SODIUM_SERV_AHEI"] = r["SODIUM_SERV_AHEI"] / (r["TOTALKCAL_AHEI"] / 2000)

    sodium_vals = [r["SODIUM_SERV_AHEI"] for r in rows]
    deciles = _quantiles_list(sodium_vals, [i / 11 for i in range(12)])

    for r in rows:
        r["AHEI_VEG"] = _score_linear(r["VEG_SERV_AHEI"], 0, 5, 0, 10)
        r["AHEI_FRT"] = _score_linear(r["FRT_SERV_AHEI"], 0, 4, 0, 10)
        max_wg = 75 if r["GENDER"] == 2 else 90
        r["AHEI_WGRAIN"] = _score_linear(r["WGRAIN_SERV_AHEI"], 0, max_wg, 0, 10)
        r["AHEI_NUTSLEG"] = _score_linear(r["NUTSLEG_SERV_AHEI"], 0, 1, 0, 10)
        r["AHEI_N3FAT"] = _score_linear(r["N3FAT_SERV_AHEI"], 0, 250, 0, 10)
        r["AHEI_PUFA"] = _score_linear(r["PUFA_SERV_AHEI"], 2, 10, 0, 10)
        r["AHEI_SSB_FRTJ"] = _score_linear(r["SSB_FRTJ_SERV_AHEI"], 1, 0, 0, 10)
        r["AHEI_REDPROC_MEAT"] = _score_linear(r["REDPROC_MEAT_SERV_AHEI"], 1.5, 0, 0, 10)
        r["AHEI_TRANS"] = _score_linear(r["TRANS_SERV_AHEI"], 4, 0.5, 0, 10)

        # sodium decile score
        val = r["SODIUM_SERV_AHEI"]
        for i in range(11):
            lower = deciles[i]
            upper = deciles[i + 1]
            if val <= upper or i == 10:
                r["AHEI_SODIUM"] = float(i)
                break

        g = r["GENDER"]
        alc = r["ALCOHOL_SERV_AHEI"]
        if g == 2:
            if alc >= 2.5:
                r["AHEI_ALCOHOL"] = 0.0
            elif alc > 1.5:
                r["AHEI_ALCOHOL"] = (alc - 2.5) * 10 / (1.5 - 2.5)
            elif 0.5 <= alc <= 1.5:
                r["AHEI_ALCOHOL"] = 10.0
            elif alc > 0.125:
                r["AHEI_ALCOHOL"] = (alc - 0) * 10 / (0.5 - 0)
            else:
                r["AHEI_ALCOHOL"] = 2.5
        else:
            if alc >= 3.5:
                r["AHEI_ALCOHOL"] = 0.0
            elif alc > 2.0:
                r["AHEI_ALCOHOL"] = (alc - 3.5) * 10 / (2.0 - 3.5)
            elif 0.5 <= alc <= 2.0:
                r["AHEI_ALCOHOL"] = 10.0
            elif alc > 0.125:
                r["AHEI_ALCOHOL"] = (alc - 0) * 10 / (0.5 - 0)
            else:
                r["AHEI_ALCOHOL"] = 2.5

        comps = [
            r["AHEI_VEG"],
            r["AHEI_FRT"],
            r["AHEI_WGRAIN"],
            r["AHEI_NUTSLEG"],
            r["AHEI_N3FAT"],
            r["AHEI_PUFA"],
            r["AHEI_SSB_FRTJ"],
            r["AHEI_REDPROC_MEAT"],
            r["AHEI_TRANS"],
            r["AHEI_SODIUM"],
            r["AHEI_ALCOHOL"],
        ]
        r["AHEI_ALL"] = sum(comps)
        r["AHEI_NOETOH"] = r["AHEI_ALL"] - r["AHEI_ALCOHOL"]

    return rows


def ahei(data: Any):
    """Compute the AHEI for a pandas DataFrame or iterable of dictionaries."""
    if HAVE_PANDAS and isinstance(data, pd.DataFrame):
        rows = _ahei_rows(data.to_dict("records"))
        return pd.DataFrame(rows)
    return _ahei_rows(data)
