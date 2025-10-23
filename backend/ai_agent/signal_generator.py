from typing import Dict, Optional, List
from datetime import datetime
import structlog

from data.models import (
    SignalType,
    MultiLayerSignal,
    CoinPrice,
    TechnicalIndicators,
    AIAnalysis,
    MacroContext,
)
from indicators.technical import TechnicalIndicators as TechCalc

logger = structlog.get_logger()


class SignalGenerator:
    """
    Multi-Layer Signal Generation Engine

    Combines multiple analysis layers:
    1. Technical Analysis (40% weight)
    2. On-Chain Metrics (30% weight) - if available
    3. Macro Context (20% weight) - if available
    4. AI Sentiment (10% weight)

    Generates final trading signals with confidence scores
    """

    # Signal type thresholds
    SIGNAL_THRESHOLDS = {
        "STRONG_BUY": 80,
        "BUY": 65,
        "WEAK_BUY": 55,
        "HOLD": 45,
        "WEAK_SELL": 35,
        "SELL": 20,
        "STRONG_SELL": 0,
    }

    def __init__(self):
        """Initialize signal generator"""
        pass

    def generate_signal(
        self,
        coin: str,
        price_data: CoinPrice,
        technical: TechnicalIndicators,
        ai_analysis: Optional[AIAnalysis] = None,
        macro: Optional[MacroContext] = None,
    ) -> MultiLayerSignal:
        """
        Generate comprehensive trading signal

        Args:
            coin: Coin symbol
            price_data: Current price data
            technical: Technical indicators
            ai_analysis: Claude AI analysis (optional)
            macro: Macro context (optional)

        Returns:
            Multi-layer trading signal
        """
        try:
            # Calculate layer scores
            technical_score = self._calculate_technical_score(technical)
            macro_score = (
                self._calculate_macro_score(macro, price_data) if macro else None
            )
            sentiment_score = (
                self._map_ai_to_score(ai_analysis) if ai_analysis else None
            )

            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(
                technical_score=technical_score,
                macro_score=macro_score,
                sentiment_score=sentiment_score,
            )

            # Determine signal type
            signal_type = self._score_to_signal_type(overall_score)

            # Calculate confidence
            confidence = self._calculate_confidence(
                technical_score, macro_score, sentiment_score, ai_analysis
            )

            # Determine action and levels
            action, entry_zone, targets, stop_loss = self._determine_trade_levels(
                signal_type, price_data, technical, ai_analysis
            )

            # Position sizing recommendation
            position_size = self._recommend_position_size(
                signal_type, confidence, price_data
            )

            # Estimate timeframe
            timeframe = ai_analysis.timeframe.value if ai_analysis else "7-14 days"

            return MultiLayerSignal(
                coin=coin,
                signal=signal_type,
                overall_score=overall_score,
                confidence=confidence,
                technical_score=technical_score,
                macro_score=macro_score,
                sentiment_score=sentiment_score,
                action=action,
                entry_zone=entry_zone,
                targets=targets,
                stop_loss=stop_loss,
                position_size_pct=position_size,
                timeframe=timeframe,
            )

        except Exception as e:
            logger.error("signal_generation_error", coin=coin, error=str(e))

            # Return default HOLD signal on error
            return MultiLayerSignal(
                coin=coin,
                signal=SignalType.HOLD,
                overall_score=50,
                confidence=0,
                technical_score=50,
                action="Wait for better setup",
                timeframe="N/A",
            )

    def _calculate_technical_score(self, technical: TechnicalIndicators) -> int:
        """Calculate technical analysis score (0-100)"""
        try:
            # Build indicators dict for TechCalc
            indicators = {
                "rsi": technical.rsi,
                "macd_signal": "BULLISH"
                if technical.macd_histogram > 0
                else "BEARISH",
                "trend": self._determine_trend(technical),
                "bb_signal": self._determine_bb_signal(technical),
                "volume_ratio": technical.volume_ratio,
            }

            return TechCalc.calculate_technical_score(indicators)

        except Exception as e:
            logger.error("technical_score_error", error=str(e))
            return 50  # Neutral on error

    def _determine_trend(self, technical: TechnicalIndicators) -> str:
        """Determine trend from EMAs"""
        if not all([technical.ema_20, technical.ema_50, technical.ema_200]):
            return "UNKNOWN"

        current_price = (technical.bb_middle or 0)  # Use BB middle as proxy

        if current_price > technical.ema_200:
            if (
                technical.ema_20 > technical.ema_50
                and technical.ema_50 > technical.ema_200
            ):
                return "STRONG_UPTREND"
            return "UPTREND"
        elif current_price < technical.ema_200:
            if (
                technical.ema_20 < technical.ema_50
                and technical.ema_50 < technical.ema_200
            ):
                return "STRONG_DOWNTREND"
            return "DOWNTREND"
        else:
            return "SIDEWAYS"

    def _determine_bb_signal(self, technical: TechnicalIndicators) -> str:
        """Determine Bollinger Bands signal"""
        if not all([technical.bb_upper, technical.bb_middle, technical.bb_lower]):
            return "NEUTRAL"

        current_price = technical.bb_middle  # Proxy

        if current_price < technical.bb_lower:
            return "OVERSOLD"
        elif current_price > technical.bb_upper:
            return "OVERBOUGHT"
        else:
            return "NEUTRAL"

    def _calculate_macro_score(
        self, macro: MacroContext, price_data: CoinPrice
    ) -> int:
        """Calculate macro context score (0-100)"""
        score = 50  # Neutral start

        try:
            # DXY (Dollar Index) - Inverse correlation with crypto
            if macro.dxy:
                if macro.dxy < 95:
                    score += 20  # Weak dollar = bullish crypto
                elif macro.dxy < 100:
                    score += 10
                elif macro.dxy > 110:
                    score -= 20  # Strong dollar = bearish crypto
                elif macro.dxy > 105:
                    score -= 10

            # VIX (Volatility Index)
            if macro.vix:
                if macro.vix < 15:
                    score += 15  # Low fear = bullish
                elif macro.vix < 20:
                    score += 5
                elif macro.vix > 30:
                    score -= 15  # High fear = bearish
                elif macro.vix > 25:
                    score -= 5

            # Fear & Greed Index
            if macro.fear_greed_index:
                fgi = macro.fear_greed_index
                if fgi < 25:
                    score += 15  # Extreme fear = buy opportunity
                elif fgi < 40:
                    score += 5
                elif fgi > 75:
                    score -= 15  # Extreme greed = sell signal
                elif fgi > 60:
                    score -= 5

            return max(0, min(100, score))

        except Exception as e:
            logger.error("macro_score_error", error=str(e))
            return 50

    def _map_ai_to_score(self, ai_analysis: AIAnalysis) -> int:
        """Map AI analysis to sentiment score"""
        # Map signal type to score
        signal_map = {
            SignalType.STRONG_BUY: 95,
            SignalType.BUY: 75,
            SignalType.WEAK_BUY: 60,
            SignalType.HOLD: 50,
            SignalType.WEAK_SELL: 40,
            SignalType.SELL: 25,
            SignalType.STRONG_SELL: 5,
        }

        base_score = signal_map.get(ai_analysis.rating, 50)

        # Adjust based on confidence
        confidence_factor = ai_analysis.confidence / 100
        adjusted_score = 50 + (base_score - 50) * confidence_factor

        return int(adjusted_score)

    def _calculate_overall_score(
        self,
        technical_score: int,
        macro_score: Optional[int],
        sentiment_score: Optional[int],
    ) -> int:
        """Calculate weighted overall score"""

        # Adjust weights based on available data
        if macro_score is not None and sentiment_score is not None:
            # All layers available
            score = (
                technical_score * 0.4
                + macro_score * 0.3
                + sentiment_score * 0.3
            )
        elif macro_score is not None:
            # No sentiment
            score = technical_score * 0.6 + macro_score * 0.4
        elif sentiment_score is not None:
            # No macro
            score = technical_score * 0.6 + sentiment_score * 0.4
        else:
            # Only technical
            score = technical_score

        return int(score)

    def _score_to_signal_type(self, score: int) -> SignalType:
        """Convert score to signal type"""
        if score >= 80:
            return SignalType.STRONG_BUY
        elif score >= 65:
            return SignalType.BUY
        elif score >= 55:
            return SignalType.WEAK_BUY
        elif score >= 45:
            return SignalType.HOLD
        elif score >= 35:
            return SignalType.WEAK_SELL
        elif score >= 20:
            return SignalType.SELL
        else:
            return SignalType.STRONG_SELL

    def _calculate_confidence(
        self,
        technical_score: int,
        macro_score: Optional[int],
        sentiment_score: Optional[int],
        ai_analysis: Optional[AIAnalysis],
    ) -> int:
        """Calculate overall confidence level"""

        # Start with AI confidence if available
        if ai_analysis:
            confidence = ai_analysis.confidence
        else:
            confidence = 50

        # Boost confidence if all scores agree
        scores = [s for s in [technical_score, macro_score, sentiment_score] if s is not None]

        if len(scores) >= 2:
            # Check if scores are aligned
            avg_score = sum(scores) / len(scores)
            variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

            # Low variance = high agreement = boost confidence
            if variance < 100:  # Scores within ~10 points
                confidence = min(100, confidence + 10)
            elif variance > 400:  # Scores diverge significantly
                confidence = max(0, confidence - 15)

        return confidence

    def _determine_trade_levels(
        self,
        signal_type: SignalType,
        price_data: CoinPrice,
        technical: TechnicalIndicators,
        ai_analysis: Optional[AIAnalysis],
    ) -> tuple:
        """Determine entry, targets, and stop loss"""

        current_price = price_data.price

        # Use AI recommendations if available
        if ai_analysis and ai_analysis.entry_zone_low:
            entry_zone = (
                f"${ai_analysis.entry_zone_low:,.0f}-${ai_analysis.entry_zone_high:,.0f}"
            )
            targets = [
                ai_analysis.target_conservative or current_price * 1.1,
                ai_analysis.target_aggressive or current_price * 1.2,
            ]
            stop_loss = ai_analysis.stop_loss or current_price * 0.9
        else:
            # Calculate based on technical levels
            if signal_type in [SignalType.STRONG_BUY, SignalType.BUY]:
                entry_low = current_price * 0.98
                entry_high = current_price * 1.02
                entry_zone = f"${entry_low:,.0f}-${entry_high:,.0f}"
                targets = [current_price * 1.1, current_price * 1.2, current_price * 1.3]
                stop_loss = technical.bb_lower or current_price * 0.92

            elif signal_type in [SignalType.WEAK_SELL, SignalType.SELL, SignalType.STRONG_SELL]:
                entry_zone = f"Current price (${current_price:,.0f})"
                targets = []  # Exit, not entry
                stop_loss = None
            else:  # HOLD, WEAK_BUY
                entry_zone = "Wait for better setup"
                targets = []
                stop_loss = None

        # Determine action
        action_map = {
            SignalType.STRONG_BUY: "Enter Long Position (High Conviction)",
            SignalType.BUY: "Enter Long Position",
            SignalType.WEAK_BUY: "Scale In (Small Position)",
            SignalType.HOLD: "Wait / Hold Current Positions",
            SignalType.WEAK_SELL: "Consider Taking Profits",
            SignalType.SELL: "Exit Long Positions",
            SignalType.STRONG_SELL: "Exit All Positions (Urgent)",
        }

        action = action_map.get(signal_type, "Hold")

        return action, entry_zone, targets, stop_loss

    def _recommend_position_size(
        self, signal_type: SignalType, confidence: int, price_data: CoinPrice
    ) -> float:
        """Recommend position size as % of portfolio"""

        # Base position size on signal strength
        base_size_map = {
            SignalType.STRONG_BUY: 10.0,
            SignalType.BUY: 7.0,
            SignalType.WEAK_BUY: 3.0,
            SignalType.HOLD: 0.0,
            SignalType.WEAK_SELL: 0.0,
            SignalType.SELL: 0.0,
            SignalType.STRONG_SELL: 0.0,
        }

        base_size = base_size_map.get(signal_type, 0.0)

        # Adjust based on confidence
        confidence_factor = confidence / 100
        adjusted_size = base_size * confidence_factor

        # Consider volatility (24h change)
        volatility = abs(price_data.change_24h)
        if volatility > 10:  # High volatility
            adjusted_size *= 0.7
        elif volatility > 5:
            adjusted_size *= 0.85

        return round(adjusted_size, 1)


# Global signal generator instance
signal_generator = SignalGenerator()
