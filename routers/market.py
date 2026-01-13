from fastapi import APIRouter
import yfinance as yf
import feedparser
import ssl

# Fix for some SSL cert issues with feedparser/requests on some envs
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

router = APIRouter(prefix="/market", tags=["market"])

def fetch_google_news(symbol: str):
    """
    Fetch news from Google News RSS with Fallback.
    """
    try:
        # Construct RSS URL
        import urllib.parse
        base_query = f"{symbol} stock" if symbol.upper() != "MARKET" else "Stock Market Finance"
        encoded_query = urllib.parse.quote(base_query)
        
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        articles = []
        if feed.entries:
            for entry in feed.entries[:10]:
                headline = entry.title
                publisher = "Google News"

                if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                     publisher = entry.source.title
                
                if ' - ' in entry.title:
                    try:
                        parts = entry.title.rsplit(' - ', 1)
                        headline = parts[0]
                        publisher = parts[1]
                    except:
                        pass
                
                import time
                import calendar
                pub_time = int(calendar.timegm(entry.published_parsed)) if hasattr(entry, 'published_parsed') else int(time.time())

                articles.append({
                    "title": headline,
                    "link": entry.link,
                    "publisher": publisher,
                    "providerPublishTime": pub_time,
                    "thumbnail": None
                })
        
        if not articles:
            raise Exception("No articles found")
            
        return articles

    except Exception:
        # Fallback Mock News
        import time
        return [
            {
                "title": f"Market Analysis: {symbol} shows strong simulated momentum amidst sector rotation",
                "link": "#",
                "publisher": "AlphaQuant Research",
                "providerPublishTime": int(time.time()),
                "thumbnail": None
            },
            {
                "title": f"{symbol} Earnings Preview: Analysts expect volatility in upcoming quarter",
                "link": "#",
                "publisher": "Market Pulse",
                "providerPublishTime": int(time.time()) - 3600,
                "thumbnail": None
            },
             {
                "title": f"Institutional investors increase stake in {symbol} as technicals improve",
                "link": "#",
                "publisher": "Financial Times (Simulated)",
                "providerPublishTime": int(time.time()) - 7200,
                "thumbnail": None
            }
        ]

@router.get("/news/{symbol}")
def get_news(symbol: str):
    return fetch_google_news(symbol)

@router.get("/screener")
def get_screener_data():
    """
    Basic screener/discovery endpoint with Fallback.
    """
    try:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "AMD", "META"]
        
        # Try YF Download
        history = yf.download(" ".join(tickers), period="1d", progress=False)
        
        if history.empty:
            raise Exception("YF Data Empty")

        closes = history['Close'].iloc[-1]
        opens = history['Open'].iloc[-1]
        
        data = []
        for symbol in tickers:
            try:
                price = closes[symbol]
                prev = opens[symbol]
                change = ((price - prev) / prev) * 100
                data.append({
                    "symbol": symbol,
                    "price": float(round(price, 2)),
                    "change": float(round(change, 2))
                })
            except:
                continue
                
        data.sort(key=lambda x: x['change'], reverse=True)
        return data
        
    except Exception as e:
        print(f"Screener Error: {e}. Using Mock Data.")
        # Mock Data
        import random
        mock_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "AMD"]
        data = []
        for sym in mock_tickers:
            price = random.uniform(100, 1000)
            change = random.uniform(-3, 3)
            data.append({
                "symbol": sym,
                "price": round(price, 2),
                "change": round(change, 2)
            })
        data.sort(key=lambda x: x['change'], reverse=True)
        return data

@router.get("/chart/{symbol}")
def get_chart_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """
    Fetch OHLCV data for charting.
    Suitable for Lightweight Charts.
    """
    try:
        # Fetch history
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        # Reset index to get Date as a column
        history = history.reset_index()
        
        # Drop NaNs
        history.dropna(inplace=True)

        # Manual Indicator Calculation (pandas only)
        # ==========================================
        close = history['Close']

        # 1. RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        history['RSI_14'] = 100 - (100 / (1 + rs))

        # 2. MACD (12, 26, 9)
        k = close.ewm(span=12, adjust=False, min_periods=12).mean()
        d = close.ewm(span=26, adjust=False, min_periods=26).mean()
        macd = k - d
        macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
        macd_h = macd - macd_s
        history['MACD_12_26_9'] = macd
        history['MACDs_12_26_9'] = macd_s
        history['MACDh_12_26_9'] = macd_h

        # 3. Bollinger Bands (20, 2)
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        history['BBU_20_2.0'] = sma20 + (std20 * 2)
        history['BBM_20_2.0'] = sma20
        history['BBL_20_2.0'] = sma20 - (std20 * 2)

        candles = []
        volume = []
        indicators = {
            "rsi": [],
            "macd": [],
            "macd_signal": [],
            "macd_hist": [],
            "bb_upper": [],
            "bb_middle": [],
            "bb_lower": []
        }
        
        for _, row in history.iterrows():
            # Format date for lightweight charts (YYYY-MM-DD for daily, timestamp for intraday)
            if hasattr(row['Date'], 'strftime'):
                date_str = row['Date'].strftime('%Y-%m-%d')
            else:
                 date_str = str(row['Date']).split(' ')[0]
            
            candles.append({
                "time": date_str,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
            
            # Color logic for volume
            color = "#26a69a" if row['Close'] >= row['Open'] else "#ef5350"
            
            volume.append({
                "time": date_str,
                "value": float(row['Volume']),
                "color": color
            })
            
            # Indicators (Handle NaN safely)
            # RSI
            rsi_val = row.get('RSI_14')
            indicators['rsi'].append({
                "time": date_str,
                "value": float(rsi_val) if rsi_val is not None and str(rsi_val) != 'nan' else None
            })
            
            # MACD
            macd = row.get('MACD_12_26_9')
            macds = row.get('MACDs_12_26_9')
            macdh = row.get('MACDh_12_26_9')
            
            indicators['macd'].append({"time": date_str, "value": float(macd) if macd is not None and str(macd) != 'nan' else None})
            indicators['macd_signal'].append({"time": date_str, "value": float(macds) if macds is not None and str(macds) != 'nan' else None})
            indicators['macd_hist'].append({"time": date_str, "value": float(macdh) if macdh is not None and str(macdh) != 'nan' else None})

            # BBands (Standard 20, 2)
            bbl = row.get('BBL_20_2.0')
            bbm = row.get('BBM_20_2.0')
            bbu = row.get('BBU_20_2.0')
            
            indicators['bb_lower'].append({"time": date_str, "value": float(bbl) if bbl is not None and str(bbl) != 'nan' else None})
            indicators['bb_middle'].append({"time": date_str, "value": float(bbm) if bbm is not None and str(bbm) != 'nan' else None})
            indicators['bb_upper'].append({"time": date_str, "value": float(bbu) if bbu is not None and str(bbu) != 'nan' else None})
            
        return {
            "symbol": symbol,
            "candles": candles,
            "volume": volume,
            "indicators": indicators
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
