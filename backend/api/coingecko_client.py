import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import structlog

from api.rate_limiter import rate_limiter

logger = structlog.get_logger()


class CoinGeckoClient:
    """
    CoinGecko API Client

    CRITICAL: Max 50 calls/minute on free tier!
    Strategy:
    - Use Binance for real-time prices (no limits)
    - Use CoinGecko for:
      * Historical data (cache heavily!)
      * Market cap data
      * Global market stats
      * Trending coins
    - Aggressive caching to stay under limits
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    # Symbol mapping (CoinGecko uses different IDs)
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "MATIC": "matic-network",
        "DOT": "polkadot",
        "ADA": "cardano",
        "XRP": "ripple",
        "INJ": "injective-protocol",
        "SEI": "sei-network",
        "ARB": "arbitrum",
        "OP": "optimism",
        "TIA": "celestia",
        "SUI": "sui",
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko client

        Args:
            api_key: Optional API key (Pro tier)
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["X-CG-PRO-API-KEY"] = self.api_key

            self.session = aiohttp.ClientSession(headers=headers)

        return self.session

    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _make_request(
        self, endpoint: str, params: Optional[Dict] = None, priority: str = "medium"
    ) -> Dict:
        """
        Make API request with rate limiting

        Args:
            endpoint: API endpoint
            params: Query parameters
            priority: Request priority

        Returns:
            API response data
        """
        # CRITICAL: Acquire rate limit token BEFORE request
        await rate_limiter.acquire("coingecko", priority=priority, tokens=1)

        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 429:
                    # Rate limit exceeded
                    logger.error("coingecko_rate_limit_exceeded")
                    retry_after = int(response.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params, priority)

                elif response.status != 200:
                    logger.error(
                        "coingecko_api_error",
                        status=response.status,
                        endpoint=endpoint,
                    )
                    return {}

                return await response.json()

        except asyncio.TimeoutError:
            logger.error("coingecko_timeout", endpoint=endpoint)
            return {}
        except Exception as e:
            logger.error("coingecko_request_error", endpoint=endpoint, error=str(e))
            return {}

    async def get_coin_data(
        self, symbol: str, include_market_data: bool = True
    ) -> Optional[Dict]:
        """
        Get comprehensive coin data

        Args:
            symbol: Coin symbol (BTC, ETH, etc.)
            include_market_data: Include market cap, volume, etc.

        Returns:
            Coin data
        """
        coin_id = self.SYMBOL_TO_ID.get(symbol.upper())
        if not coin_id:
            logger.warning("coingecko_unknown_symbol", symbol=symbol)
            return None

        data = await self._make_request(
            f"coins/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
            },
            priority="high",
        )

        if not data:
            return None

        market_data = data.get("market_data", {})

        return {
            "symbol": symbol.upper(),
            "name": data.get("name"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "market_cap_rank": market_data.get("market_cap_rank"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_percentage_24h"),
            "price_change_7d": market_data.get("price_change_percentage_7d"),
            "price_change_30d": market_data.get("price_change_percentage_30d"),
            "ath": market_data.get("ath", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
        }

    async def get_historical_prices(
        self, symbol: str, days: int = 30
    ) -> List[Dict]:
        """
        Get historical price data

        Args:
            symbol: Coin symbol
            days: Number of days of history

        Returns:
            List of price data points
        """
        coin_id = self.SYMBOL_TO_ID.get(symbol.upper())
        if not coin_id:
            return []

        data = await self._make_request(
            f"coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            priority="low",  # Historical data is low priority
        )

        if not data or "prices" not in data:
            return []

        # Convert to readable format
        prices = []
        for timestamp, price in data["prices"]:
            prices.append(
                {"timestamp": datetime.fromtimestamp(timestamp / 1000), "price": price}
            )

        return prices

    async def get_global_market_data(self) -> Dict:
        """
        Get global cryptocurrency market data

        Returns:
            Global market stats
        """
        data = await self._make_request("global", priority="medium")

        if not data or "data" not in data:
            return {}

        global_data = data["data"]

        return {
            "total_market_cap_usd": global_data.get("total_market_cap", {}).get("usd"),
            "total_volume_24h_usd": global_data.get("total_volume", {}).get("usd"),
            "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc"),
            "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth"),
            "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
            "markets": global_data.get("markets"),
            "market_cap_change_24h": global_data.get(
                "market_cap_change_percentage_24h_usd"
            ),
        }

    async def get_trending_coins(self) -> List[Dict]:
        """
        Get trending coins

        Returns:
            List of trending coins
        """
        data = await self._make_request("search/trending", priority="low")

        if not data or "coins" not in data:
            return []

        trending = []
        for item in data["coins"][:10]:  # Top 10
            coin = item.get("item", {})
            trending.append(
                {
                    "symbol": coin.get("symbol"),
                    "name": coin.get("name"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc"),
                }
            )

        return trending

    async def get_top_gainers_losers(self, limit: int = 10) -> Dict:
        """
        Get top gainers and losers

        Args:
            limit: Number of coins to return

        Returns:
            Dict with gainers and losers
        """
        # Get market data for top coins
        data = await self._make_request(
            "coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": "false",
            },
            priority="medium",
        )

        if not data:
            return {"gainers": [], "losers": []}

        # Sort by 24h change
        gainers = sorted(
            data, key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True
        )[:limit]

        losers = sorted(data, key=lambda x: x.get("price_change_percentage_24h", 0))[
            :limit
        ]

        return {
            "gainers": [
                {
                    "symbol": g.get("symbol").upper(),
                    "name": g.get("name"),
                    "change_24h": g.get("price_change_percentage_24h"),
                    "price": g.get("current_price"),
                }
                for g in gainers
            ],
            "losers": [
                {
                    "symbol": l.get("symbol").upper(),
                    "name": l.get("name"),
                    "change_24h": l.get("price_change_percentage_24h"),
                    "price": l.get("current_price"),
                }
                for l in losers
            ],
        }

    async def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Get Fear & Greed Index

        Note: This might require alternative.me API or similar

        Returns:
            Fear & Greed Index data
        """
        # Fear & Greed is not from CoinGecko
        # Using alternative.me API instead
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.alternative.me/fng/", timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and "data" in data:
                            fng = data["data"][0]
                            return {
                                "value": int(fng.get("value")),
                                "classification": fng.get("value_classification"),
                                "timestamp": datetime.fromtimestamp(
                                    int(fng.get("timestamp"))
                                ),
                            }
        except Exception as e:
            logger.warning("fear_greed_index_error", error=str(e))

        return None

    def get_coin_id(self, symbol: str) -> Optional[str]:
        """
        Get CoinGecko coin ID from symbol

        Args:
            symbol: Coin symbol

        Returns:
            CoinGecko coin ID
        """
        return self.SYMBOL_TO_ID.get(symbol.upper())
