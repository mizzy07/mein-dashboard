import { useEffect, useState } from 'react';
import { Brain, TrendingUp, AlertTriangle, Lightbulb } from 'lucide-react';
import { tradingAPI, MorningBrief } from '../services/api';

const AIInsights = () => {
  const [brief, setBrief] = useState<MorningBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMorningBrief();
    // Refresh every 30 minutes
    const interval = setInterval(loadMorningBrief, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadMorningBrief = async () => {
    try {
      setLoading(true);
      const data = await tradingAPI.getMorningBrief();
      setBrief(data);
      setError(null);
    } catch (err) {
      setError('Failed to load AI insights');
      console.error('Morning brief error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !brief) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="text-blue-500" size={24} />
          <h3 className="text-xl font-bold text-slate-200">AI Insights</h3>
        </div>
        <div className="text-slate-400">Loading AI analysis...</div>
      </div>
    );
  }

  if (error && !brief) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="text-blue-500" size={24} />
          <h3 className="text-xl font-bold text-slate-200">AI Insights</h3>
        </div>
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  if (!brief) return null;

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'BULLISH':
        return 'text-trade-green';
      case 'BEARISH':
        return 'text-trade-red';
      default:
        return 'text-slate-400';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'bg-trade-green/20 text-trade-green';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-500';
      case 'HIGH':
        return 'bg-trade-red/20 text-trade-red';
      default:
        return 'bg-slate-500/20 text-slate-400';
    }
  };

  const getSignalColor = (signal: string) => {
    if (signal.includes('BUY')) return 'text-trade-green';
    if (signal.includes('SELL')) return 'text-trade-red';
    return 'text-slate-400';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Brain className="text-blue-500" size={24} />
          <h3 className="text-xl font-bold text-slate-200">AI Insights</h3>
        </div>
        <div className="text-sm text-slate-400">{brief.date}</div>
      </div>

      {/* Market Status */}
      <div className="mb-6 p-4 bg-dark-bg rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400 mb-1">Market Status</p>
            <p className={`text-2xl font-bold ${getMarketStatusColor(brief.market_status)}`}>
              {brief.market_status}
            </p>
          </div>
          {brief.fear_greed !== undefined && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Fear & Greed</p>
              <p className="text-2xl font-bold text-white">{brief.fear_greed}</p>
            </div>
          )}
          <div>
            <p className="text-sm text-slate-400 mb-1">Risk Level</p>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskLevelColor(brief.risk_level)}`}>
              {brief.risk_level}
            </span>
          </div>
        </div>
      </div>

      {/* Top Opportunities */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp size={18} className="text-trade-green" />
          <h4 className="font-semibold text-slate-200">Top Opportunities Today</h4>
        </div>
        <div className="space-y-2">
          {brief.top_opportunities.map((opp, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-dark-bg rounded-lg hover:bg-slate-800/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                  {opp.coin.slice(0, 2)}
                </div>
                <div>
                  <p className="font-semibold text-slate-200">{opp.coin}</p>
                  <p className={`text-sm font-medium ${getSignalColor(opp.signal)}`}>
                    {opp.signal.replace(/_/g, ' ')}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-400">Confidence</p>
                <p className="font-bold text-white">{opp.confidence}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Macro Alerts */}
      {brief.macro_alerts && brief.macro_alerts.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-yellow-500" />
            <h4 className="font-semibold text-slate-200">Macro Alerts</h4>
          </div>
          <div className="space-y-2">
            {brief.macro_alerts.map((alert, idx) => (
              <div
                key={idx}
                className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-200 text-sm"
              >
                {alert}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Tip */}
      <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <div className="flex items-start gap-3">
          <Lightbulb size={20} className="text-blue-400 mt-0.5" />
          <div className="text-sm text-blue-200">
            <p className="font-semibold mb-1">Trading Tip</p>
            <p>
              {brief.market_status === 'BULLISH'
                ? 'Market conditions are favorable. Consider scaling into positions on dips with strict stop losses.'
                : brief.market_status === 'BEARISH'
                ? 'Market conditions are challenging. Focus on capital preservation and wait for better setups.'
                : 'Market is uncertain. Wait for clearer signals before making significant moves.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
