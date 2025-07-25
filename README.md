# codex-workspace

這個專案提供一個簡單的 Python 程式，用來模擬加密貨幣的網格交易策略。

## grid_backtest.py

程式會向 CoinGecko 下載歷史價格後依照等差或等比方式建立網格，並進行回測。

### 使用方式

1. 安裝依賴（需要 Python 3）：
   ```bash
   pip install requests numpy
   ```

2. 執行腳本並依提示輸入各項參數：
   ```bash
   python3 grid_backtest.py
   ```

   需輸入的項目包括：
   - CoinGecko 幣種 ID（例如 `bitcoin`）
   - 起始與結束日期（`YYYY-MM-DD`）
   - 網格上下界價格與格數
   - 網格類型 `arith`（等差）或 `geom`（等比）
   - 若無法連線，可額外提供含 `date,price` 的 CSV 檔做離線測試

程式會下載或讀取價格資料，執行回測並輸出最終資產價值與網格價格。

若因網路限制無法下載資料，請準備符合格式的 CSV 檔（範例檔 `sample_btc.csv` 已隨附）。
