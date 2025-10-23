import { useEffect, useState } from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { Trade } from '../types';
import { generateRecentTrades } from '../data/mockData';

const RecentTrades = () => {
  const [trades, setTrades] = useState<Trade[]>(generateRecentTrades());

  useEffect(() => {
    const interval = setInterval(() => {
      setTrades(generateRecentTrades());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-slate-200 mb-4">Letzte Trades</h3>

      <div className="space-y-2">
        {/* Header */}
        <div className="grid grid-cols-4 text-slate-400 text-sm font-medium pb-2 border-b border-dark-border">
          <div>Zeit</div>
          <div className="text-right">Preis (USDT)</div>
          <div className="text-right">Menge (BTC)</div>
          <div className="text-right">Typ</div>
        </div>

        {/* Trades */}
        <div className="max-h-96 overflow-y-auto space-y-1">
          {trades.map((trade) => (
            <div
              key={trade.id}
              className="grid grid-cols-4 text-sm py-2 hover:bg-dark-bg/50 rounded transition-colors"
            >
              <div className="text-slate-400">{trade.time}</div>
              <div className={`text-right font-medium ${
                trade.type === 'buy' ? 'text-trade-green' : 'text-trade-red'
              }`}>
                {trade.price.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
              </div>
              <div className="text-right text-slate-300">
                {trade.amount.toFixed(4)}
              </div>
              <div className="text-right">
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${
                  trade.type === 'buy'
                    ? 'bg-trade-green/20 text-trade-green'
                    : 'bg-trade-red/20 text-trade-red'
                }`}>
                  {trade.type === 'buy' ? (
                    <>
                      <ArrowUpRight size={12} />
                      Kauf
                    </>
                  ) : (
                    <>
                      <ArrowDownRight size={12} />
                      Verkauf
                    </>
                  )}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecentTrades;
