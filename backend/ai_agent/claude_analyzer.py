import json
from typing import Dict, Optional
from datetime import datetime
import structlog
from anthropic import AsyncAnthropic

from data.models import (
    SignalType,
    Timeframe,
    AIAnalysis,
    CoinPrice,
    TechnicalIndicators,
    MacroContext,
)
from config.settings import settings

logger = structlog.get_logger()


class ClaudeAnalyzer:
    """
    Claude AI Analyzer

    Provides intelligent crypto analysis using Claude Sonnet 4
    - Coin-specific recommendations
    - Market sentiment analysis
    - Macro context interpretation
    - Kian Hoss strategy integration
    """

    def __init__(self):
        """Initialize Claude client"""
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def analyze_coin(
        self,
        coin: str,
        price_data: CoinPrice,
        technical: TechnicalIndicators,
        macro: Optional[MacroContext] = None,
    ) -> AIAnalysis:
        """
        Comprehensive coin analysis

        Args:
            coin: Coin symbol
            price_data: Current price data
            technical: Technical indicators
            macro: Macro context (optional)

        Returns:
            AI analysis with rating and reasoning
        """
        try:
            prompt = self._build_coin_analysis_prompt(
                coin, price_data, technical, macro
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                temperature=0.7,  # Some creativity but mostly factual
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse Claude's response
            analysis_text = response.content[0].text

            # Extract JSON from response
            analysis_data = self._parse_analysis_response(analysis_text)

            # Build AIAnalysis object
            return AIAnalysis(
                coin=coin,
                rating=SignalType(analysis_data.get("rating", "HOLD")),
                confidence=analysis_data.get("confidence", 50),
                timeframe=Timeframe(analysis_data.get("timeframe", "SWING")),
                entry_zone_low=analysis_data.get("entry_zone_low"),
                entry_zone_high=analysis_data.get("entry_zone_high"),
                target_conservative=analysis_data.get("target_conservative"),
                target_aggressive=analysis_data.get("target_aggressive"),
                stop_loss=analysis_data.get("stop_loss"),
                risk_reward_ratio=analysis_data.get("risk_reward_ratio"),
                reasoning=analysis_data.get("reasoning", "Analysis completed"),
                key_factors=analysis_data.get("key_factors", []),
                risks=analysis_data.get("risks", []),
                position_size_pct=analysis_data.get("position_size_pct"),
            )

        except Exception as e:
            logger.error("claude_analysis_error", coin=coin, error=str(e))

            # Return default HOLD rating on error
            return AIAnalysis(
                coin=coin,
                rating=SignalType.HOLD,
                confidence=0,
                timeframe=Timeframe.SWING,
                reasoning=f"Analysis error: {str(e)}",
                key_factors=[],
                risks=["Unable to analyze due to error"],
            )

    def _build_coin_analysis_prompt(
        self,
        coin: str,
        price_data: CoinPrice,
        technical: TechnicalIndicators,
        macro: Optional[MacroContext],
    ) -> str:
        """Build comprehensive analysis prompt for Claude"""

        # Format macro context
        macro_text = "Not available"
        if macro:
            macro_text = f"""
DXY (Dollar Index): {macro.dxy} - Trend: {macro.dxy_trend or 'Unknown'}
VIX (Market Fear): {macro.vix}
Fed Funds Rate: {macro.fed_funds_rate}%
Fear & Greed Index: {macro.fear_greed_index}/100
Market Phase: {macro.market_phase or 'Unknown'}
"""

        prompt = f"""Analyze {coin} for swing trading opportunity following Kian Hoss's strategy.

CURRENT PRICE DATA:
Symbol: {coin}
Price: ${price_data.price:,.2f}
24h Change: {price_data.change_24h:+.2f}%
7d Change: {price_data.change_7d:+.2f}% (if available)
24h Volume: ${price_data.volume_24h:,.0f}
24h High: ${price_data.high_24h:,.2f}
24h Low: ${price_data.low_24h:,.2f}

TECHNICAL INDICATORS:
RSI: {technical.rsi:.1f}
MACD: {technical.macd:.2f} (Signal: {technical.macd_signal:.2f}, Histogram: {technical.macd_histogram:.2f})
Bollinger Bands:
  - Upper: ${technical.bb_upper:,.2f}
  - Middle: ${technical.bb_middle:,.2f}
  - Lower: ${technical.bb_lower:,.2f}
EMA 20: ${technical.ema_20:,.2f if technical.ema_20 else 'N/A'}
EMA 50: ${technical.ema_50:,.2f if technical.ema_50 else 'N/A'}
EMA 200: ${technical.ema_200:,.2f if technical.ema_200 else 'N/A'}
Volume Ratio: {technical.volume_ratio:.2f}x average (if available)

MACRO CONTEXT:
{macro_text}

KIAN HOSS STRATEGY PRINCIPLES:
1. Focus: Buying dips in uptrends (NOT catching falling knives in bear markets)
2. Timeframe: Swing trades lasting days to weeks
3. Entry: Only when multiple factors align (technical + macro + risk/reward)
4. Risk Management: Strict stop losses, position sizing based on confidence
5. Macro Must Be Supportive: Fed pivot, DXY weakness, risk-on environment

YOUR TASK:
Provide a comprehensive trading recommendation in STRICT JSON format.

Output MUST be valid JSON with this exact structure:
{{
  "rating": "STRONG_BUY" | "BUY" | "WEAK_BUY" | "HOLD" | "WEAK_SELL" | "SELL" | "STRONG_SELL",
  "confidence": 0-100,
  "timeframe": "SCALP" | "DAY" | "SWING" | "POSITION",
  "entry_zone_low": <number>,
  "entry_zone_high": <number>,
  "target_conservative": <number>,
  "target_aggressive": <number>,
  "stop_loss": <number>,
  "risk_reward_ratio": <number>,
  "reasoning": "Detailed explanation of the rating...",
  "key_factors": [
    "Factor 1",
    "Factor 2",
    "Factor 3"
  ],
  "risks": [
    "Risk 1",
    "Risk 2"
  ],
  "position_size_pct": 1-10
}}

RATING GUIDELINES:
- STRONG_BUY: Highly confident opportunity, multiple bullish confluences, good macro
- BUY: Solid entry point, favorable conditions
- WEAK_BUY: Marginal opportunity, some caution
- HOLD: Wait for better setup, unclear direction
- WEAK_SELL: Consider taking profits, weakening momentum
- SELL: Exit recommended, deteriorating conditions
- STRONG_SELL: Strong exit signal, high downside risk

CONFIDENCE GUIDELINES:
- 80-100%: Very high conviction, multiple strong signals
- 60-79%: Good conviction, favorable setup
- 40-59%: Moderate conviction, mixed signals
- 20-39%: Low conviction, uncertain
- 0-19%: Very low conviction, avoid

IMPORTANT:
- Respond ONLY with valid JSON
- No markdown code blocks
- No additional text before or after JSON
- All numeric fields must be numbers not strings
- Reasoning should be 2-4 sentences explaining key factors
- Include specific entry/exit levels based on support/resistance
- Consider current market conditions and macro environment

Provide your analysis now:"""

        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """
        Parse Claude's JSON response

        Args:
            response_text: Raw response from Claude

        Returns:
            Parsed analysis data
        """
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response_text:
                # Extract JSON from code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                # Assume the whole response is JSON
                json_text = response_text.strip()

            # Parse JSON
            data = json.loads(json_text)

            return data

        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), response=response_text[:200])

            # Return default values
            return {
                "rating": "HOLD",
                "confidence": 0,
                "timeframe": "SWING",
                "reasoning": "Failed to parse analysis response",
                "key_factors": [],
                "risks": ["Analysis parsing failed"],
            }

    async def analyze_market_sentiment(
        self, market_data: Dict, macro: Optional[MacroContext] = None
    ) -> Dict:
        """
        Analyze overall market sentiment

        Args:
            market_data: Market overview data
            macro: Macro context

        Returns:
            Market sentiment analysis
        """
        try:
            prompt = f"""Analyze the current cryptocurrency market sentiment.

MARKET DATA:
Total Market Cap: ${market_data.get('total_market_cap', 0):,.0f}
24h Change: {market_data.get('market_cap_change_24h', 0):+.2f}%
BTC Dominance: {market_data.get('btc_dominance', 0):.1f}%

Top Gainers:
{self._format_coin_list(market_data.get('top_gainers', []))}

Top Losers:
{self._format_coin_list(market_data.get('top_losers', []))}

MACRO CONTEXT:
{"Available" if macro else "Not available"}

Provide analysis in JSON format:
{{
  "sentiment": "BULLISH" | "NEUTRAL" | "BEARISH",
  "sentiment_score": 0-100,
  "key_drivers": ["driver1", "driver2", "driver3"],
  "top_opportunities": ["opp1", "opp2", "opp3"],
  "top_risks": ["risk1", "risk2", "risk3"],
  "market_phase": "ACCUMULATION" | "MARKUP" | "DISTRIBUTION" | "MARKDOWN",
  "recommendation": "Brief trading recommendation..."
}}

Respond ONLY with valid JSON:"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            return self._parse_analysis_response(response_text)

        except Exception as e:
            logger.error("market_sentiment_error", error=str(e))
            return {
                "sentiment": "NEUTRAL",
                "sentiment_score": 50,
                "key_drivers": [],
                "top_opportunities": [],
                "top_risks": [],
                "market_phase": "UNKNOWN",
                "recommendation": "Unable to analyze market sentiment",
            }

    def _format_coin_list(self, coins: list) -> str:
        """Format list of coins for prompt"""
        if not coins:
            return "None"

        return "\n".join(
            [
                f"  - {c.get('symbol', 'N/A')}: {c.get('change_24h', 0):+.2f}%"
                for c in coins[:5]
            ]
        )

    async def explain_trade(self, coin: str, signal: SignalType, context: Dict) -> str:
        """
        Generate educational explanation for a trade signal

        Args:
            coin: Coin symbol
            signal: Trading signal
            context: Context data

        Returns:
            Educational explanation
        """
        try:
            prompt = f"""Explain in simple terms why {coin} has a {signal.value} signal.

Context:
{json.dumps(context, indent=2)}

Provide a clear, educational explanation (2-3 paragraphs) that helps a trader understand:
1. WHY this signal was generated
2. WHAT key factors support it
3. WHAT to watch for (risks/invalidation)

Write in a friendly, educational tone. No JSON, just clear text:"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            logger.error("explain_trade_error", error=str(e))
            return f"Unable to generate explanation for {coin} {signal.value} signal."


# Global Claude analyzer instance
claude_analyzer = ClaudeAnalyzer()
