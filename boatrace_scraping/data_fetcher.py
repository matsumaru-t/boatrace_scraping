from dataclasses import asdict
from itertools import combinations, permutations

from bs4 import BeautifulSoup
from models import RaceData, RacerInfo, Ticket
from utils import HTTPClient, to_float

BASE_URL = "https://www.boatrace.jp/owpc/pc/race"


def generate_urls(date: str, stage: int, race: int) -> list[str]:
    query_param = f"rno={race:02}&jcd={stage:02}&hd={date}"
    urls = [
        f"{BASE_URL}/racelist?{query_param}",
        f"{BASE_URL}/odds3t?{query_param}",
        f"{BASE_URL}/odds3f?{query_param}",
        f"{BASE_URL}/odds2tf?{query_param}",
        f"{BASE_URL}/oddsk?{query_param}",
        f"{BASE_URL}/oddstf?{query_param}",
        f"{BASE_URL}/raceresult?{query_param}",
    ]
    return urls


def parse_racelist(html: str) -> list[RacerInfo] | None:
    soup = BeautifulSoup(html, "xml")

    table = soup.select_one(".is-tableFixed__3rdadd table")
    if table is None:
        return None

    trs = table.select("tbody tr:first-child")

    racers = []
    for tr in trs:
        tds = tr.select("td")

        rid, grade = map(
            str.strip, tds[2].select_one("div:nth-of-type(1)").text.split("/")
        )
        rid = int(rid)
        match grade:
            case "A2":
                grade = 3
            case "A1":
                grade = 2
            case "B1":
                grade = 1
            case "B2":
                grade = 0

        age, weight = (
            tds[2]
            .select_one("div:nth-of-type(3)")
            .text.split("\n")[1]
            .strip()
            .split("/")
        )
        age = int(age.replace("歳", ""))
        weight = to_float(weight.replace("kg", ""))

        f_num, l_num, st_mean = map(str.strip, tds[3].text.split("\n")[:3])
        f_num, l_num = int(f_num[1:]), int(l_num[1:])
        st_mean = to_float(st_mean)

        top1_national, top2_national, top3_national = map(
            str.strip, tds[4].text.split("\n")[:3]
        )
        top1_local, top2_local, top3_local = map(str.strip, tds[5].text.split("\n")[:3])
        mortor_no, top2_mortor, top3_mortor = map(
            str.strip, tds[6].text.split("\n")[:3]
        )
        boat_no, top2_boat, top3_boat = map(str.strip, tds[7].text.split("\n")[:3])
        (
            top1_national,
            top2_national,
            top3_national,
            top1_local,
            top2_local,
            top3_local,
            top2_mortor,
            top3_mortor,
            top2_boat,
            top3_boat,
        ) = map(
            to_float,
            [
                top1_national,
                top2_national,
                top3_national,
                top1_local,
                top2_local,
                top3_local,
                top2_mortor,
                top3_mortor,
                top2_boat,
                top3_boat,
            ],
        )
        mortor_no, boat_no = int(mortor_no), int(boat_no)

        racers.append(
            RacerInfo(
                rid=rid,
                grade=grade,
                age=age,
                weight=weight,
                f_num=f_num,
                l_num=l_num,
                st_mean=st_mean,
                top1_national=top1_national,
                top2_national=top2_national,
                top3_national=top3_national,
                top1_local=top1_local,
                top2_local=top2_local,
                top3_local=top3_local,
                mortor_no=mortor_no,
                top2_mortor=top2_mortor,
                top3_mortor=top3_mortor,
                boat_no=boat_no,
                top2_boat=top2_boat,
                top3_boat=top3_boat,
            )
        )

    return racers


def parse_odds(htmls: list[str]) -> dict[str, float] | None:
    odds = {}
    soup = BeautifulSoup(htmls[0], "xml")

    # 3連単
    odds3t = list(map(lambda x: to_float(x.text), soup.select("td.oddsPoint")))
    odds3t = [v for i in range(6) for v in odds3t[i::6]]
    it = iter(odds3t)
    for i, j, k in permutations(range(1, 7), 3):
        try:
            odds[f"(3t){i}-{j}-{k}"] = next(it)
        except StopIteration:
            return None

    # 3連複
    soup = BeautifulSoup(htmls[1], "xml")
    odds3f = list(map(lambda x: to_float(x.text), soup.select("td.oddsPoint")))
    it = iter(odds3f)
    for j, k in combinations(range(2, 7), 2):
        for i in range(1, j):
            try:
                odds[f"(3f){i}={j}={k}"] = next(it)
            except StopIteration:
                return None

    # 2連単
    soup = BeautifulSoup(htmls[2], "xml")
    odds2tf = list(map(lambda x: to_float(x.text), soup.select("td.oddsPoint")))
    it = iter(odds2tf)
    for j in range(1, 6):
        for i in range(1, 7):
            try:
                odds[f"(2t){i}-{j+(i<=j)}"] = next(it)
            except StopIteration:
                return None

    # 2連複
    for j in range(2, 7):
        for i in range(1, j):
            try:
                odds[f"(2f){i}={j}"] = next(it)
            except StopIteration:
                return None

    # 拡連複
    soup = BeautifulSoup(htmls[3], "xml")
    oddsk = list(
        map(lambda x: to_float(x.text.split("-")[0]), soup.select("td.oddsPoint"))
    )
    it = iter(oddsk)
    for j in range(2, 7):
        for i in range(1, j):
            try:
                odds[f"(k){i}={j}"] = next(it)
            except StopIteration:
                return None

    # 単勝
    soup = BeautifulSoup(htmls[4], "xml")
    oddstf = list(
        map(lambda x: to_float(x.text.split("-")[0]), soup.select("td.oddsPoint"))
    )
    it = iter(oddstf)
    for i in range(1, 7):
        try:
            odds[f"(t){i}"] = next(it)
        except StopIteration:
            return None

    # 複勝
    for i in range(1, 7):
        try:
            odds[f"(f){i}"] = next(it)
        except StopIteration:
            return None

    return odds


def parse_raceresult(html: str) -> dict[str, float] | None:
    soup = BeautifulSoup(html, "xml")

    try:
        table = soup.find(string="勝式").find_parent("table")
    except AttributeError:
        return None

    payout = {}
    for i, j, k in permutations(range(1, 7), 3):
        payout[f"(3t){i}-{j}-{k}"] = 0.0
    for i, j, k in combinations(range(1, 7), 3):
        payout[f"(3f){i}={j}={k}"] = 0.0
    for i, j in permutations(range(1, 7), 2):
        payout[f"(2t){i}-{j}"] = 0.0
    for i, j in combinations(range(1, 7), 2):
        payout[f"(2f){i}={j}"] = 0.0
    for i, j in combinations(range(1, 7), 2):
        payout[f"(k){i}={j}"] = 0.0
    for i in range(1, 7):
        payout[f"(t){i}"] = 0.0
    for i in range(1, 7):
        payout[f"(f){i}"] = 0.0
    numsets = table.select(".numberSet1")

    for el in numsets:
        numset = el.text.strip()
        if not numset:
            continue
        val = to_float(el.parent.find_next_sibling("td").text.replace(",", ""))
        match el.find_parent("tbody").select_one("tr > td").text:
            case "3連単":
                payout[f"(3t){numset}"] = val
            case "3連複":
                payout[f"(3f){numset}"] = val
            case "2連単":
                payout[f"(2t){numset}"] = val
            case "2連複":
                payout[f"(2f){numset}"] = val
            case "拡連複":
                payout[f"(k){numset}"] = val
            case "単勝":
                payout[f"(t){numset}"] = val
            case "複勝":
                payout[f"(f){numset}"] = val

    return payout


async def fetch_racedata(
    client: HTTPClient,
    date: str,
    stage: int,
    race: int,
) -> dict | None:
    urls = generate_urls(date, stage, race)

    racelist_html, *odds_html, raceresult_html = await client.fetch_all(urls)

    racers = parse_racelist(racelist_html)
    odds_dict = parse_odds(odds_html)
    payout_dict = parse_raceresult(raceresult_html)

    if racers is None or odds_dict is None or payout_dict is None:
        return None

    tickets = [
        Ticket(name=name, odds=odds_dict[name], payout=payout_dict[name])
        for name in odds_dict.keys()
    ]

    return asdict(
        RaceData(
            date=date,
            stage=stage,
            race=race,
            racers=racers,
            tickets=tickets,
        )
    )
