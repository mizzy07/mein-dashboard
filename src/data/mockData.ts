import { OrderBookEntry, Trade, CandleData, Asset, Ticker } from '../types';

export const generateOrderBook = (): { bids: OrderBookEntry[], asks: OrderBookEntry[] } => {
  const bids: OrderBookEntry[] = [];
  const asks: OrderBookEntry[] = [];

  let basePrice = 42500;

  // Generate bids (buy orders)
  for (let i = 0; i < 15; i++) {
    const price = basePrice - (i * 50 + Math.random() * 50);
    const amount = Math.random() * 2 + 0.1;
    bids.push({
      price: Number(price.toFixed(2)),
      amount: Number(amount.toFixed(4)),
      total: Number((price * amount).toFixed(2))
    });
  }

  // Generate asks (sell orders)
  for (let i = 0; i < 15; i++) {
    const price = basePrice + (i * 50 + Math.random() * 50);
    const amount = Math.random() * 2 + 0.1;
    asks.push({
      price: Number(price.toFixed(2)),
      amount: Number(amount.toFixed(4)),
      total: Number((price * amount).toFixed(2))
    });
  }

  return { bids, asks };
};

export const generateRecentTrades = (): Trade[] => {
  const trades: Trade[] = [];
  const now = new Date();

  for (let i = 0; i < 20; i++) {
    const time = new Date(now.getTime() - i * 60000);
    trades.push({
      id: `trade-${i}`,
      time: time.toLocaleTimeString('de-DE'),
      price: 42500 + (Math.random() - 0.5) * 1000,
      amount: Math.random() * 0.5 + 0.01,
      type: Math.random() > 0.5 ? 'buy' : 'sell'
    });
  }

  return trades;
};

export const generateCandleData = (): CandleData[] => {
  const data: CandleData[] = [];
  let basePrice = 40000;

  for (let i = 0; i < 50; i++) {
    const open = basePrice + (Math.random() - 0.5) * 1000;
    const close = open + (Math.random() - 0.5) * 2000;
    const high = Math.max(open, close) + Math.random() * 500;
    const low = Math.min(open, close) - Math.random() * 500;
    const volume = Math.random() * 100 + 50;

    data.push({
      time: `${i}h`,
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume: Number(volume.toFixed(2))
    });

    basePrice = close;
  }

  return data;
};

export const mockAssets: Asset[] = [
  { symbol: 'BTC', name: 'Bitcoin', amount: 0.5234, value: 22245.50, change24h: 3.45 },
  { symbol: 'ETH', name: 'Ethereum', amount: 5.892, value: 9850.25, change24h: -1.23 },
  { symbol: 'SOL', name: 'Solana', amount: 45.23, value: 4523.00, change24h: 5.67 },
  { symbol: 'USDT', name: 'Tether', amount: 10000, value: 10000.00, change24h: 0.01 },
];

export const mockTicker: Ticker = {
  symbol: 'BTC/USDT',
  price: 42567.89,
  change24h: 3.45,
  volume24h: 28500000000,
  high24h: 43200.00,
  low24h: 41200.00
};

// Simulate real-time price updates
export const updatePrice = (currentPrice: number): number => {
  const change = (Math.random() - 0.5) * 100;
  return Number((currentPrice + change).toFixed(2));
};
