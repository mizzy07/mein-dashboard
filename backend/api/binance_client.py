import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import structlog
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException

from api.rate_limiter import rate_limiter

logger = structlog.get_logger()


class BinanceClient:
    """
    Binance API Client

    Features:
    - WebSocket for real-time price updates (no rate limits!)
    - REST API for historical data
    - Automatic reconnection
    - Error handling with exponential backoff
    """

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Binance client

        Args:
            api_key: Optional API key (not needed for public data)
            api_secret: Optional API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Optional[AsyncClient] = None
        self.socket_manager: Optional[BinanceSocketManager] = None

        # Price cache (updated via WebSocket)
        self.price_cache: Dict[str, Dict] = {}

        # WebSocket connection status
        self.ws_connected = False
        self.ws_callbacks: List[Callable] = []

    async def connect(self):
        """Initialize Binance async client"""
        try:
            if self.api_key and self.api_secret:
                self.client = await AsyncClient.create(
                    api_key=self.api_key, api_secret=self.api_secret
                )
            else:
                # Public data only
                self.client = await AsyncClient.create()

            self.socket_manager = BinanceSocketManager(self.client)
            logger.info("binance_client_connected", has_credentials=bool(self.api_key))

        except Exception as e:
            logger.error("binance_connection_failed", error=str(e))
            raise

    async def close(self):
        """Close Binance client connection"""
        if self.socket_manager:
            try:
                await self.socket_manager.close()
            except Exception as e:
                logger.warning("binance_socket_close_error", error=str(e))

        if self.client:
            await self.client.close_connection()

        logger.info("binance_client_closed")

    async def get_ticker_24h(self, symbol: str) -> Dict:
        """
        Get 24h ticker data

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')

        Returns:
            Dict with price, volume, high, low, change
        """
        await rate_limiter.acquire("binance", priority="high")

        try:
            ticker = await self.client.get_ticker(symbol=symbol)

            return {
                "symbol": symbol,
                "price": float(ticker["lastPrice"]),
                "change_24h": float(ticker["priceChangePercent"]),
                "volume_24h": float(ticker["volume"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"]),
                "timestamp": datetime.utcnow(),
            }

        except BinanceAPIException as e:
            logger.error("binance_ticker_error", symbol=symbol, error=str(e))
            raise

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
        start_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Get candlestick (kline) data

        Args:
            symbol: Trading pair
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w)
            limit: Number of candles (max 1000)
            start_time: Start time for historical data

        Returns:
            List of OHLCV data
        """
        await rate_limiter.acquire("binance", priority="medium")

        try:
            klines = await self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=int(start_time.timestamp() * 1000) if start_time else None,
            )

            # Parse klines into readable format
            result = []
            for k in klines:
                result.append(
                    {
                        "timestamp": datetime.fromtimestamp(k[0] / 1000),
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": float(k[5]),
                    }
                )

            return result

        except BinanceAPIException as e:
            logger.error("binance_klines_error", symbol=symbol, error=str(e))
            raise

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book (bid/ask depth)

        Args:
            symbol: Trading pair
            limit: Depth limit (5, 10, 20, 50, 100, 500, 1000)

        Returns:
            Dict with bids and asks
        """
        await rate_limiter.acquire("binance", priority="high")

        try:
            order_book = await self.client.get_order_book(symbol=symbol, limit=limit)

            return {
                "symbol": symbol,
                "bids": [
                    {"price": float(b[0]), "amount": float(b[1])}
                    for b in order_book["bids"]
                ],
                "asks": [
                    {"price": float(a[0]), "amount": float(a[1])}
                    for a in order_book["asks"]
                ],
                "timestamp": datetime.utcnow(),
            }

        except BinanceAPIException as e:
            logger.error("binance_orderbook_error", symbol=symbol, error=str(e))
            raise

    async def start_ticker_socket(
        self, symbols: List[str], callback: Optional[Callable] = None
    ):
        """
        Start WebSocket for real-time ticker updates

        Args:
            symbols: List of symbols to track
            callback: Optional callback function for price updates
        """
        if not self.socket_manager:
            await self.connect()

        if callback:
            self.ws_callbacks.append(callback)

        try:
            # Convert symbols to lowercase for websocket
            symbol_list = [s.lower() for s in symbols]

            # Start multiplex socket for all symbols
            socket = self.socket_manager.multiplex_socket(
                [f"{s}@ticker" for s in symbol_list]
            )

            async with socket as stream:
                self.ws_connected = True
                logger.info("binance_websocket_connected", symbols=len(symbols))

                while True:
                    msg = await stream.recv()

                    if msg:
                        await self._process_ticker_message(msg)

        except Exception as e:
            logger.error("binance_websocket_error", error=str(e))
            self.ws_connected = False

            # Retry connection after delay
            await asyncio.sleep(5)
            logger.info("binance_websocket_reconnecting")
            await self.start_ticker_socket(symbols, callback)

    async def _process_ticker_message(self, msg: Dict):
        """Process incoming ticker WebSocket message"""
        try:
            if msg.get("e") == "24hrTicker":
                data = msg.get("data", {})
                symbol = data.get("s")

                if symbol:
                    # Update cache
                    self.price_cache[symbol] = {
                        "symbol": symbol,
                        "price": float(data.get("c", 0)),
                        "change_24h": float(data.get("P", 0)),
                        "volume_24h": float(data.get("v", 0)),
                        "high_24h": float(data.get("h", 0)),
                        "low_24h": float(data.get("l", 0)),
                        "timestamp": datetime.utcnow(),
                    }

                    # Call registered callbacks
                    for callback in self.ws_callbacks:
                        await callback(self.price_cache[symbol])

        except Exception as e:
            logger.error("binance_message_process_error", error=str(e))

    def get_cached_price(self, symbol: str) -> Optional[Dict]:
        """
        Get cached price from WebSocket updates

        Args:
            symbol: Trading pair

        Returns:
            Cached price data or None
        """
        return self.price_cache.get(symbol)

    async def get_funding_rate(self, symbol: str) -> Optional[Dict]:
        """
        Get current funding rate for futures

        Args:
            symbol: Futures symbol

        Returns:
            Funding rate data
        """
        await rate_limiter.acquire("binance", priority="medium")

        try:
            # Get funding rate from futures API
            funding = await self.client.futures_funding_rate(symbol=symbol, limit=1)

            if funding:
                return {
                    "symbol": symbol,
                    "funding_rate": float(funding[0]["fundingRate"]),
                    "funding_time": datetime.fromtimestamp(
                        funding[0]["fundingTime"] / 1000
                    ),
                }

            return None

        except Exception as e:
            logger.warning("binance_funding_rate_error", symbol=symbol, error=str(e))
            return None

    async def get_open_interest(self, symbol: str) -> Optional[Dict]:
        """
        Get open interest for futures

        Args:
            symbol: Futures symbol

        Returns:
            Open interest data
        """
        await rate_limiter.acquire("binance", priority="low")

        try:
            oi = await self.client.futures_open_interest(symbol=symbol)

            return {
                "symbol": symbol,
                "open_interest": float(oi["openInterest"]),
                "timestamp": datetime.fromtimestamp(int(oi["time"]) / 1000),
            }

        except Exception as e:
            logger.warning("binance_open_interest_error", symbol=symbol, error=str(e))
            return None
