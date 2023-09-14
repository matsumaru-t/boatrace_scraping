from math import isclose, isnan

from boatrace_scraping.utils import to_float, race_range


def test_to_float():
    assert isclose(to_float("1.234"), 1.234)
    assert to_float("5") == 5
    assert isnan(to_float("-"))


def test_race_range():
    assert race_range("20210701", "20210703")[0] == ("20210701", 1, 1)
    assert len(race_range("20210701", "20210703")) == 2 * 24 * 12
