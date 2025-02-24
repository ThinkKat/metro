import { useState } from 'react'
import './App.css'
import MetroMap from './components/MetroMap/MetroMap'
import Panel from './components/Panel/Panel'
import SearchBar from './components/SearchBar/SearchBar';

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [stationPublicCode, setStationPublicCode] = useState(null)

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1>수도권 전철 노선도</h1>
        </div>
      </header>
      <main className="app-main">
        {/* {stationPublicCode && (
            <div className="test-station-info">
                선택된 역: {stationPublicCode}
            </div>
        )} */}
        <MetroMap setStationPublicCode={setStationPublicCode} />
        <SearchBar setStationPublicCode={setStationPublicCode} />
        <Panel isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode} />
      </main>
    </div>
  )
}

export default App
