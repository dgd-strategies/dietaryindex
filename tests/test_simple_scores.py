import pandas as pd
from dietaryindex_py import dii_score, mind_score, hei_score


def test_dii_score_basic():
    df = pd.DataFrame({
        "ALCOHOL_DII": [10, 20],
        "VITB12_DII": [5, 4],
    })
    score = dii_score(df)
    assert len(score) == 2
    assert score.notna().all()


def test_mind_score_basic():
    df = pd.DataFrame({
        "GREEN_LEAFY": [1, 0],
        "RED_MEAT": [0, 1],
    })
    result = mind_score(df)
    assert result.iloc[0] > result.iloc[1]


def test_hei_score_basic():
    df = pd.DataFrame({
        "TOTAL_FRT": [5, 1],
        "WHOLE_FRT": [5, 1],
    })
    result = hei_score(df)
    assert result.iloc[0] >= result.iloc[1]
