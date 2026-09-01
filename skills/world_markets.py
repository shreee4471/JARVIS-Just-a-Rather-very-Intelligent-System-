"""
Skill: world_markets
Fetches live market prices (stocks, crypto, commodities) from World Monitor.

Trigger phrases: "price of bitcoin", "how is the market", "S&P 500",
                 "gold price", "oil price", "stock market", "crypto prices"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


# Common aliases the user might say → symbol or crypto id
CRYPTO_ALIASES = {
    "bitcoin": "BTC", "btc": "BTC",
    "ethereum": "ETH", "eth": "ETH",
    "solana": "SOL", "sol": "SOL",
    "bnb": "BNB",
    "xrp": "XRP", "ripple": "XRP",
    "dogecoin": "DOGE", "doge": "DOGE",
    "usdt": "USDT", "tether": "USDT",
    "usdc": "USDC",
}

STOCK_ALIASES = {
    "s&p": "SPY", "s&p 500": "SPY", "sp500": "SPY",
    "nasdaq": "QQQ",
    "dow": "DIA", "dow jones": "DIA",
    "apple": "AAPL", "aapl": "AAPL",
    "microsoft": "MSFT", "msft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL",
    "nvidia": "NVDA", "nvda": "NVDA",
    "tesla": "TSLA", "tsla": "TSLA",
    "amazon": "AMZN", "amzn": "AMZN",
}

COMMODITY_ALIASES = {
    "gold": "GC=F",
    "silver": "SI=F",
    "oil": "CL=F", "crude oil": "CL=F", "crude": "CL=F", "wti": "CL=F",
    "brent": "BZ=F",
    "natural gas": "NG=F", "gas": "NG=F",
    "copper": "HG=F",
    "wheat": "ZW=F",
    "corn": "ZC=F",
}


def _format_change(pct: float | None) -> str:
    if pct is None:
        return ""
    sign = "+" if pct >= 0 else ""
    return f" ({sign}{pct:.2f}% today)"


class WorldMarketsSkill(BaseSkill):
    name = "world_markets"
    description = (
        "Fetch live financial market prices from World Monitor including stocks, cryptocurrencies, "
        "and commodities. Use when the user asks about: the price of Bitcoin, Ethereum, gold, oil, "
        "silver, or any cryptocurrency; stock prices for Apple, Microsoft, Tesla, Nvidia, Amazon, Google; "
        "stock market indices like S&P 500, Nasdaq, Dow Jones; commodity prices; market overview. "
        "Pass the asset name or symbol as the 'asset' parameter."
    )
    parameters = {
        "asset": {
            "type": "string",
            "description": (
                "The asset to look up. Examples: 'bitcoin', 'BTC', 'gold', 'oil', "
                "'S&P 500', 'Apple', 'AAPL', 'ethereum', 'silver', 'nasdaq', or "
                "'overview' / 'market' for a general market summary."
            ),
        }
    }

    def run(self, asset: str = "overview") -> str:
        asset_lower = asset.lower().strip()

        try:
            # Determine asset type and call the right endpoint
            if asset_lower in ("overview", "market", "markets", "all"):
                return self._market_overview()

            if asset_lower in CRYPTO_ALIASES or asset_lower.upper() in {v for v in CRYPTO_ALIASES.values()}:
                return self._crypto_price(asset_lower)

            if asset_lower in COMMODITY_ALIASES or any(alias in asset_lower for alias in COMMODITY_ALIASES):
                return self._commodity_price(asset_lower)

            # Default: try stocks
            return self._stock_price(asset_lower)

        except WorldMonitorUnavailable as e:
            return str(e)

    def _crypto_price(self, asset: str) -> str:
        symbol = CRYPTO_ALIASES.get(asset, asset.upper())
        data = fetch_wm("/api/market/v1/ListCryptoQuotes")
        if not data:
            return f"Could not fetch crypto prices from World Monitor."

        quotes = data.get("quotes", [])
        for q in quotes:
            if q.get("symbol", "").upper() == symbol:
                price = q.get("currentPrice") or q.get("price")
                change = q.get("priceChangePercent24h") or q.get("change24h")
                name = q.get("name", symbol)
                if price:
                    return f"{name} is at ${price:,.2f}{_format_change(change)}."
        return f"Could not find price for {asset.upper()} in World Monitor."

    def _commodity_price(self, asset: str) -> str:
        # Find best match
        symbol = None
        for alias, sym in COMMODITY_ALIASES.items():
            if alias in asset:
                symbol = sym
                break
        if not symbol:
            symbol = asset.upper()

        data = fetch_wm("/api/market/v1/ListCommodityQuotes")
        if not data:
            return "Could not fetch commodity prices from World Monitor."

        quotes = data.get("quotes", [])
        for q in quotes:
            if q.get("symbol", "").upper() == symbol.upper():
                price = q.get("price") or q.get("currentPrice")
                change = q.get("changePercent") or q.get("priceChangePercent24h")
                name = q.get("name", asset)
                if price:
                    return f"{name} is at ${price:,.2f}{_format_change(change)}."

        return f"Could not find price for {asset} in World Monitor."

    def _stock_price(self, asset: str) -> str:
        symbol = STOCK_ALIASES.get(asset) or asset.upper()
        data = fetch_wm("/api/market/v1/ListMarketQuotes")
        if not data:
            return "Could not fetch stock prices from World Monitor."

        quotes = data.get("quotes", [])
        for q in quotes:
            if q.get("symbol", "").upper() == symbol.upper():
                price = q.get("price") or q.get("currentPrice")
                change = q.get("changePercent") or q.get("priceChangePercent24h")
                name = q.get("name", symbol)
                if price:
                    return f"{name} ({symbol}) is trading at ${price:,.2f}{_format_change(change)}."

        return f"Could not find {asset.upper()} in World Monitor's stock data."

    def _market_overview(self) -> str:
        """Pull top 3 stocks + BTC + Gold for a quick spoken summary."""
        results = []

        stock_data = fetch_wm("/api/market/v1/ListMarketQuotes")
        if stock_data:
            for q in stock_data.get("quotes", [])[:3]:
                price = q.get("price") or q.get("currentPrice")
                change = q.get("changePercent")
                if price:
                    chg = f"{'+' if (change or 0) >= 0 else ''}{change:.1f}%" if change else ""
                    results.append(f"{q.get('symbol', '')} at ${price:,.0f} {chg}".strip())

        crypto_data = fetch_wm("/api/market/v1/ListCryptoQuotes")
        if crypto_data:
            for q in crypto_data.get("quotes", []):
                if q.get("symbol", "").upper() == "BTC":
                    price = q.get("currentPrice") or q.get("price")
                    change = q.get("priceChangePercent24h")
                    if price:
                        chg = f"{'+' if (change or 0) >= 0 else ''}{change:.1f}%" if change else ""
                        results.append(f"Bitcoin at ${price:,.0f} {chg}".strip())
                    break

        if not results:
            return "World Monitor market data is loading. Please try again in a moment."

        return "Market snapshot: " + ", ".join(results) + "."
