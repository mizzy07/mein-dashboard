from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from typing import List, Optional

from config.settings import settings
from data.cache_manager import cache_manager
from api.binance_client import BinanceClient
from api.coingecko_client import CoinGeckoClient
from ai_agent.claude_analyzer import claude_analyzer
from ai_agent.signal_generator import signal_generator
from indicators.technical import TechnicalIndicators
from data.models import CoinAnalysis, MarketOverview, MorningBrief

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("starting_application")

    # Initialize clients
    app.state.binance = BinanceClient()
    await app.state.binance.connect()

    app.state.coingecko = CoinGeckoClient(settings.COINGECKO_API_KEY)

    # Connect cache
    await cache_manager.connect()

    logger.info("application_started")

    yield

    # Cleanup
    logger.info("shutting_down_application")
    await app.state.binance.close()
    await app.state.coingecko.close()
    await cache_manager.close()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title="AI Crypto Trading Dashboard API",
    description="AI-powered cryptocurrency trading analysis system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "AI Crypto Trading Dashboard API",
        "version": "1.0.0",
        "status": "operational",
        "tracked_coins": settings.coins_list,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cache_stats": await cache_manager.get_stats(),
        "binance_connected": app.state.binance.client is not None,
    }


@app.get("/api/coins")
async def get_tracked_coins():
    """Get list of tracked coins"""
    return {"coins": settings.coins_list}


@app.get("/api/coin/{symbol}")
async def get_coin_analysis(symbol: str):
    """
    Get comprehensive analysis for a specific coin

    Args:
        symbol: Coin symbol (e.g., BTC, ETH)
    """
    symbol = symbol.upper()

    if symbol not in settings.coins_list:
        raise HTTPException(status_code=404, detail=f"Coin {symbol} not tracked")

    try:
        # Check cache first
        cached = await cache_manager.get_signal(symbol)
        if cached:
            logger.info("coin_analysis_cache_hit", symbol=symbol)
            return cached

        # Fetch data from Binance
        ticker_symbol = f"{symbol}USDT"
        price_data = await app.state.binance.get_ticker_24h(ticker_symbol)

        # Get historical data for technical analysis
        klines = await app.state.binance.get_klines(ticker_symbol, interval="1h", limit=200)

        # Calculate technical indicators
        tech_analysis = TechnicalIndicators.analyze_candles(klines)

        # Build TechnicalIndicators model
        from data.models import TechnicalIndicators as TechModel
        technical = TechModel(
            rsi=tech_analysis["rsi"],
            macd=tech_analysis["macd"],
            macd_signal=tech_analysis["macd_signal_line"],
            macd_histogram=tech_analysis["macd_histogram"],
            bb_upper=tech_analysis["bb_upper"],
            bb_middle=tech_analysis["bb_middle"],
            bb_lower=tech_analysis["bb_lower"],
            ema_20=tech_analysis.get("ema_20"),
            ema_50=tech_analysis.get("ema_50"),
            ema_200=tech_analysis.get("ema_200"),
            volume_ratio=tech_analysis.get("volume_ratio"),
        )

        # Build CoinPrice model
        from data.models import CoinPrice
        coin_price = CoinPrice(**price_data)

        # Get AI analysis from Claude
        ai_analysis = await claude_analyzer.analyze_coin(
            coin=symbol,
            price_data=coin_price,
            technical=technical,
            macro=None,  # TODO: Add macro context
        )

        # Generate multi-layer signal
        signal = signal_generator.generate_signal(
            coin=symbol,
            price_data=coin_price,
            technical=technical,
            ai_analysis=ai_analysis,
            macro=None,
        )

        result = {
            "coin": symbol,
            "price": price_data,
            "technical": tech_analysis,
            "ai_analysis": ai_analysis.dict(),
            "signal": signal.dict(),
        }

        # Cache result
        await cache_manager.set_signal(symbol, result)

        return result

    except Exception as e:
        logger.error("coin_analysis_error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/market-overview")
async def get_market_overview():
    """Get overall market overview"""
    try:
        # Get global market data from CoinGecko
        global_data = await app.state.coingecko.get_global_market_data()

        # Get top gainers and losers
        movers = await app.state.coingecko.get_top_gainers_losers(limit=5)

        # Get fear & greed index
        fear_greed = await app.state.coingecko.get_fear_greed_index()

        return {
            "total_market_cap": global_data.get("total_market_cap_usd"),
            "btc_dominance": global_data.get("btc_dominance"),
            "market_cap_change_24h": global_data.get("market_cap_change_24h"),
            "fear_greed_index": fear_greed.get("value") if fear_greed else None,
            "top_gainers": movers["gainers"],
            "top_losers": movers["losers"],
        }

    except Exception as e:
        logger.error("market_overview_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Market overview failed: {str(e)}")


@app.get("/api/signals")
async def get_all_signals():
    """Get trading signals for all tracked coins"""
    results = []

    for symbol in settings.coins_list:
        try:
            # Try cache first
            cached = await cache_manager.get_signal(symbol)
            if cached:
                results.append({
                    "symbol": symbol,
                    "signal": cached["signal"]["signal"],
                    "confidence": cached["signal"]["confidence"],
                    "price": cached["price"]["price"],
                    "change_24h": cached["price"]["change_24h"],
                })
        except Exception as e:
            logger.warning("signal_fetch_error", symbol=symbol, error=str(e))
            continue

    return {"signals": results}


@app.get("/api/morning-brief")
async def get_morning_brief():
    """Get AI-generated morning brief"""
    try:
        # Get market overview
        market = await get_market_overview()

        # Get signals for top coins
        btc_analysis = await get_coin_analysis("BTC")
        eth_analysis = await get_coin_analysis("ETH")
        sol_analysis = await get_coin_analysis("SOL")

        # Build morning brief
        return {
            "date": str(datetime.now().date()),
            "market_status": "BULLISH" if market.get("market_cap_change_24h", 0) > 0 else "BEARISH",
            "top_opportunities": [
                {
                    "coin": btc_analysis["coin"],
                    "signal": btc_analysis["signal"]["signal"],
                    "confidence": btc_analysis["signal"]["confidence"],
                },
                {
                    "coin": eth_analysis["coin"],
                    "signal": eth_analysis["signal"]["signal"],
                    "confidence": eth_analysis["signal"]["confidence"],
                },
                {
                    "coin": sol_analysis["coin"],
                    "signal": sol_analysis["signal"]["signal"],
                    "confidence": sol_analysis["signal"]["confidence"],
                },
            ],
            "macro_alerts": [],
            "risk_level": "MEDIUM",
            "fear_greed": market.get("fear_greed_index"),
        }

    except Exception as e:
        logger.error("morning_brief_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Morning brief failed: {str(e)}")


@app.get("/api/rate-limits")
async def get_rate_limits():
    """Get current rate limit status"""
    from api.rate_limiter import rate_limiter

    return rate_limiter.get_status()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
