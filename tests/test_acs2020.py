import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import pandas as pd
except Exception:  # pragma: no cover - pandas may be missing
    pd = None

from dietaryindex_py import acs2020_v1


def test_acs2020_basic():
    data = {
        "RESPONDENTID": [1, 2, 3, 4, 5, 6],
        "GENDER": [1, 1, 1, 2, 2, 2],
        "VEG_SERV_ACS2020": [1, 2, 3, 1, 2, 3],
        "VEG_ITEMS_SERV_ACS2020": [2, 3, 4, 2, 3, 5],
        "FRT_SERV_ACS2020": [0.5, 1, 1.5, 0.3, 0.7, 1.1],
        "FRT_ITEMS_SERV_ACS2020": [1, 2, 3, 1, 2, 3],
        "WGRAIN_SERV_ACS2020": [0.2, 0.4, 0.6, 0.2, 0.3, 0.8],
        "REDPROC_MEAT_SERV_ACS2020": [1, 0.8, 0.5, 1.2, 0.7, 0.4],
        "HPFRG_RATIO_SERV_ACS2020": [0.2, 0.3, 0.4, 0.25, 0.35, 0.45],
        "SSB_FRTJ_SERV_ACS2020": [0.2, 0.5, 1.2, 0.1, 0.6, 0.9],
    }

    if pd is not None:
        df = pd.DataFrame(data)
        result = acs2020_v1(df)
        assert "ACS2020_V1_ALL" in result.columns
        comp_sum = result[[
            "ACS2020_VEG",
            "ACS2020_VEG_ITEMS",
            "ACS2020_FRT",
            "ACS2020_FRT_ITEMS",
            "ACS2020_WGRAIN",
            "ACS2020_SSB_FRTJ",
            "ACS2020_REDPROC_MEAT",
            "ACS2020_HPFRG_RATIO",
        ]].sum(axis=1)
        assert all(abs(result["ACS2020_V1_ALL"] - comp_sum) < 1e-6)
    else:
        result = acs2020_v1(data)
        assert "ACS2020_V1_ALL" in result
        comp_sum = [
            result["ACS2020_VEG"][i]
            + result["ACS2020_VEG_ITEMS"][i]
            + result["ACS2020_FRT"][i]
            + result["ACS2020_FRT_ITEMS"][i]
            + result["ACS2020_WGRAIN"][i]
            + result["ACS2020_SSB_FRTJ"][i]
            + result["ACS2020_REDPROC_MEAT"][i]
            + result["ACS2020_HPFRG_RATIO"][i]
            for i in range(len(data["RESPONDENTID"]))
        ]
        assert all(
            abs(result["ACS2020_V1_ALL"][i] - comp_sum[i]) < 1e-6
            for i in range(len(comp_sum))
        )
