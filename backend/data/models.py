from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """Trading signal types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WEAK_BUY = "WEAK_BUY"
    HOLD = "HOLD"
    WEAK_SELL = "WEAK_SELL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class Timeframe(str, Enum):
    """Trading timeframes"""
    SCALP = "SCALP"  # Minutes to hours
    DAY = "DAY"  # Hours to 1 day
    SWING = "SWING"  # Days to weeks
    POSITION = "POSITION"  # Weeks to months


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""
    rsi: float = Field(..., description="RSI value (0-100)")
    macd: float = Field(..., description="MACD value")
    macd_signal: float = Field(..., description="MACD signal line")
    macd_histogram: float = Field(..., description="MACD histogram")
    bb_upper: float = Field(..., description="Bollinger Band upper")
    bb_middle: float = Field(..., description="Bollinger Band middle")
    bb_lower: float = Field(..., description="Bollinger Band lower")
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    volume_ratio: Optional[float] = Field(None, description="Volume vs avg (ratio)")


class OnChainMetrics(BaseModel):
    """On-chain metrics (optional)"""
    sopr: Optional[float] = Field(None, description="Spent Output Profit Ratio")
    mvrv: Optional[float] = Field(None, description="MVRV Ratio")
    exchange_inflow: Optional[float] = None
    exchange_outflow: Optional[float] = None
    exchange_net_flow: Optional[float] = None
    whale_activity: Optional[str] = None


class MacroContext(BaseModel):
    """Macroeconomic context"""
    dxy: Optional[float] = Field(None, description="Dollar Index")
    dxy_trend: Optional[str] = None
    vix: Optional[float] = Field(None, description="Volatility Index")
    fed_funds_rate: Optional[float] = None
    fear_greed_index: Optional[int] = Field(None, ge=0, le=100)
    market_phase: Optional[str] = None


class CoinPrice(BaseModel):
    """Current coin price data"""
    symbol: str
    price: float
    change_24h: float
    change_7d: Optional[float] = None
    volume_24h: float
    market_cap: Optional[float] = None
    high_24h: float
    low_24h: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIAnalysis(BaseModel):
    """Claude AI analysis result"""
    coin: str
    rating: SignalType
    confidence: int = Field(..., ge=0, le=100, description="Confidence score 0-100%")
    timeframe: Timeframe
    entry_zone_low: Optional[float] = None
    entry_zone_high: Optional[float] = None
    target_conservative: Optional[float] = None
    target_aggressive: Optional[float] = None
    stop_loss: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    reasoning: str = Field(..., description="Detailed reasoning for the rating")
    key_factors: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    position_size_pct: Optional[float] = Field(None, description="Recommended % of portfolio")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MultiLayerSignal(BaseModel):
    """Aggregated signal from multiple layers"""
    coin: str
    signal: SignalType
    overall_score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)

    # Layer breakdowns
    technical_score: int = Field(..., ge=0, le=100)
    on_chain_score: Optional[int] = Field(None, ge=0, le=100)
    macro_score: Optional[int] = Field(None, ge=0, le=100)
    sentiment_score: Optional[int] = Field(None, ge=0, le=100)

    # Trade details
    action: str
    entry_zone: Optional[str] = None
    targets: List[float] = Field(default_factory=list)
    stop_loss: Optional[float] = None
    position_size_pct: Optional[float] = None
    timeframe: str = "7-14 days"

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CoinAnalysis(BaseModel):
    """Complete analysis for a coin"""
    coin: str
    price_data: CoinPrice
    technical: TechnicalIndicators
    on_chain: Optional[OnChainMetrics] = None
    ai_analysis: Optional[AIAnalysis] = None
    signal: MultiLayerSignal
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class MarketOverview(BaseModel):
    """Overall market overview"""
    total_market_cap: Optional[float] = None
    btc_dominance: Optional[float] = None
    fear_greed_index: Optional[int] = None
    market_sentiment: str = "NEUTRAL"  # BULLISH, NEUTRAL, BEARISH
    top_gainers: List[Dict[str, Any]] = Field(default_factory=list)
    top_losers: List[Dict[str, Any]] = Field(default_factory=list)
    macro_context: Optional[MacroContext] = None
    key_drivers: List[str] = Field(default_factory=list)
    top_opportunities: List[str] = Field(default_factory=list)
    top_risks: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MorningBrief(BaseModel):
    """Daily morning brief"""
    date: str
    market_status: str  # BULLISH, NEUTRAL, BEARISH
    top_opportunities: List[Dict[str, Any]]
    macro_alerts: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    recommended_actions: List[str]
    key_events_today: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertConfig(BaseModel):
    """Alert configuration"""
    coin: str
    alert_type: str  # PRICE, SIGNAL, TECHNICAL, MACRO
    condition: str
    threshold: Optional[float] = None
    enabled: bool = True
    last_triggered: Optional[datetime] = None
