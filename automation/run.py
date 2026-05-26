#!/usr/bin/env python3
"""
CryptoSignals LK - Full Automation Script
- Fetches trending coins (CoinGecko)
- Generates news articles (Groq AI)
- Generates SMC-based trading signals
- Fetches copyright-free images (Unsplash/Pexels)
- Saves to Supabase
- Posts signals to Telegram
- Cleans up 30-day old data
"""

import os
import re
import json
import time
import math
import requests
from datetime import datetime, timedelta, timezone

# =============================================
# CONFIG
# =============================================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
ARTICLES_PER_RUN = int(os.environ.get("ARTICLES_PER_RUN", "3"))
SIGNALS_PER_RUN = int(os.environ.get("SIGNALS_PER_RUN", "3"))
SITE_URL = os.environ.get("SITE_URL", "https://crypto-news-lake.vercel.app")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# =============================================
# STEP 1: FETCH MARKET DATA
# =============================================

def get_trending_coins():
    print("📈 Fetching trending coins from CoinGecko...")
    try:
        res = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
        data = res.json()
        coins = []
        for item in data.get("coins", [])[:7]:
            coin = item["item"]
            coins.append({
                "id": coin["id"],
                "name": coin["name"],
                "symbol": coin["symbol"].upper(),
                "market_cap_rank": coin.get("market_cap_rank", 999),
            })
        print(f"✅ Found {len(coins)} trending coins: {[c['symbol'] for c in coins]}")
        return coins
    except Exception as e:
        print(f"⚠️ CoinGecko error: {e}, using fallback")
        return [
            {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "market_cap_rank": 1},
            {"id": "ethereum", "name": "Ethereum", "symbol": "ETH", "market_cap_rank": 2},
            {"id": "solana", "name": "Solana", "symbol": "SOL", "market_cap_rank": 5},
        ]

def get_coin_price_data(coin_id):
    try:
        res = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true",
            timeout=10
        )
        data = res.json()
        if coin_id in data:
            return data[coin_id]
    except:
        pass
    return {}

def get_ohlcv_data(coin_id, days=14):
    """Fetch OHLCV candle data for technical analysis"""
    try:
        res = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}",
            timeout=15
        )
        data = res.json()
        candles = []
        for c in data:
            candles.append({
                "openTime": c[0],
                "open": c[1],
                "high": c[2],
                "low": c[3],
                "close": c[4],
            })
        return candles
    except Exception as e:
        print(f"⚠️ OHLCV fetch failed: {e}")
        return []

# =============================================
# STEP 2: SMC TECHNICAL ANALYSIS ENGINE
# (Adapted from your Forex system)
# =============================================

class SwingPointDetector:
    def __init__(self, lookback=3):
        self.lookback = lookback

    def detect(self, candles):
        swings = []
        for i in range(self.lookback, len(candles) - self.lookback):
            curr = candles[i]
            left = candles[i - self.lookback:i]
            right = candles[i + 1:i + self.lookback + 1]

            is_high = all(c["high"] < curr["high"] for c in left) and \
                      all(c["high"] < curr["high"] for c in right)
            is_low = all(c["low"] > curr["low"] for c in left) and \
                     all(c["low"] > curr["low"] for c in right)

            if is_high:
                swings.append({"type": "high", "price": curr["high"], "index": i, "time": curr["openTime"]})
            if is_low:
                swings.append({"type": "low", "price": curr["low"], "index": i, "time": curr["openTime"]})

        return sorted(swings, key=lambda x: x["time"])


class StructureAnalyzer:
    def analyze(self, swings):
        if len(swings) < 4:
            return "unknown"

        highs = [s for s in swings if s["type"] == "high"]
        lows = [s for s in swings if s["type"] == "low"]

        hh = lh = hl = ll = 0
        for i in range(1, len(highs)):
            if highs[i]["price"] > highs[i-1]["price"]: hh += 1
            else: lh += 1
        for i in range(1, len(lows)):
            if lows[i]["price"] > lows[i-1]["price"]: hl += 1
            else: ll += 1

        if hh >= 2 and hl >= 2: return "bullish_trending"
        if lh >= 2 and ll >= 2: return "bearish_trending"
        return "ranging"


class LiquidityAnalyzer:
    def detect_sweep(self, candles, swings):
        """Detect if recent price swept a key liquidity level"""
        if len(candles) < 3 or len(swings) < 2:
            return None

        last = candles[-1]
        prev = candles[-2]

        highs = [s for s in swings if s["type"] == "high"]
        lows = [s for s in swings if s["type"] == "low"]

        if not highs or not lows:
            return None

        recent_high = max(highs, key=lambda x: x["time"])
        recent_low = min(lows, key=lambda x: x["time"])

        # Upside sweep (hit buy-side liquidity) → Bearish bias
        if last["high"] > recent_high["price"] and last["close"] < recent_high["price"]:
            return {
                "direction": "upside",
                "bias": "bearish",
                "level": recent_high["price"],
                "confidence": 0.72,
            }

        # Downside sweep (hit sell-side liquidity) → Bullish bias
        if last["low"] < recent_low["price"] and last["close"] > recent_low["price"]:
            return {
                "direction": "downside",
                "bias": "bullish",
                "level": recent_low["price"],
                "confidence": 0.72,
            }

        return None

    def find_equal_levels(self, candles, tolerance_pct=0.002):
        """Find equal highs/lows (EQH/EQL) - engineered liquidity"""
        highs = [c["high"] for c in candles[-20:]]
        lows = [c["low"] for c in candles[-20:]]

        eqh = eql = None
        for i in range(len(highs)):
            for j in range(i+1, len(highs)):
                if abs(highs[i] - highs[j]) / max(highs[i], 0.001) < tolerance_pct:
                    eqh = (highs[i] + highs[j]) / 2
        for i in range(len(lows)):
            for j in range(i+1, len(lows)):
                if abs(lows[i] - lows[j]) / max(lows[i], 0.001) < tolerance_pct:
                    eql = (lows[i] + lows[j]) / 2

        return {"eqh": eqh, "eql": eql}


class OrderBlockDetector:
    def detect(self, candles):
        """Find bullish/bearish order blocks"""
        obs = []
        for i in range(1, len(candles) - 1):
            curr = candles[i]
            nxt = candles[i + 1]

            curr_bull = curr["close"] > curr["open"]
            curr_bear = curr["close"] < curr["open"]
            nxt_bull = nxt["close"] > nxt["open"]
            nxt_bear = nxt["close"] < nxt["open"]

            # Bullish OB: bearish candle before strong bullish move
            if curr_bear and nxt_bull and nxt["close"] > curr["high"]:
                obs.append({
                    "type": "bullish",
                    "top": curr["high"],
                    "bottom": curr["low"],
                    "time": curr["openTime"],
                })

            # Bearish OB: bullish candle before strong bearish move
            if curr_bull and nxt_bear and nxt["close"] < curr["low"]:
                obs.append({
                    "type": "bearish",
                    "top": curr["high"],
                    "bottom": curr["low"],
                    "time": curr["openTime"],
                })

        return obs[-3:] if obs else []


class FVGDetector:
    def detect(self, candles):
        """Detect Fair Value Gaps"""
        fvgs = []
        for i in range(1, len(candles) - 1):
            prev = candles[i - 1]
            curr = candles[i]
            nxt = candles[i + 1]

            # Bullish FVG
            if nxt["low"] > prev["high"]:
                fvgs.append({
                    "type": "bullish",
                    "top": nxt["low"],
                    "bottom": prev["high"],
                    "mid": (nxt["low"] + prev["high"]) / 2,
                })

            # Bearish FVG
            if nxt["high"] < prev["low"]:
                fvgs.append({
                    "type": "bearish",
                    "top": prev["low"],
                    "bottom": nxt["high"],
                    "mid": (prev["low"] + nxt["high"]) / 2,
                })

        return fvgs[-3:] if fvgs else []


def analyze_market_structure(candles, coin):
    """Full SMC analysis pipeline - adapted from your Forex system"""
    if len(candles) < 10:
        return None

    swing_detector = SwingPointDetector(lookback=3)
    structure_analyzer = StructureAnalyzer()
    liquidity_analyzer = LiquidityAnalyzer()
    ob_detector = OrderBlockDetector()
    fvg_detector = FVGDetector()

    swings = swing_detector.detect(candles)
    phase = structure_analyzer.analyze(swings)
    sweep = liquidity_analyzer.detect_sweep(candles, swings)
    eq_levels = liquidity_analyzer.find_equal_levels(candles)
    order_blocks = ob_detector.detect(candles)
    fvgs = fvg_detector.detect(candles)

    last_price = candles[-1]["close"]
    highs = [s["price"] for s in swings if s["type"] == "high"]
    lows = [s["price"] for s in swings if s["type"] == "low"]

    recent_high = max(highs[-3:]) if highs else last_price * 1.05
    recent_low = min(lows[-3:]) if lows else last_price * 0.95

    # Determine signal
    signal_type = "HOLD"
    confidence = 50
    htf_bias = "neutral"

    if sweep:
        htf_bias = sweep["bias"]
        confidence = int(sweep["confidence"] * 100)
        if sweep["bias"] == "bullish":
            signal_type = "BUY"
            confidence = min(90, confidence + 10)
        elif sweep["bias"] == "bearish":
            signal_type = "SELL"
            confidence = min(90, confidence + 10)
    elif phase == "bullish_trending":
        signal_type = "BUY"
        htf_bias = "bullish"
        confidence = 65
    elif phase == "bearish_trending":
        signal_type = "SELL"
        htf_bias = "bearish"
        confidence = 65

    # Order block entry refinement
    entry_price = last_price
    entry_method = "market"
    if order_blocks:
        relevant_obs = [ob for ob in order_blocks
                       if (signal_type == "BUY" and ob["type"] == "bullish") or
                          (signal_type == "SELL" and ob["type"] == "bearish")]
        if relevant_obs:
            ob = relevant_obs[-1]
            entry_price = ob["top"] if signal_type == "BUY" else ob["bottom"]
            entry_method = "order_block"

    # FVG entry refinement
    if fvgs and entry_method == "market":
        relevant_fvgs = [f for f in fvgs
                        if (signal_type == "BUY" and f["type"] == "bullish") or
                           (signal_type == "SELL" and f["type"] == "bearish")]
        if relevant_fvgs:
            entry_price = relevant_fvgs[-1]["mid"]
            entry_method = "fvg"

    # Calculate SL/TP
    atr = calculate_atr(candles)
    if signal_type == "BUY":
        stop_loss = round(entry_price - atr * 2, 6)
        target_price = round(entry_price + atr * 4, 6)
    elif signal_type == "SELL":
        stop_loss = round(entry_price + atr * 2, 6)
        target_price = round(entry_price - atr * 4, 6)
    else:
        stop_loss = round(last_price - atr * 2, 6)
        target_price = round(last_price + atr * 2, 6)

    return {
        "coin": coin["symbol"],
        "signal_type": signal_type,
        "entry_price": round(entry_price, 6),
        "target_price": target_price,
        "stop_loss": stop_loss,
        "confidence": confidence,
        "phase": phase,
        "htf_bias": htf_bias,
        "entry_method": entry_method,
        "sweep": sweep,
        "eq_levels": eq_levels,
        "order_blocks_count": len(order_blocks),
        "fvgs_count": len(fvgs),
        "last_price": last_price,
        "atr": atr,
    }


def calculate_atr(candles, period=14):
    if len(candles) < 2:
        return candles[-1]["close"] * 0.02 if candles else 0
    ranges = [abs(c["high"] - c["low"]) for c in candles[-period:]]
    return sum(ranges) / len(ranges)

# =============================================
# STEP 3: AI CONTENT GENERATION (GROQ)
# =============================================

def build_article_prompt(coin, price, change_str):
    return f"""You are a professional crypto news writer. Write a crypto news article about {coin['name']} ({coin['symbol']}).

Current Price: ${price}
24h Change: {change_str}

Respond with ONLY a JSON object. No markdown, no code blocks, no extra text:
{{"title":"SEO title here","summary":"2-3 sentence summary here","content":"Full article 250-300 words. No special characters.","coin_tags":["{coin['symbol']}","CRYPTO"],"market_analysis":{{"short_term":"Bullish","long_term":"Bullish","support":"$X,XXX","resistance":"$X,XXX","sentiment_score":65,"key_insight":"Key insight here"}}}}"""


def build_signal_prompt(coin, smc_data, price_data):
    price = price_data.get("usd", "N/A")
    change = price_data.get("usd_24h_change", 0)
    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

    return f"""You are an expert crypto trader using SMC (Smart Money Concepts).

Coin: {coin['name']} ({coin['symbol']})
Current Price: ${price}
24h Change: {change_str}
Market Phase: {smc_data['phase']}
HTF Bias: {smc_data['htf_bias']}
Signal Type: {smc_data['signal_type']}
Entry Price: ${smc_data['entry_price']}
Stop Loss: ${smc_data['stop_loss']}
Target: ${smc_data['target_price']}
Confidence: {smc_data['confidence']}%
Order Blocks Found: {smc_data['order_blocks_count']}
FVGs Found: {smc_data['fvgs_count']}

Write a SHORT signal analysis (2-3 sentences max) explaining WHY this signal is valid based on the SMC data above.
Return ONLY plain text, no JSON, no markdown."""


def parse_ai_response(text):
    text = text.strip()
    if "```" in text:
        text = re.sub(r'```(?:json)?', '', text)
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        def fix_newlines(s):
            result = []
            in_string = False
            escape = False
            for ch in s:
                if escape:
                    result.append(ch)
                    escape = False
                elif ch == '\\':
                    result.append(ch)
                    escape = True
                elif ch == '"':
                    result.append(ch)
                    in_string = not in_string
                elif in_string and ch == '\n':
                    result.append('\\n')
                elif in_string and ch == '\r':
                    result.append('\\r')
                elif in_string and ch == '\t':
                    result.append('\\t')
                else:
                    result.append(ch)
            return ''.join(result)
        text = fix_newlines(text)
        try:
            return json.loads(text)
        except:
            text = re.sub(r'[\n\r\t]', ' ', text)
            return json.loads(text)


def call_groq(prompt, max_tokens=2048, json_mode=True):
    if not GROQ_API_KEY:
        raise Exception("No Groq API key")
    for attempt in range(3):
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if res.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"⏳ Rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"⏳ Retry {attempt+1}/3: {e}")
            time.sleep(10)
    raise Exception("Groq failed after 3 attempts")

# =============================================
# STEP 4: IMAGE FETCHING
# =============================================

def get_image_unsplash(query):
    if not UNSPLASH_ACCESS_KEY:
        raise Exception("No Unsplash key")
    res = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 5, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        timeout=10,
    )
    res.raise_for_status()
    results = res.json().get("results", [])
    if not results:
        raise Exception("No results")
    photo = results[0]
    return {"url": photo["urls"]["regular"], "credit": f"Photo by {photo['user']['name']} on Unsplash"}


def get_image_pexels(query):
    if not PEXELS_API_KEY:
        raise Exception("No Pexels key")
    res = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "per_page": 5, "orientation": "landscape"},
        headers={"Authorization": PEXELS_API_KEY},
        timeout=10,
    )
    res.raise_for_status()
    photos = res.json().get("photos", [])
    if not photos:
        raise Exception("No results")
    photo = photos[0]
    return {"url": photo["src"]["large"], "credit": f"Photo by {photo['photographer']} on Pexels"}


def get_default_image(symbol):
    defaults = {
        "BTC": "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=800&q=80",
        "ETH": "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80",
        "SOL": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&q=80",
    }
    return {"url": defaults.get(symbol, "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=800&q=80"), "credit": "Unsplash"}


def get_image(coin_name, coin_symbol):
    query = f"{coin_name} cryptocurrency trading"
    try:
        return get_image_unsplash(query)
    except:
        try:
            return get_image_pexels(query)
        except:
            return get_default_image(coin_symbol)

# =============================================
# STEP 5: SAVE TO SUPABASE
# =============================================

def save_article(article_data, image_data, ai_provider):
    payload = {
        "title": article_data["title"],
        "summary": article_data.get("summary", ""),
        "content": article_data.get("content", ""),
        "coin_tags": article_data.get("coin_tags", []),
        "image_url": image_data["url"],
        "image_credit": image_data["credit"],
        "market_analysis": article_data.get("market_analysis"),
        "is_published": True,
        "ai_provider": ai_provider,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    res = requests.post(f"{SUPABASE_URL}/rest/v1/news", headers=SUPABASE_HEADERS, json=payload)
    if res.status_code not in (200, 201):
        raise Exception(f"Supabase insert failed: {res.text}")
    data = res.json()
    article_id = data[0]["id"] if data else "unknown"
    print(f"✅ Article saved: {article_data['title'][:55]}... (ID: {article_id})")
    return article_id


def save_signal(smc_data, signal_content):
    payload = {
        "coin": smc_data["coin"],
        "signal_type": smc_data["signal_type"],
        "entry_price": smc_data["entry_price"],
        "target_price": smc_data["target_price"],
        "stop_loss": smc_data["stop_loss"],
        "confidence": smc_data["confidence"],
        "content": signal_content,
        "timeframe": "4H",
        "structure_phase": smc_data["phase"],
        "htf_bias": smc_data["htf_bias"],
        "is_active": True,
        "ai_provider": "groq+smc",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    res = requests.post(f"{SUPABASE_URL}/rest/v1/signals", headers=SUPABASE_HEADERS, json=payload)
    if res.status_code not in (200, 201):
        raise Exception(f"Signal save failed: {res.text}")
    data = res.json()
    signal_id = data[0]["id"] if data else "unknown"
    print(f"✅ Signal saved: {smc_data['coin']} {smc_data['signal_type']} @ ${smc_data['entry_price']} (ID: {signal_id})")
    return signal_id

# =============================================
# STEP 6: TELEGRAM AUTO POST
# =============================================

def send_telegram_signal(smc_data, signal_content):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("⚠️ Telegram not configured, skipping")
        return

    emoji = "🟢" if smc_data["signal_type"] == "BUY" else "🔴" if smc_data["signal_type"] == "SELL" else "🟡"
    phase_emoji = "📈" if "bullish" in smc_data["phase"] else "📉" if "bearish" in smc_data["phase"] else "↔️"

    rr = abs(smc_data["target_price"] - smc_data["entry_price"]) / max(abs(smc_data["stop_loss"] - smc_data["entry_price"]), 0.0001)

    msg = f"""{emoji} *{smc_data['coin']}/USDT — {smc_data['signal_type']} SIGNAL*

💰 *Entry:* `${smc_data['entry_price']}`
🎯 *Target:* `${smc_data['target_price']}`
🛑 *Stop Loss:* `${smc_data['stop_loss']}`
⚡ *Confidence:* {smc_data['confidence']}%
📊 *R:R Ratio:* 1:{rr:.1f}

{phase_emoji} *Structure:* {smc_data['phase'].replace('_', ' ').title()}
🧠 *HTF Bias:* {smc_data['htf_bias'].upper()}

📝 {signal_content}

⚠️ _Not financial advice. DYOR._
🔗 [Full Analysis]({SITE_URL}/signals.html)"""

    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": msg,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        if res.status_code == 200:
            print(f"✅ Telegram signal posted for {smc_data['coin']}")
        else:
            print(f"⚠️ Telegram failed: {res.text[:100]}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# =============================================
# STEP 7: CLEANUP
# =============================================

def cleanup_old_data():
    print("🧹 Cleaning up 30-day old data...")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/news", params={"published_at": f"lt.{cutoff}"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Old articles deleted (status: {res.status_code})")
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/analytics", params={"created_at": f"lt.{cutoff}"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Old analytics deleted (status: {res.status_code})")
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/signals", params={"created_at": f"lt.{cutoff}", "is_active": "eq.false"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Old signals deleted (status: {res.status_code})")

# =============================================
# MAIN
# =============================================

def main():
    print("=" * 55)
    print(f"🚀 CryptoSignals LK — Automation Starting")
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return
    if not GROQ_API_KEY:
        print("❌ Missing GROQ_API_KEY")
        return

    coins = get_trending_coins()
    article_coins = coins[:ARTICLES_PER_RUN]
    signal_coins = coins[:SIGNALS_PER_RUN]

    article_success = article_fail = 0
    signal_success = signal_fail = 0

    # ── PHASE 1: GENERATE NEWS ARTICLES ──────────────────
    print(f"\n{'─'*40}")
    print(f"📰 PHASE 1: Generating {len(article_coins)} Articles")
    print(f"{'─'*40}")

    for i, coin in enumerate(article_coins):
        print(f"\n[Article {i+1}/{len(article_coins)}] {coin['name']} ({coin['symbol']})")
        try:
            price_data = get_coin_price_data(coin["id"])
            price = price_data.get("usd", "N/A")
            change = price_data.get("usd_24h_change", 0)
            change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
            print(f"💰 Price: ${price} | 24h: {change_str}")

            prompt = build_article_prompt(coin, price, change_str)
            print(f"🤖 Generating article with Groq...")
            raw = call_groq(prompt)
            article_data = parse_ai_response(raw)
            print(f"📝 Title: {article_data['title'][:55]}...")

            image_data = get_image(coin["name"], coin["symbol"])
            print(f"🖼️ Image: {image_data['url'][:50]}...")

            save_article(article_data, image_data, "groq")
            article_success += 1
        except Exception as e:
            print(f"❌ Article failed for {coin['symbol']}: {e}")
            article_fail += 1

        if i < len(article_coins) - 1:
            print("⏳ Waiting 10s...")
            time.sleep(10)

    # ── PHASE 2: GENERATE SMC SIGNALS ────────────────────
    print(f"\n{'─'*40}")
    print(f"📊 PHASE 2: Generating {len(signal_coins)} Signals (SMC)")
    print(f"{'─'*40}")

    for i, coin in enumerate(signal_coins):
        print(f"\n[Signal {i+1}/{len(signal_coins)}] {coin['name']} ({coin['symbol']})")
        try:
            price_data = get_coin_price_data(coin["id"])
            print(f"💰 Price: ${price_data.get('usd', 'N/A')}")

            # Fetch OHLCV candles for SMC analysis
            print(f"📊 Fetching candles...")
            candles = get_ohlcv_data(coin["id"], days=14)

            if len(candles) < 10:
                print(f"⚠️ Not enough candles ({len(candles)}), skipping signal")
                signal_fail += 1
                continue

            print(f"🔍 Running SMC analysis ({len(candles)} candles)...")
            smc_data = analyze_market_structure(candles, coin)

            if not smc_data:
                print(f"⚠️ SMC analysis returned no data")
                signal_fail += 1
                continue

            print(f"📈 Signal: {smc_data['signal_type']} | Phase: {smc_data['phase']} | Confidence: {smc_data['confidence']}%")

            # Generate AI commentary
            signal_prompt = build_signal_prompt(coin, smc_data, price_data)
            signal_content = call_groq(signal_prompt, max_tokens=200, json_mode=False)
            signal_content = signal_content.strip()[:300]

            # Save to Supabase
            save_signal(smc_data, signal_content)

            # Post to Telegram
            send_telegram_signal(smc_data, signal_content)

            signal_success += 1
        except Exception as e:
            print(f"❌ Signal failed for {coin['symbol']}: {e}")
            signal_fail += 1

        if i < len(signal_coins) - 1:
            print("⏳ Waiting 10s...")
            time.sleep(10)

    # ── CLEANUP ───────────────────────────────────────────
    print(f"\n{'─'*40}")
    cleanup_old_data()

    # ── SUMMARY ───────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"✅ DONE!")
    print(f"   Articles: {article_success} success / {article_fail} fail")
    print(f"   Signals:  {signal_success} success / {signal_fail} fail")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
