import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import structlog

logger = structlog.get_logger()


class TechnicalIndicators:
    """
    Technical Analysis Indicators

    Implements:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - EMA (Exponential Moving Average)
    - Volume Analysis
    """

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate RSI

        Args:
            prices: List of closing prices
            period: RSI period (default 14)

        Returns:
            RSI value (0-100) or None
        """
        if len(prices) < period + 1:
            logger.warning("insufficient_data_for_rsi", required=period + 1, got=len(prices))
            return None

        try:
            df = pd.DataFrame({"close": prices})

            # Calculate price changes
            delta = df["close"].diff()

            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)

            # Calculate average gain and loss
            avg_gain = gains.rolling(window=period).mean()
            avg_loss = losses.rolling(window=period).mean()

            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1])

        except Exception as e:
            logger.error("rsi_calculation_error", error=str(e))
            return None

    @staticmethod
    def calculate_macd(
        prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Optional[Dict]:
        """
        Calculate MACD

        Args:
            prices: List of closing prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)

        Returns:
            Dict with macd, signal, and histogram
        """
        if len(prices) < slow + signal:
            logger.warning("insufficient_data_for_macd", required=slow + signal, got=len(prices))
            return None

        try:
            df = pd.DataFrame({"close": prices})

            # Calculate EMAs
            ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
            ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

            # MACD line
            macd_line = ema_fast - ema_slow

            # Signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()

            # Histogram
            histogram = macd_line - signal_line

            return {
                "macd": float(macd_line.iloc[-1]),
                "signal": float(signal_line.iloc[-1]),
                "histogram": float(histogram.iloc[-1]),
            }

        except Exception as e:
            logger.error("macd_calculation_error", error=str(e))
            return None

    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Optional[Dict]:
        """
        Calculate Bollinger Bands

        Args:
            prices: List of closing prices
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2)

        Returns:
            Dict with upper, middle, and lower bands
        """
        if len(prices) < period:
            logger.warning("insufficient_data_for_bollinger", required=period, got=len(prices))
            return None

        try:
            df = pd.DataFrame({"close": prices})

            # Middle band (SMA)
            middle_band = df["close"].rolling(window=period).mean()

            # Standard deviation
            std = df["close"].rolling(window=period).std()

            # Upper and lower bands
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)

            return {
                "upper": float(upper_band.iloc[-1]),
                "middle": float(middle_band.iloc[-1]),
                "lower": float(lower_band.iloc[-1]),
            }

        except Exception as e:
            logger.error("bollinger_calculation_error", error=str(e))
            return None

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average

        Args:
            prices: List of closing prices
            period: EMA period

        Returns:
            EMA value
        """
        if len(prices) < period:
            return None

        try:
            df = pd.DataFrame({"close": prices})
            ema = df["close"].ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1])

        except Exception as e:
            logger.error("ema_calculation_error", error=str(e))
            return None

    @staticmethod
    def calculate_volume_ratio(
        volumes: List[float], period: int = 20
    ) -> Optional[float]:
        """
        Calculate volume ratio (current vs average)

        Args:
            volumes: List of volume values
            period: Period for average calculation

        Returns:
            Volume ratio
        """
        if len(volumes) < period + 1:
            return None

        try:
            df = pd.DataFrame({"volume": volumes})

            # Average volume
            avg_volume = df["volume"].iloc[:-1].tail(period).mean()

            # Current volume
            current_volume = df["volume"].iloc[-1]

            if avg_volume == 0:
                return None

            return float(current_volume / avg_volume)

        except Exception as e:
            logger.error("volume_ratio_calculation_error", error=str(e))
            return None

    @staticmethod
    def analyze_candles(ohlcv_data: List[Dict]) -> Dict:
        """
        Comprehensive analysis of OHLCV data

        Args:
            ohlcv_data: List of OHLCV candles

        Returns:
            Dict with all technical indicators
        """
        if len(ohlcv_data) < 50:
            logger.warning(
                "insufficient_candles_for_analysis",
                required=50,
                got=len(ohlcv_data),
            )
            return {}

        try:
            # Extract price and volume data
            closes = [c["close"] for c in ohlcv_data]
            volumes = [c["volume"] for c in ohlcv_data]

            # Calculate indicators
            rsi = TechnicalIndicators.calculate_rsi(closes)
            macd_data = TechnicalIndicators.calculate_macd(closes)
            bb_data = TechnicalIndicators.calculate_bollinger_bands(closes)

            ema_20 = TechnicalIndicators.calculate_ema(closes, 20)
            ema_50 = TechnicalIndicators.calculate_ema(closes, 50)
            ema_200 = TechnicalIndicators.calculate_ema(closes, 200)

            volume_ratio = TechnicalIndicators.calculate_volume_ratio(volumes)

            # Current price
            current_price = closes[-1]

            # Determine trend
            trend = "UNKNOWN"
            if ema_20 and ema_50 and ema_200:
                if current_price > ema_200:
                    if ema_20 > ema_50 > ema_200:
                        trend = "STRONG_UPTREND"
                    else:
                        trend = "UPTREND"
                elif current_price < ema_200:
                    if ema_20 < ema_50 < ema_200:
                        trend = "STRONG_DOWNTREND"
                    else:
                        trend = "DOWNTREND"
                else:
                    trend = "SIDEWAYS"

            # RSI interpretation
            rsi_signal = "NEUTRAL"
            if rsi:
                if rsi < 30:
                    rsi_signal = "OVERSOLD"
                elif rsi > 70:
                    rsi_signal = "OVERBOUGHT"
                elif rsi < 40:
                    rsi_signal = "BEARISH"
                elif rsi > 60:
                    rsi_signal = "BULLISH"

            # MACD interpretation
            macd_signal = "NEUTRAL"
            if macd_data:
                if macd_data["histogram"] > 0:
                    if macd_data["macd"] > macd_data["signal"]:
                        macd_signal = "BULLISH"
                else:
                    if macd_data["macd"] < macd_data["signal"]:
                        macd_signal = "BEARISH"

            # Bollinger Bands interpretation
            bb_signal = "NEUTRAL"
            if bb_data:
                bb_width = (
                    (bb_data["upper"] - bb_data["lower"]) / bb_data["middle"]
                ) * 100

                if current_price < bb_data["lower"]:
                    bb_signal = "OVERSOLD"
                elif current_price > bb_data["upper"]:
                    bb_signal = "OVERBOUGHT"
                elif bb_width < 10:
                    bb_signal = "SQUEEZE"  # Potential breakout

            return {
                "rsi": rsi,
                "rsi_signal": rsi_signal,
                "macd": macd_data["macd"] if macd_data else None,
                "macd_signal_line": macd_data["signal"] if macd_data else None,
                "macd_histogram": macd_data["histogram"] if macd_data else None,
                "macd_signal": macd_signal,
                "bb_upper": bb_data["upper"] if bb_data else None,
                "bb_middle": bb_data["middle"] if bb_data else None,
                "bb_lower": bb_data["lower"] if bb_data else None,
                "bb_signal": bb_signal,
                "ema_20": ema_20,
                "ema_50": ema_50,
                "ema_200": ema_200,
                "trend": trend,
                "volume_ratio": volume_ratio,
                "current_price": current_price,
            }

        except Exception as e:
            logger.error("candle_analysis_error", error=str(e))
            return {}

    @staticmethod
    def calculate_technical_score(indicators: Dict) -> int:
        """
        Calculate overall technical score (0-100)

        Args:
            indicators: Dict of technical indicators

        Returns:
            Score from 0 (very bearish) to 100 (very bullish)
        """
        score = 50  # Neutral starting point

        # RSI contribution (0-20 points)
        if indicators.get("rsi"):
            rsi = indicators["rsi"]
            if rsi < 30:
                score += 20  # Very oversold = bullish
            elif rsi < 40:
                score += 10
            elif rsi > 70:
                score -= 20  # Very overbought = bearish
            elif rsi > 60:
                score -= 10

        # MACD contribution (0-20 points)
        macd_signal = indicators.get("macd_signal", "NEUTRAL")
        if macd_signal == "BULLISH":
            score += 20
        elif macd_signal == "BEARISH":
            score -= 20

        # Trend contribution (0-30 points)
        trend = indicators.get("trend", "UNKNOWN")
        if trend == "STRONG_UPTREND":
            score += 30
        elif trend == "UPTREND":
            score += 15
        elif trend == "STRONG_DOWNTREND":
            score -= 30
        elif trend == "DOWNTREND":
            score -= 15

        # Bollinger Bands contribution (0-15 points)
        bb_signal = indicators.get("bb_signal", "NEUTRAL")
        if bb_signal == "OVERSOLD":
            score += 15
        elif bb_signal == "OVERBOUGHT":
            score -= 15
        elif bb_signal == "SQUEEZE":
            score += 5  # Potential breakout

        # Volume contribution (0-15 points)
        volume_ratio = indicators.get("volume_ratio")
        if volume_ratio:
            if volume_ratio > 1.5:
                # High volume supports the trend
                if score > 50:
                    score += 15
                else:
                    score -= 15
            elif volume_ratio < 0.5:
                # Low volume = weak trend
                if score > 50:
                    score -= 5
                else:
                    score += 5

        # Clamp score between 0 and 100
        return max(0, min(100, score))
