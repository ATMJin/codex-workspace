"""簡易加密貨幣網格交易回測工具。

執行 ``python3 grid_backtest.py`` 後依序輸入：
1. CoinGecko 上的幣種 ID
2. 起始與結束日期
3. 網格的上下價格區間與格數
4. 網格類型：``arith`` 表示等差，``geom`` 表示等比
5. (選填) 若無法連線網路，可輸入 CSV 檔路徑做離線測試
"""

import datetime as dt
import numpy as np
import requests
import csv


def get_user_params():
    coin = input("CoinGecko 幣種 ID (例: bitcoin): ").strip() or "bitcoin"
    start = input("開始日期 (YYYY-MM-DD): ").strip() or "2024-01-01"
    end = input("結束日期 (YYYY-MM-DD): ").strip() or "2024-02-01"
    lower = float(input("下界價格: "))
    upper = float(input("上界價格: "))
    grids = int(input("格數: "))
    gtype = input("網格類型 (arith/geom): ").strip().lower() or "arith"
    csv_path = input("離線 CSV 檔路徑 (直接 Enter 表示下載資料): ").strip()
    return coin, start, end, lower, upper, grids, gtype, csv_path


def download_data(coin, start, end):
    """Download daily closing prices from CoinGecko."""
    start_ts = int(dt.datetime.fromisoformat(start).timestamp())
    end_ts = int(dt.datetime.fromisoformat(end).timestamp())
    url = (
        f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
        f"?vs_currency=usd&from={start_ts}&to={end_ts}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    prices = [p[1] for p in data.get("prices", [])]
    return np.array(prices)


def load_csv(path):
    """Load prices from a CSV file with ``date,price`` columns."""
    prices = []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            try:
                prices.append(float(row[1]))
            except (IndexError, ValueError):
                continue
    return np.array(prices)
  
def setup_grid(lower, upper, grids, gtype):
    if gtype.startswith("geom"):
        return np.geomspace(lower, upper, grids + 1)
    return np.linspace(lower, upper, grids + 1)


def backtest(prices, grid):
    cash = 1000.0
    position = 0.0
    last_price = prices[0]

    for price in prices[1:]:
        for level in grid[:-1]:
            if last_price < level <= price and position > 0:
                position -= 1
                cash += level
            elif last_price > level >= price and cash >= level:
                position += 1
                cash -= level
        last_price = price
    return cash + position * prices[-1]


def main():
    params = get_user_params()
    coin, start, end, lower, upper, grids, gtype, csv_path = params

    if csv_path:
        try:
            prices = load_csv(csv_path)
        except Exception as e:
            print("無法讀取 CSV:", e)
            return
    else:
        try:
            prices = download_data(coin, start, end)
        except Exception as e:
            print("下載資料失敗:", e)
            return
    if len(prices) == 0:
        print("沒有取得任何價格資料")
        return
    grid = setup_grid(lower, upper, grids, gtype)
    final_value = backtest(prices, grid)
    print(f"最終資產價值: {final_value:.2f}")
    print("網格價格:", np.round(grid, 2))


if __name__ == "__main__":
    main()
