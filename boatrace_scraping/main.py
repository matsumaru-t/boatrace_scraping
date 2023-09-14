import asyncio
import json

import aiohttp
import flet as ft
from data_fetcher import fetch_racedata
from utils import race_range


async def main(page: ft.Page) -> None:
    page.scroll = "auto"
    page.title = "ボートレースデータ取得ツール"

    title_text = ft.Text("ボートレースデータ取得")

    start_textbox = ft.TextField(label="開始日", value="20210701")
    end_textbox = ft.TextField(label="終了日", value="20210703")

    pb = ft.ProgressBar(width=400, value=0)
    result_container = ft.Container()

    async def search(e) -> None:
        start, end = start_textbox.value, end_textbox.value
        pb.value = 0

        async def create_task(session, date, stage, race):
            task = await fetch_racedata(session, date, stage, race)
            pb.value += 1 / len(race_range(start, end))
            await pb.update_async()
            return task

        timeout = aiohttp.ClientTimeout(total=60 * 60)
        semaphore = asyncio.Semaphore(100)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with semaphore:
                tasks = [
                    create_task(session, date, stage, race)
                    for date, stage, race in race_range(start, end)
                ]
                result = await asyncio.gather(*tasks)

        result = [r for r in result if r is not None]

        result_container.content = ft.Text(f"{len(result)}件のデータを取得しました。")

        def save(e: ft.FilePickerResultEvent):
            if e.path is None:
                return
            if not e.path.endswith(".json"):
                e.path += ".json"
            with open(e.path, "w") as f:
                json.dump(result, f)

        picker = ft.FilePicker(on_result=save)
        page.overlay.append(picker)

        await page.update_async()
        await picker.save_file_async(
            dialog_title="保存先を選択してください", file_name="racedata.json"
        )

    search_button = ft.ElevatedButton("検索", icon="search", on_click=search)

    await page.add_async(
        ft.Column(
            controls=[
                title_text,
                ft.Row(
                    controls=[
                        start_textbox,
                        end_textbox,
                    ]
                ),
                ft.Row(
                    controls=[
                        search_button,
                        pb,
                    ]
                ),
                result_container,
            ],
        ),
    )


if __name__ == "__main__":
    ft.app(main)
