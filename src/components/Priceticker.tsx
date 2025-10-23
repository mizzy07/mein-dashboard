import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Ticker } from '../types';
import { mockTicker, updatePrice } from '../data/mockData';

const PriceTicker = () => {
  const [ticker, setTicker] = useState<Ticker>(mockTicker);
  const [priceDirection, setPriceDirection] = useState<'up' | 'down' | 'neutral'>('neutral');

  useEffect(() => {
    const interval = setInterval(() => {
      setTicker(prev => {
        const newPrice = updatePrice(prev.price);
        setPriceDirection(newPrice > prev.price ? 'up' : newPrice < prev.price ? 'down' : 'neutral');

        return {
          ...prev,
          price: newPrice
        };
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const isPositive = ticker.change24h >= 0;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-200">{ticker.symbol}</h2>
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-4xl font-bold transition-colors ${
              priceDirection === 'up' ? 'text-trade-green' :
              priceDirection === 'down' ? 'text-trade-red' :
              'text-white'
            }`}>
              ${ticker.price.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <div className={`flex items-center gap-1 px-2 py-1 rounded ${
              isPositive ? 'bg-trade-green/20 text-trade-green' : 'bg-trade-red/20 text-trade-red'
            }`}>
              {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
              <span className="font-semibold">
                {isPositive ? '+' : ''}{ticker.change24h.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 text-right">
          <div>
            <p className="text-slate-400 text-sm">24h Hoch</p>
            <p className="text-lg font-semibold text-slate-200">
              ${ticker.high24h.toLocaleString('de-DE')}
            </p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">24h Tief</p>
            <p className="text-lg font-semibold text-slate-200">
              ${ticker.low24h.toLocaleString('de-DE')}
            </p>
          </div>
          <div>
            <p className="text-slate-400 text-sm">24h Volumen</p>
            <p className="text-lg font-semibold text-slate-200">
              ${(ticker.volume24h / 1000000000).toFixed(2)}B
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceTicker;
