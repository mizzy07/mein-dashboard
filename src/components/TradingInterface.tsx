import { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const TradingInterface = () => {
  const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit');
  const [price, setPrice] = useState('42567.89');
  const [amount, setAmount] = useState('');
  const [total, setTotal] = useState('');

  const handleAmountChange = (value: string) => {
    setAmount(value);
    if (value && price) {
      setTotal((parseFloat(value) * parseFloat(price)).toFixed(2));
    }
  };

  const handleTotalChange = (value: string) => {
    setTotal(value);
    if (value && price) {
      setAmount((parseFloat(value) / parseFloat(price)).toFixed(8));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`${activeTab === 'buy' ? 'Kaufauftrag' : 'Verkaufsauftrag'} eingereicht!\nTyp: ${orderType}\nPreis: ${price}\nMenge: ${amount}\nGesamt: ${total}`);
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-slate-200 mb-4">Trading</h3>

      {/* Buy/Sell Tabs */}
      <div className="grid grid-cols-2 gap-2 mb-6">
        <button
          onClick={() => setActiveTab('buy')}
          className={`py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${
            activeTab === 'buy'
              ? 'bg-trade-green text-white'
              : 'bg-dark-bg text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingUp size={20} />
          Kaufen
        </button>
        <button
          onClick={() => setActiveTab('sell')}
          className={`py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${
            activeTab === 'sell'
              ? 'bg-trade-red text-white'
              : 'bg-dark-bg text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingDown size={20} />
          Verkaufen
        </button>
      </div>

      {/* Order Type */}
      <div className="flex gap-4 mb-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="orderType"
            checked={orderType === 'limit'}
            onChange={() => setOrderType('limit')}
            className="w-4 h-4"
          />
          <span className="text-slate-200">Limit</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="orderType"
            checked={orderType === 'market'}
            onChange={() => setOrderType('market')}
            className="w-4 h-4"
          />
          <span className="text-slate-200">Market</span>
        </label>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Price */}
        {orderType === 'limit' && (
          <div>
            <label className="block text-slate-400 text-sm mb-2">
              Preis (USDT)
            </label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              step="0.01"
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="0.00"
            />
          </div>
        )}

        {/* Amount */}
        <div>
          <label className="block text-slate-400 text-sm mb-2">
            Menge (BTC)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => handleAmountChange(e.target.value)}
            step="0.00000001"
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
            placeholder="0.00000000"
          />
          <div className="flex gap-2 mt-2">
            {[25, 50, 75, 100].map((percent) => (
              <button
                key={percent}
                type="button"
                onClick={() => handleAmountChange((0.5 * (percent / 100)).toString())}
                className="flex-1 py-1 text-xs bg-dark-bg text-slate-400 hover:text-slate-200 rounded"
              >
                {percent}%
              </button>
            ))}
          </div>
        </div>

        {/* Total */}
        <div>
          <label className="block text-slate-400 text-sm mb-2">
            Gesamt (USDT)
          </label>
          <input
            type="number"
            value={total}
            onChange={(e) => handleTotalChange(e.target.value)}
            step="0.01"
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
            placeholder="0.00"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className={`w-full py-4 rounded-lg font-bold text-white transition-colors ${
            activeTab === 'buy'
              ? 'bg-trade-green hover:bg-green-600'
              : 'bg-trade-red hover:bg-red-600'
          }`}
        >
          {activeTab === 'buy' ? 'BTC Kaufen' : 'BTC Verkaufen'}
        </button>
      </form>

      {/* Available Balance */}
      <div className="mt-6 pt-4 border-t border-dark-border">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Verfügbar:</span>
          <span className="text-slate-200 font-medium">
            {activeTab === 'buy' ? '10,000.00 USDT' : '0.5234 BTC'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TradingInterface;
