from dataclasses import dataclass


@dataclass
class RacerInfo:
    rid: int
    grade: int
    age: int
    weight: float
    f_num: int
    l_num: int
    st_mean: float
    top1_national: float
    top2_national: float
    top3_national: float
    top1_local: float
    top2_local: float
    top3_local: float
    mortor_no: int
    top2_mortor: float
    top3_mortor: float
    boat_no: int
    top2_boat: float
    top3_boat: float


@dataclass
class Ticket:
    name: str
    odds: float
    payout: float


@dataclass
class RaceData:
    date: str
    stage: int
    race: int
    racers: list[RacerInfo]
    tickets: list[Ticket]
