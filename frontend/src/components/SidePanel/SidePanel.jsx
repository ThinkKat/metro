import SearchBar from './SearchBar';
import StationInfo from './StationInfo';
import './SidePanel.css';

const SidePanel = ({isOpen, setIsOpen, stationPublicCode, setStationPublicCode}) => {
  return (
      <div className={`side-panel ${isOpen ? 'open' : ''}`}>
      {/* 토글 버튼 추가 */}
      <button 
        className="drawer-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? '→' : '←'}
      </button>
      <div className="station-info-container">
        <SearchBar stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode}/>
        <StationInfo stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode}/>
      </div>
    </div>
  );
};

export default SidePanel;