import StationInfo from './StationInfo/StationInfo';
import './Panel.css';

const Panel = ({ isModalOpen, setIsModalOpen, stationPublicCode, setStationPublicCode, isPanelOpen, setIsPanelOpen}) => {
  return (
    <>
      <div 
        className={`panel ${isPanelOpen && 'open'}`}
      >
        <button className='panel-open-button'
          onClick={() => setIsPanelOpen(!isPanelOpen)}
        >
          {isPanelOpen ?  '↓' : '↑'}
        </button>
        <div className="station-info-container">
          <StationInfo isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} stationPublicCode={stationPublicCode} setStationPublicCode={setStationPublicCode}/>
        </div>
        {isModalOpen && <div id="overlay-panel"></div>}
      </div>
      
    </>
    
  );
};

export default Panel;