import { useState } from 'react'
import './App.css'
import SubwayMap from './components/SubwayMap/SubwayMap'
import SidePanel from './components/SidePanel/SidePanel'

function App() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);
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
            <div className="station-info">
                선택된 역: {stationPublicCode}
            </div>
        )} */}
        <SubwayMap isDrawerOpen={isDrawerOpen} setIsDrawerOpen={setIsDrawerOpen} stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode} />
        <SidePanel isOpen={isDrawerOpen} setIsOpen={setIsDrawerOpen} stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode} />
      </main>
    </div>
  )
}

export default App
