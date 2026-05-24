#!/usr/bin/env python3
import os
import json
import time
import requests
from datetime import datetime, timedelta, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
ARTICLES_PER_RUN = int(os.environ.get("ARTICLES_PER_RUN", "3"))

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

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
        print(f"⚠️ CoinGecko error: {e}, using fallback coins")
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

def build_prompt(coin, price, change_str):
    return f"""You are a professional crypto news writer. Write a detailed, SEO-optimized crypto news article.

Coin: {coin['name']} ({coin['symbol']})
Current Price: ${price}
24h Change: {change_str}

Return your response as a JSON object with exactly these fields:
{{
  "title": "Engaging SEO title (60-70 chars)",
  "summary": "2-3 sentence summary for previews",
  "content": "Full article content (400-600 words). Use ## for headings, paragraphs separated by blank lines. Include price analysis, market sentiment, key factors.",
  "coin_tags": ["{coin['symbol']}", "CRYPTO"],
  "market_analysis": {{
    "short_term": "Bullish/Bearish/Neutral",
    "long_term": "Bullish/Bearish/Neutral",
    "support": "$XX,XXX (realistic support level)",
    "resistance": "$XX,XXX (realistic resistance level)",
    "sentiment_score": 65,
    "key_insight": "One key insight in 1-2 sentences"
  }}
}}

Return ONLY valid JSON, no markdown, no extra text."""

def parse_ai_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    return json.loads(text)

def generate_with_groq(coin, price_data):
    if not GROQ_API_KEY:
        raise Exception("No Groq API key")
    price = price_data.get("usd", "N/A")
    change = price_data.get("usd_24h_change", 0)
    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
    prompt = build_prompt(coin, price, change_str)
    print(f"🤖 Generating with Groq for {coin['symbol']}...")
    for attempt in range(3):
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500,
                },
                timeout=30,
            )
            if res.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"⏳ Rate limit, waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
                continue
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            return parse_ai_response(content), "groq"
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"⏳ Retry {attempt+1}/3 after error: {e}")
            time.sleep(10)
    raise Exception("Groq failed after 3 attempts")

def generate_article(coin, price_data):
    try:
        return generate_with_groq(coin, price_data)
    except Exception as e:
        print(f"❌ Groq failed: {e}")
        raise Exception(f"Article generation failed: {e}")

def get_image_unsplash(query):
    if not UNSPLASH_ACCESS_KEY:
        raise Exception("No Unsplash key")
    print(f"🖼️ Searching Unsplash for: {query}")
    res = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 5, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        timeout=10,
    )
    res.raise_for_status()
    results = res.json().get("results", [])
    if not results:
        raise Exception("No Unsplash results")
    photo = results[0]
    return {"url": photo["urls"]["regular"], "credit": f"Photo by {photo['user']['name']} on Unsplash"}

def get_image_pexels(query):
    if not PEXELS_API_KEY:
        raise Exception("No Pexels key")
    print(f"🖼️ Searching Pexels for: {query} (fallback)")
    res = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "per_page": 5, "orientation": "landscape"},
        headers={"Authorization": PEXELS_API_KEY},
        timeout=10,
    )
    res.raise_for_status()
    photos = res.json().get("photos", [])
    if not photos:
        raise Exception("No Pexels results")
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
    query = f"{coin_name} cryptocurrency bitcoin trading"
    try:
        return get_image_unsplash(query)
    except Exception as e:
        print(f"⚠️ Unsplash failed: {e}")
        try:
            return get_image_pexels(query)
        except Exception as e2:
            print(f"⚠️ Pexels failed: {e2}, using default image")
            return get_default_image(coin_symbol)

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
    print(f"✅ Saved article: {article_data['title'][:60]}... (ID: {article_id})")
    return article_id

def cleanup_old_data():
    print("🧹 Cleaning up old data...")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/news", params={"published_at": f"lt.{cutoff}"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Deleted old articles (status: {res.status_code})")
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/analytics", params={"created_at": f"lt.{cutoff}"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Deleted old analytics (status: {res.status_code})")
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/signals", params={"created_at": f"lt.{cutoff}", "is_active": "eq.false"}, headers=SUPABASE_HEADERS)
    print(f"🗑️ Deleted old signals (status: {res.status_code})")

def main():
    print("=" * 50)
    print(f"🚀 Crypto News Automation Starting")
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return

    if not GROQ_API_KEY:
        print("❌ Missing GROQ_API_KEY")
        return

    coins = get_trending_coins()
    coins = coins[:ARTICLES_PER_RUN]
    success_count = 0
    fail_count = 0

    for i, coin in enumerate(coins):
        print(f"\n--- Processing {i+1}/{len(coins)}: {coin['name']} ({coin['symbol']}) ---")
        try:
            price_data = get_coin_price_data(coin["id"])
            print(f"💰 Price: ${price_data.get('usd', 'N/A')} | 24h: {price_data.get('usd_24h_change', 0):.2f}%")
            article_data, ai_provider = generate_article(coin, price_data)
            print(f"📝 Title: {article_data['title'][:60]}...")
            image_data = get_image(coin["name"], coin["symbol"])
            print(f"🖼️ Image: {image_data['url'][:60]}...")
            save_article(article_data, image_data, ai_provider)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed for {coin['symbol']}: {e}")
            fail_count += 1

        if i < len(coins) - 1:
            print("⏳ Waiting 10 seconds...")
            time.sleep(10)

    print("\n" + "=" * 50)
    cleanup_old_data()
    print("\n" + "=" * 50)
    print(f"✅ Done! Success: {success_count} | Failed: {fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    main()
