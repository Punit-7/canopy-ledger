# tests/test_frames.py
import pandas as pd

from ledger.frames import districts, tidy


def test_gid_parsing():
    b = pd.DataFrame(
        {
            "gid_0": ["IND"] * 2,
            "gid_1": ["IND.10_1", "IND.10_1"],
            "name_1": ["Jharkhand"] * 2,
            "gid_2": ["IND.10.3_1", None],
            "name_2": ["Garhwa", None],
            "engtype_2": ["District", None],
            "adm_level": ["2", "1"],
            "gfw_area__ha": [1.0, 2.0],
        }
    )
    d = districts(b)
    assert len(d) == 1
    assert (d.loc[0, "adm1"], d.loc[0, "adm2"], d.loc[0, "district"]) == (10, 3, "Garhwa")


def test_booleans_and_flags():
    df = tidy(
        pd.DataFrame(
            {
                "is__umd_regional_primary_forest_2001": ["true", "False", None],
                "wdpa_protected_areas__iucn_cat": ["II", None, None],
            }
        )
    )
    assert df["is_primary"].tolist() == [True, False, False]
    assert df["is_protected"].tolist() == [True, False, False]
