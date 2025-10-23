import { useEffect, useState } from 'react';
import { BarChart3, Activity, Zap } from 'lucide-react';
import AIInsights from './AIInsights';
import LiveCoinCard from './LiveCoinCard';
import { tradingAPI, MarketOverview } from '../services/api';

const TRACKED_COINS = ['BTC', 'ETH', 'SOL', 'BNB', 'AVAX', 'LINK', 'MATIC', 'DOT', 'ADA', 'XRP', 'INJ', 'SEI', 'ARB', 'OP', 'TIA', 'SUI'];

const LiveDashboard = () => {
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    checkBackendStatus();
    loadMarketOverview();

    // Refresh market overview every 5 minutes
    const interval = setInterval(loadMarketOverview, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      await tradingAPI.healthCheck();
      setIsLive(true);
    } catch (err) {
      setIsLive(false);
      console.error('Backend health check failed:', err);
    }
  };

  const loadMarketOverview = async () => {
    try {
      const data = await tradingAPI.getMarketOverview();
      setMarketOverview(data);
    } catch (err) {
      console.error('Market overview error:', err);
    }
  };

  const getFearGreedColor = (value?: number) => {
    if (!value) return 'text-slate-400';
    if (value < 25) return 'text-trade-red';
    if (value < 45) return 'text-orange-500';
    if (value < 55) return 'text-yellow-500';
    if (value < 75) return 'text-green-500';
    return 'text-trade-green';
  };

  const getFearGreedLabel = (value?: number) => {
    if (!value) return 'N/A';
    if (value < 25) return 'Extreme Fear';
    if (value < 45) return 'Fear';
    if (value < 55) return 'Neutral';
    if (value < 75) return 'Greed';
    return 'Extreme Greed';
  };

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <header className="bg-dark-card border-b border-dark-border">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Crypto Trading Dashboard</h1>
                <p className="text-slate-400 text-sm">Powered by Claude AI & Real-time Data</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Live Status */}
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-trade-green animate-pulse' : 'bg-slate-600'}`}></div>
                <span className="text-sm text-slate-400">
                  {isLive ? 'Live' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <div className="space-y-6">
          {/* Market Overview Bar */}
          {marketOverview && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-slate-400 text-sm mb-1">Total Market Cap</p>
                  <p className="text-xl font-bold text-white">
                    ${(marketOverview.total_market_cap / 1e12).toFixed(2)}T
                  </p>
                  <p className={`text-sm ${marketOverview.market_cap_change_24h >= 0 ? 'text-trade-green' : 'text-trade-red'}`}>
                    {marketOverview.market_cap_change_24h >= 0 ? '+' : ''}
                    {marketOverview.market_cap_change_24h.toFixed(2)}%
                  </p>
                </div>

                <div>
                  <p className="text-slate-400 text-sm mb-1">BTC Dominance</p>
                  <p className="text-xl font-bold text-white">
                    {marketOverview.btc_dominance.toFixed(1)}%
                  </p>
                </div>

                <div>
                  <p className="text-slate-400 text-sm mb-1">Fear & Greed Index</p>
                  <p className={`text-xl font-bold ${getFearGreedColor(marketOverview.fear_greed_index)}`}>
                    {marketOverview.fear_greed_index || 'N/A'}
                  </p>
                  <p className="text-sm text-slate-400">
                    {getFearGreedLabel(marketOverview.fear_greed_index)}
                  </p>
                </div>

                <div>
                  <p className="text-slate-400 text-sm mb-1">Status</p>
                  <div className="flex items-center gap-2">
                    <Activity size={20} className="text-blue-500" />
                    <p className="text-lg font-semibold text-slate-200">
                      {isLive ? 'Analyzing Markets' : 'Connecting...'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            {/* Coins Grid - Takes 3 columns */}
            <div className="xl:col-span-3">
              <div className="flex items-center gap-2 mb-4">
                <Zap size={20} className="text-yellow-500" />
                <h2 className="text-xl font-bold text-slate-200">Live Crypto Analysis</h2>
                <span className="text-sm text-slate-400">({TRACKED_COINS.length} coins tracked)</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {TRACKED_COINS.map((symbol) => (
                  <LiveCoinCard key={symbol} symbol={symbol} />
                ))}
              </div>
            </div>

            {/* AI Insights Sidebar - Takes 1 column */}
            <div className="xl:col-span-1">
              <AIInsights />
            </div>
          </div>

          {/* Top Movers */}
          {marketOverview && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Top Gainers */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span className="text-trade-green">▲</span>
                  Top Gainers (24h)
                </h3>
                <div className="space-y-3">
                  {marketOverview.top_gainers.slice(0, 5).map((coin, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                      <div>
                        <p className="font-semibold text-slate-200">{coin.symbol.toUpperCase()}</p>
                        <p className="text-sm text-slate-400">{coin.name}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-trade-green">+{coin.change_24h.toFixed(2)}%</p>
                        <p className="text-sm text-slate-400">${coin.price.toFixed(4)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Losers */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span className="text-trade-red">▼</span>
                  Top Losers (24h)
                </h3>
                <div className="space-y-3">
                  {marketOverview.top_losers.slice(0, 5).map((coin, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                      <div>
                        <p className="font-semibold text-slate-200">{coin.symbol.toUpperCase()}</p>
                        <p className="text-sm text-slate-400">{coin.name}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-trade-red">{coin.change_24h.toFixed(2)}%</p>
                        <p className="text-sm text-slate-400">${coin.price.toFixed(4)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-dark-card border-t border-dark-border mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-slate-400">
            <p>AI Crypto Trading Dashboard - Powered by Claude AI</p>
            <p>Data: Binance + CoinGecko | Analysis: Claude Sonnet 4</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LiveDashboard;
