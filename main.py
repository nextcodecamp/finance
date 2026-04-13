from fastapi import FastAPI, HTTPException, Query
import yfinance as yf
import pandas as pd

app = FastAPI(title="Stock Data API")


@app.get("/")
def root():
    return {"message": "Stock API is running"}


@app.get("/stock/{symbol}")
def get_stock_info(symbol: str):
    """
    ดึงข้อมูลพื้นฐานและราคาล่าสุดของหุ้น
    เช่น /stock/AAPL
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # บางครั้ง yfinance อาจคืนข้อมูลไม่ครบ
        if not info or "symbol" not in info:
            raise HTTPException(status_code=404, detail="Stock not found")

        data = {
            "symbol": info.get("symbol"),
            "shortName": info.get("shortName"),
            "longName": info.get("longName"),
            "currency": info.get("currency"),
            "exchange": info.get("exchange"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currentPrice": info.get("currentPrice"),
            "previousClose": info.get("previousClose"),
            "open": info.get("open"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "volume": info.get("volume"),
            "marketCap": info.get("marketCap"),
        }

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{symbol}")
def get_stock_history(
    symbol: str,
    period: str = Query(default="1mo", description="Examples: 5d, 1mo, 3mo, 6mo, 1y"),
    interval: str = Query(default="1d", description="Examples: 1d, 1h, 15m")
):
    """
    ดึงข้อมูลราคาหุ้นย้อนหลัง
    เช่น /history/AAPL?period=1mo&interval=1d
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data found")

        hist = hist.reset_index()

        # แปลง timestamp เป็น string
        if "Date" in hist.columns:
            hist["Date"] = hist["Date"].astype(str)
        if "Datetime" in hist.columns:
            hist["Datetime"] = hist["Datetime"].astype(str)

        records = hist.to_dict(orient="records")

        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "count": len(records),
            "data": records
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
