import datetime as dt
import json
import numpy as np
import requests


def get_user_params():
    coin = input("Coin ID on CoinGecko (e.g. bitcoin): ").strip() or "bitcoin"
    start = input("Start date (YYYY-MM-DD): ").strip() or "2024-01-01"
    end = input("End date (YYYY-MM-DD): ").strip() or "2024-02-01"
    lower = float(input("Lower price bound: "))
    upper = float(input("Upper price bound: "))
    grids = int(input("Number of grids: "))
    gtype = input("Grid type ('arith' or 'geom'): ").strip().lower() or "arith"
    return coin, start, end, lower, upper, grids, gtype


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
    coin, start, end, lower, upper, grids, gtype = params
    try:
        prices = download_data(coin, start, end)
    except Exception as e:
        print("Failed to download data:", e)
        return
    if len(prices) == 0:
        print("No data downloaded.")
        return
    grid = setup_grid(lower, upper, grids, gtype)
    final_value = backtest(prices, grid)
    print(f"Final portfolio value: {final_value:.2f}")
    print("Grid levels:", np.round(grid, 2))


if __name__ == "__main__":
    main()
