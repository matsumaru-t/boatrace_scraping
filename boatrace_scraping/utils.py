from datetime import date, timedelta
from typing import Sequence


def to_float(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        return float("nan")


class race_range(Sequence[tuple[str, int, int]]):
    def __init__(self, start: str, end: str) -> None:
        self.start_date = date.fromisoformat(start)
        self.end_date = date.fromisoformat(end)

    def __getitem__(self, index: int) -> tuple[str, int, int]:
        total_days = (self.end_date - self.start_date).days
        if index < 0 or total_days * 24 * 12 <= index:
            raise IndexError
        current_date = self.start_date + timedelta(days=index // (24 * 12))
        stage = (index % (24 * 12)) // 12 + 1
        race = (index % (24 * 12)) % 12 + 1

        return current_date.strftime("%Y%m%d"), stage, race

    def __len__(self) -> int:
        return (self.end_date - self.start_date).days * 24 * 12
