from types import SimpleNamespace

import pytest

from ledger.fixtures import make_frames
from ledger.frames import districts, tidy


@pytest.fixture(scope="session")
def frames():
    raw = make_frames(last_year=2025)
    return {
        "chg": tidy(raw["tcl_change"]),
        "summ": tidy(raw["tcl_summary"]),
        "viirs": tidy(raw["viirs_weekly"]),
        "names": districts(raw["boundaries"]),
    }


@pytest.fixture
def settings():
    return SimpleNamespace(expect_max_loss_year=2025, canopy_threshold=30)
