import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dietaryindex_py import acs2020_v1, acs2020_v2, ahei


def test_acs2020_basic():
    data = [
        {
            "RESPONDENTID": i,
            "GENDER": 1 if i <= 3 else 2,
            "VEG_SERV_ACS2020": v,
            "VEG_ITEMS_SERV_ACS2020": vi,
            "FRT_SERV_ACS2020": f,
            "FRT_ITEMS_SERV_ACS2020": fi,
            "WGRAIN_SERV_ACS2020": w,
            "REDPROC_MEAT_SERV_ACS2020": r,
            "HPFRG_RATIO_SERV_ACS2020": h,
            "SSB_FRTJ_SERV_ACS2020": s,
        }
        for i, (v, vi, f, fi, w, r, h, s) in enumerate(
            [
                (1, 2, 0.5, 1, 0.2, 1, 0.2, 0.2),
                (2, 3, 1, 2, 0.4, 0.8, 0.3, 0.5),
                (3, 4, 1.5, 3, 0.6, 0.5, 0.4, 1.2),
                (1, 2, 0.3, 1, 0.2, 1.2, 0.25, 0.1),
                (2, 3, 0.7, 2, 0.3, 0.7, 0.35, 0.6),
                (3, 5, 1.1, 3, 0.8, 0.4, 0.45, 0.9),
            ],
            start=1,
        )
    ]

    result = acs2020_v1(data)
    assert isinstance(result, list)
    for row in result:
        comp_sum = (
            row["ACS2020_VEG"]
            + row["ACS2020_VEG_ITEMS"]
            + row["ACS2020_FRT"]
            + row["ACS2020_FRT_ITEMS"]
            + row["ACS2020_WGRAIN"]
            + row["ACS2020_SSB_FRTJ"]
            + row["ACS2020_REDPROC_MEAT"]
            + row["ACS2020_HPFRG_RATIO"]
        )
        assert abs(row["ACS2020_V1_ALL"] - comp_sum) < 1e-6


def test_ssb_boundary():
    df = [
        {
            "RESPONDENTID": 1,
            "GENDER": 1,
            "VEG_SERV_ACS2020": 1,
            "VEG_ITEMS_SERV_ACS2020": 1,
            "FRT_SERV_ACS2020": 1,
            "FRT_ITEMS_SERV_ACS2020": 1,
            "WGRAIN_SERV_ACS2020": 1,
            "REDPROC_MEAT_SERV_ACS2020": 1,
            "HPFRG_RATIO_SERV_ACS2020": 1,
            "SSB_FRTJ_SERV_ACS2020": 0.428,
        }
    ]

    out = acs2020_v1(df)
    assert out[0]["ACS2020_SSB_FRTJ"] == 0.5


def test_acs2020_v2_basic():
    df = [
        {
            "RESPONDENTID": 1,
            "GENDER": 1,
            "TOTALKCAL_ACS2020": 2000,
            "VEG_SERV_ACS2020": 1,
            "VEG_ITEMS_SERV_ACS2020": 2,
            "FRT_SERV_ACS2020": 1,
            "FRT_ITEMS_SERV_ACS2020": 1,
            "WGRAIN_SERV_ACS2020": 0.5,
            "REDPROC_MEAT_SERV_ACS2020": 1,
            "HPFRG_SERV_ACS2020": 2,
            "SSB_FRTJ_SERV_ACS2020": 0.2,
        },
        {
            "RESPONDENTID": 2,
            "GENDER": 2,
            "TOTALKCAL_ACS2020": 1800,
            "VEG_SERV_ACS2020": 2,
            "VEG_ITEMS_SERV_ACS2020": 3,
            "FRT_SERV_ACS2020": 1.5,
            "FRT_ITEMS_SERV_ACS2020": 2,
            "WGRAIN_SERV_ACS2020": 0.7,
            "REDPROC_MEAT_SERV_ACS2020": 0.6,
            "HPFRG_SERV_ACS2020": 1.5,
            "SSB_FRTJ_SERV_ACS2020": 0.5,
        },
    ]

    res = acs2020_v2(df)
    assert isinstance(res, list)
    assert "ACS2020_V2_ALL" in res[0]


def test_ahei_basic():
    df = [
        {
            "RESPONDENTID": 1,
            "GENDER": 2,
            "TOTALKCAL_AHEI": 2000,
            "VEG_SERV_AHEI": 4,
            "FRT_SERV_AHEI": 3,
            "WGRAIN_SERV_AHEI": 80,
            "NUTSLEG_SERV_AHEI": 0.8,
            "N3FAT_SERV_AHEI": 200,
            "PUFA_SERV_AHEI": 8,
            "SSB_FRTJ_SERV_AHEI": 0.5,
            "REDPROC_MEAT_SERV_AHEI": 1,
            "TRANS_SERV_AHEI": 1,
            "SODIUM_SERV_AHEI": 1000,
            "ALCOHOL_SERV_AHEI": 1,
        }
    ]

    res = ahei(df)
    assert isinstance(res, list)
    assert "AHEI_ALL" in res[0]


def test_missing_column_v1():
    data = [{"RESPONDENTID": 1, "GENDER": 1}]
    with pytest.raises(KeyError):
        acs2020_v1(data)


def test_missing_column_v2():
    data = [{"RESPONDENTID": 1, "GENDER": 1, "TOTALKCAL_ACS2020": 2000}]
    with pytest.raises(KeyError):
        acs2020_v2(data)


def test_missing_column_ahei():
    data = [{"RESPONDENTID": 1, "GENDER": 1, "TOTALKCAL_AHEI": 2000}]
    with pytest.raises(KeyError):
        ahei(data)


def test_dataframe_input_roundtrip():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame([
        {
            "RESPONDENTID": 1,
            "GENDER": 1,
            "VEG_SERV_ACS2020": 1,
            "VEG_ITEMS_SERV_ACS2020": 1,
            "FRT_SERV_ACS2020": 1,
            "FRT_ITEMS_SERV_ACS2020": 1,
            "WGRAIN_SERV_ACS2020": 1,
            "REDPROC_MEAT_SERV_ACS2020": 1,
            "HPFRG_RATIO_SERV_ACS2020": 1,
            "SSB_FRTJ_SERV_ACS2020": 0.5,
        }
    ])
    out_df = acs2020_v1(df)
    assert isinstance(out_df, pd.DataFrame)
    out_dict = acs2020_v1(df.to_dict("records"))[0]
    for col in out_dict:
        assert abs(out_df.at[0, col] - out_dict[col]) < 1e-6
