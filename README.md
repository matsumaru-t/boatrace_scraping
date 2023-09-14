# ボートレースデータ取得ツール

![image](https://github.com/matsumaru-t/boatrace_scraping/assets/40226692/1158b600-5f78-40f3-aac8-b9f14b81ea56)

## 概要
このツールは https://www.boatrace.jp からボートレースデータをスクレイピングするGUIアプリケーションです。

開始日、終了日を指定して検索を実行することでダウンロードができ、以下の構造を持ったjsonファイルとして保存することができます。

```python
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
```

データ分析等にお使いください。

## 使用方法

### リポジトリのクローン
```zsh
git clone https://github.com/matsumaru-t/boatrace_scraping.git
cd boatrace_scraping
```

### パッケージのインストール

Poetryを使用しているので、以下のコマンドでパッケージのインストールができます。

```zsh
poetry install
```

### アプリケーションの起動

パッケージのインストールが完了したら、以下のコマンドでGUIが立ち上がります。

```zsh
poetry run python boatrace_scraping/main.py
```

