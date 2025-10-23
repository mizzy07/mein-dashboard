const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CoinAnalysis {
  coin: string;
  price: {
    symbol: string;
    price: number;
    change_24h: number;
    change_7d?: number;
    volume_24h: number;
    high_24h: number;
    low_24h: number;
  };
  technical: {
    rsi: number;
    rsi_signal: string;
    macd: number;
    macd_signal: string;
    trend: string;
    bb_upper: number;
    bb_middle: number;
    bb_lower: number;
    ema_20?: number;
    ema_50?: number;
    ema_200?: number;
  };
  ai_analysis: {
    coin: string;
    rating: string;
    confidence: number;
    timeframe: string;
    entry_zone_low?: number;
    entry_zone_high?: number;
    target_conservative?: number;
    target_aggressive?: number;
    stop_loss?: number;
    risk_reward_ratio?: number;
    reasoning: string;
    key_factors: string[];
    risks: string[];
    position_size_pct?: number;
  };
  signal: {
    coin: string;
    signal: string;
    overall_score: number;
    confidence: number;
    technical_score: number;
    macro_score?: number;
    sentiment_score?: number;
    action: string;
    entry_zone?: string;
    targets: number[];
    stop_loss?: number;
    position_size_pct?: number;
    timeframe: string;
  };
}

export interface MarketOverview {
  total_market_cap: number;
  btc_dominance: number;
  market_cap_change_24h: number;
  fear_greed_index?: number;
  top_gainers: Array<{
    symbol: string;
    name: string;
    change_24h: number;
    price: number;
  }>;
  top_losers: Array<{
    symbol: string;
    name: string;
    change_24h: number;
    price: number;
  }>;
}

export interface SignalSummary {
  symbol: string;
  signal: string;
  confidence: number;
  price: number;
  change_24h: number;
}

export interface MorningBrief {
  date: string;
  market_status: string;
  top_opportunities: Array<{
    coin: string;
    signal: string;
    confidence: number;
  }>;
  macro_alerts: string[];
  risk_level: string;
  fear_greed?: number;
}

class TradingAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`);

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Get comprehensive analysis for a coin
  async getCoinAnalysis(symbol: string): Promise<CoinAnalysis> {
    return this.request<CoinAnalysis>(`/api/coin/${symbol}`);
  }

  // Get market overview
  async getMarketOverview(): Promise<MarketOverview> {
    return this.request<MarketOverview>('/api/market-overview');
  }

  // Get all trading signals
  async getAllSignals(): Promise<{ signals: SignalSummary[] }> {
    return this.request<{ signals: SignalSummary[] }>('/api/signals');
  }

  // Get morning brief
  async getMorningBrief(): Promise<MorningBrief> {
    return this.request<MorningBrief>('/api/morning-brief');
  }

  // Get tracked coins list
  async getTrackedCoins(): Promise<{ coins: string[] }> {
    return this.request<{ coins: string[] }>('/api/coins');
  }

  // Health check
  async healthCheck(): Promise<any> {
    return this.request('/health');
  }
}

export const tradingAPI = new TradingAPI();
