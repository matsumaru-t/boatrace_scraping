import asyncio
from datetime import date, timedelta
from typing import Sequence

import aiohttp


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


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession, parallel: int = 10) -> None:
        self.session = session
        self.semaphore = asyncio.Semaphore(parallel)

    async def fetch(self, url: str) -> str | None:
        try:
            async with self.semaphore:
                async with self.session.get(url) as response:
                    return await response.text()
        except aiohttp.ClientError:
            return None

    async def fetch_all(self, urls: list[str]) -> list[str | None]:
        return await asyncio.gather(*[self.fetch(url) for url in urls])


async def main():
    async with aiohttp.ClientSession() as session:
        client = HTTPClient(session)
        htmls = await client.fetch_all(["https://google.com"] * 10)
        print(*[type(html) for html in htmls])


if __name__ == "__main__":
    asyncio.run(main())
