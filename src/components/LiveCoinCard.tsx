import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { tradingAPI, CoinAnalysis } from '../services/api';

interface LiveCoinCardProps {
  symbol: string;
}

const LiveCoinCard = ({ symbol }: LiveCoinCardProps) => {
  const [analysis, setAnalysis] = useState<CoinAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysis();
    // Refresh every 60 seconds
    const interval = setInterval(loadAnalysis, 60000);
    return () => clearInterval(interval);
  }, [symbol]);

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      const data = await tradingAPI.getCoinAnalysis(symbol);
      setAnalysis(data);
      setError(null);
    } catch (err) {
      setError(`Failed to load ${symbol}`);
      console.error(`Analysis error for ${symbol}:`, err);
    } finally {
      setLoading(false);
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'STRONG_BUY':
        return 'bg-trade-green text-white';
      case 'BUY':
        return 'bg-trade-green/80 text-white';
      case 'WEAK_BUY':
        return 'bg-green-600/60 text-white';
      case 'HOLD':
        return 'bg-slate-600 text-white';
      case 'WEAK_SELL':
        return 'bg-orange-600/60 text-white';
      case 'SELL':
        return 'bg-trade-red/80 text-white';
      case 'STRONG_SELL':
        return 'bg-trade-red text-white';
      default:
        return 'bg-slate-600 text-white';
    }
  };

  const getRSIColor = (rsi: number) => {
    if (rsi < 30) return 'text-trade-green'; // Oversold
    if (rsi > 70) return 'text-trade-red'; // Overbought
    return 'text-slate-400';
  };

  if (loading && !analysis) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-4 animate-pulse">
        <div className="h-6 bg-slate-700 rounded mb-2"></div>
        <div className="h-4 bg-slate-700 rounded"></div>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-4">
        <div className="text-red-400 text-sm">{error}</div>
      </div>
    );
  }

  if (!analysis) return null;

  const { price, signal, technical, ai_analysis } = analysis;
  const isPositive = price.change_24h >= 0;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-blue-500/50 transition-all cursor-pointer">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            {symbol.slice(0, 2)}
          </div>
          <div>
            <h3 className="font-bold text-slate-200">{symbol}</h3>
            <div className={`flex items-center gap-1 text-sm ${isPositive ? 'text-trade-green' : 'text-trade-red'}`}>
              {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              <span>{isPositive ? '+' : ''}{price.change_24h.toFixed(2)}%</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-white">
            ${price.price.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Signal Badge */}
      <div className="mb-3">
        <div className={`${getSignalColor(signal.signal)} px-3 py-2 rounded-lg flex items-center justify-between`}>
          <span className="font-bold text-sm">{signal.signal.replace(/_/g, ' ')}</span>
          <span className="text-sm opacity-90">{signal.confidence}% ✓</span>
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
        <div className="bg-dark-bg rounded p-2">
          <p className="text-slate-400 text-xs">RSI</p>
          <p className={`font-semibold ${getRSIColor(technical.rsi)}`}>
            {technical.rsi.toFixed(1)}
          </p>
        </div>
        <div className="bg-dark-bg rounded p-2">
          <p className="text-slate-400 text-xs">Trend</p>
          <p className="font-semibold text-slate-200 truncate text-xs">
            {technical.trend.replace(/_/g, ' ')}
          </p>
        </div>
      </div>

      {/* AI Analysis Summary */}
      {ai_analysis && (
        <div className="border-t border-dark-border pt-3">
          <div className="flex items-start gap-2 mb-2">
            <Activity size={14} className="text-blue-400 mt-0.5" />
            <p className="text-xs text-slate-300 line-clamp-2">
              {ai_analysis.reasoning}
            </p>
          </div>

          {/* Key Factors */}
          {ai_analysis.key_factors && ai_analysis.key_factors.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-slate-400 mb-1">Key Factors:</p>
              <ul className="text-xs text-slate-300 space-y-1">
                {ai_analysis.key_factors.slice(0, 2).map((factor, idx) => (
                  <li key={idx} className="flex items-start gap-1">
                    <span className="text-blue-400">•</span>
                    <span className="line-clamp-1">{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Entry/Target */}
          {signal.entry_zone && (
            <div className="mt-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Entry:</span>
                <span className="text-slate-200 font-medium">{signal.entry_zone}</span>
              </div>
              {signal.targets && signal.targets.length > 0 && (
                <div className="flex justify-between mt-1">
                  <span className="text-slate-400">Target:</span>
                  <span className="text-trade-green font-medium">
                    ${signal.targets[0].toLocaleString('de-DE')}
                  </span>
                </div>
              )}
              {signal.stop_loss && (
                <div className="flex justify-between mt-1">
                  <span className="text-slate-400">Stop:</span>
                  <span className="text-trade-red font-medium">
                    ${signal.stop_loss.toLocaleString('de-DE')}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Action */}
      <div className="mt-3 pt-3 border-t border-dark-border">
        <p className="text-xs text-slate-400 mb-1">Recommended Action</p>
        <p className="text-sm font-semibold text-slate-200">{signal.action}</p>
      </div>
    </div>
  );
};

export default LiveCoinCard;
