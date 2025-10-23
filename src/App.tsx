import { useState } from 'react'
import Dashboard from './components/Dashboard'
import LiveDashboard from './components/LiveDashboard'

function App() {
  const [useLiveData, setUseLiveData] = useState(true)

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Toggle between Demo and Live */}
      <div className="fixed top-4 right-4 z-50">
        <button
          onClick={() => setUseLiveData(!useLiveData)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-lg transition-colors"
        >
          {useLiveData ? '📊 Live AI Mode' : '🎮 Demo Mode'}
        </button>
      </div>

      {useLiveData ? <LiveDashboard /> : <Dashboard />}
    </div>
  )
}

export default App
