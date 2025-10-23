import PriceTicker from './Priceticker';
import TradingChart from './TradingChart';
import OrderBook from './OrderBook';
import TradingInterface from './TradingInterface';
import Portfolio from './Portfolio';
import RecentTrades from './RecentTrades';
import { BarChart3 } from 'lucide-react';

const Dashboard = () => {
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
                <h1 className="text-2xl font-bold text-white">Trading Dashboard</h1>
                <p className="text-slate-400 text-sm">Echtzeit Krypto-Trading</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-slate-400 text-sm">Eingeloggt als</p>
                <p className="text-white font-semibold">Demo User</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <div className="space-y-6">
          {/* Price Ticker */}
          <PriceTicker />

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Chart */}
            <div className="lg:col-span-2 space-y-6">
              <TradingChart />
              <RecentTrades />
            </div>

            {/* Right Column - Trading & OrderBook */}
            <div className="space-y-6">
              <TradingInterface />
              <OrderBook />
            </div>
          </div>

          {/* Portfolio */}
          <Portfolio />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-dark-card border-t border-dark-border mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-slate-400">
            <p>Trading Dashboard - Demo Version</p>
            <p>Powered by React & TypeScript</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
