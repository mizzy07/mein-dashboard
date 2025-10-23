# Trading Dashboard

Ein modernes, responsives Trading Dashboard für Kryptowährungen, entwickelt mit React, TypeScript und TailwindCSS.

## Features

- **Echtzeit-Preisanzeige**: Live-Preisupdates mit visuellen Indikatoren für Preisbewegungen
- **Interaktiver Chart**: Preisdiagramm mit verschiedenen Zeitrahmen (1M, 5M, 15M, 1H, 4H, 1D, 1W)
- **Orderbuch**: Live-Anzeige von Kauf- und Verkaufsaufträgen mit visuellem Tiefendiagramm
- **Trading-Interface**: Intuitive Benutzeroberfläche für Limit- und Market-Orders
- **Portfolio-Übersicht**: Detaillierte Ansicht Ihrer Krypto-Assets mit Performance-Tracking
- **Handelshistorie**: Chronologische Übersicht der letzten ausgeführten Trades
- **Dark Mode Design**: Professionelles, augenfreundliches dunkles Theme

## Technologie-Stack

- **Frontend Framework**: React 18
- **Sprache**: TypeScript
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Package Manager**: npm

## Installation

```bash
# Repository klonen
git clone https://github.com/mizzy07/mein-dashboard.git

# In das Projektverzeichnis wechseln
cd mein-dashboard

# Dependencies installieren
npm install
```

## Verwendung

### Entwicklungsserver starten

```bash
npm run dev
```

Der Entwicklungsserver läuft standardmäßig auf `http://localhost:5173`

### Produktions-Build erstellen

```bash
npm run build
```

Die optimierten Dateien werden im `dist/` Verzeichnis erstellt.

### Build-Vorschau

```bash
npm run preview
```

## Projektstruktur

```
mein-dashboard/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx          # Haupt-Dashboard-Layout
│   │   ├── Priceticker.tsx        # Echtzeit-Preisanzeige
│   │   ├── TradingChart.tsx       # Preis-Chart-Komponente
│   │   ├── OrderBook.tsx          # Orderbuch-Anzeige
│   │   ├── TradingInterface.tsx   # Buy/Sell Interface
│   │   ├── Portfolio.tsx          # Portfolio-Übersicht
│   │   └── RecentTrades.tsx       # Handelshistorie
│   ├── data/
│   │   └── mockData.ts            # Mock-Daten für Demo
│   ├── types/
│   │   └── index.ts               # TypeScript-Typdefinitionen
│   ├── App.tsx                    # Root-Komponente
│   ├── main.tsx                   # App-Einstiegspunkt
│   └── index.css                  # Globale Styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Features im Detail

### Preis-Ticker
- Zeigt den aktuellen BTC/USDT Preis in Echtzeit
- 24h High/Low/Volume Statistiken
- Visuelle Indikatoren für Preisbewegungen (grün/rot)
- Prozentuale Änderung über 24 Stunden

### Trading-Chart
- Area-Chart für Preisentwicklung
- Auswahl verschiedener Zeitrahmen
- Responsive und interaktive Darstellung
- Farbcodierte Darstellung mit Gradienten

### Orderbuch
- Getrennte Anzeige von Kauf- und Verkaufsaufträgen
- Visuelle Tiefendarstellung
- Spread-Anzeige
- Echtzeit-Updates alle 3 Sekunden

### Trading-Interface
- Wechsel zwischen Kauf und Verkauf
- Limit- und Market-Order-Typen
- Prozentuale Schnellauswahl (25%, 50%, 75%, 100%)
- Automatische Berechnung von Gesamt-/Mengenfeldern
- Anzeige verfügbarer Guthaben

### Portfolio
- Übersicht aller gehaltenen Assets
- Gesamtportfoliowert mit 24h Änderung
- Einzelne Asset-Performance
- Prozentuale Portfolioverteilung
- Visuelle Fortschrittsbalken

## Demo-Daten

Das Dashboard verwendet Mock-Daten für Demonstrationszwecke. In einer Produktionsumgebung würden diese durch echte API-Aufrufe an eine Krypto-Exchange ersetzt.

## Anpassung

### Farben anpassen

Die Farbpalette kann in `tailwind.config.js` angepasst werden:

```javascript
theme: {
  extend: {
    colors: {
      'trade-green': '#10b981',
      'trade-red': '#ef4444',
      'dark-bg': '#0f172a',
      'dark-card': '#1e293b',
      'dark-border': '#334155',
    },
  },
}
```

### Zeitintervalle ändern

Update-Intervalle können in den jeweiligen Komponenten angepasst werden:
- Preis-Updates: `PriceTicker.tsx` (aktuell: 2 Sekunden)
- Orderbuch-Updates: `OrderBook.tsx` (aktuell: 3 Sekunden)
- Trade-Updates: `RecentTrades.tsx` (aktuell: 5 Sekunden)

## Lizenz

MIT

## Autor

Erstellt mit Claude Code