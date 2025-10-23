import { useEffect, useState } from 'react';
import { OrderBookEntry } from '../types';
import { generateOrderBook } from '../data/mockData';

const OrderBook = () => {
  const [orderBook, setOrderBook] = useState(generateOrderBook());

  useEffect(() => {
    const interval = setInterval(() => {
      setOrderBook(generateOrderBook());
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const maxTotal = Math.max(
    ...orderBook.bids.map(b => b.total),
    ...orderBook.asks.map(a => a.total)
  );

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-slate-200 mb-4">Orderbuch</h3>

      <div className="space-y-4">
        {/* Header */}
        <div className="grid grid-cols-3 text-slate-400 text-sm font-medium pb-2 border-b border-dark-border">
          <div className="text-left">Preis (USDT)</div>
          <div className="text-right">Menge (BTC)</div>
          <div className="text-right">Gesamt</div>
        </div>

        {/* Asks (Verkaufsaufträge) */}
        <div className="space-y-1">
          {orderBook.asks.slice(0, 8).reverse().map((ask, idx) => (
            <div
              key={`ask-${idx}`}
              className="grid grid-cols-3 text-sm relative py-1"
            >
              <div
                className="absolute inset-0 bg-trade-red/10"
                style={{ width: `${(ask.total / maxTotal) * 100}%` }}
              />
              <div className="text-trade-red font-medium relative z-10">
                {ask.price.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
              </div>
              <div className="text-slate-300 text-right relative z-10">
                {ask.amount.toFixed(4)}
              </div>
              <div className="text-slate-400 text-right relative z-10">
                {ask.total.toLocaleString('de-DE')}
              </div>
            </div>
          ))}
        </div>

        {/* Spread */}
        <div className="py-3 px-4 bg-dark-bg rounded text-center">
          <span className="text-slate-400 text-sm">Spread: </span>
          <span className="text-white font-semibold">
            {(orderBook.asks[0].price - orderBook.bids[0].price).toFixed(2)} USDT
          </span>
        </div>

        {/* Bids (Kaufaufträge) */}
        <div className="space-y-1">
          {orderBook.bids.slice(0, 8).map((bid, idx) => (
            <div
              key={`bid-${idx}`}
              className="grid grid-cols-3 text-sm relative py-1"
            >
              <div
                className="absolute inset-0 bg-trade-green/10"
                style={{ width: `${(bid.total / maxTotal) * 100}%` }}
              />
              <div className="text-trade-green font-medium relative z-10">
                {bid.price.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
              </div>
              <div className="text-slate-300 text-right relative z-10">
                {bid.amount.toFixed(4)}
              </div>
              <div className="text-slate-400 text-right relative z-10">
                {bid.total.toLocaleString('de-DE')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OrderBook;
