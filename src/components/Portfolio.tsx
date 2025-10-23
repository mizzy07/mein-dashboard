import { TrendingUp, TrendingDown, Wallet } from 'lucide-react';
import { mockAssets } from '../data/mockData';

const Portfolio = () => {
  const totalValue = mockAssets.reduce((sum, asset) => sum + asset.value, 0);
  const totalChange = mockAssets.reduce((sum, asset) => sum + (asset.value * asset.change24h / 100), 0);
  const totalChangePercent = (totalChange / totalValue) * 100;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-slate-200 flex items-center gap-2">
          <Wallet size={24} />
          Portfolio
        </h3>
        <div className="text-right">
          <p className="text-slate-400 text-sm">Gesamtwert</p>
          <p className="text-2xl font-bold text-white">
            ${totalValue.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
          </p>
          <div className={`flex items-center gap-1 justify-end ${
            totalChangePercent >= 0 ? 'text-trade-green' : 'text-trade-red'
          }`}>
            {totalChangePercent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span className="text-sm font-semibold">
              {totalChangePercent >= 0 ? '+' : ''}{totalChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {mockAssets.map((asset) => {
          const isPositive = asset.change24h >= 0;
          const percentage = (asset.value / totalValue) * 100;

          return (
            <div
              key={asset.symbol}
              className="bg-dark-bg rounded-lg p-4 hover:bg-slate-800/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {asset.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-200">{asset.symbol}</p>
                    <p className="text-sm text-slate-400">{asset.name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-200">
                    ${asset.value.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                  </p>
                  <div className={`text-sm font-medium ${
                    isPositive ? 'text-trade-green' : 'text-trade-red'
                  }`}>
                    {isPositive ? '+' : ''}{asset.change24h.toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">
                  {asset.amount.toFixed(4)} {asset.symbol}
                </span>
                <span className="text-slate-400">
                  {percentage.toFixed(2)}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="mt-2 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Portfolio;
