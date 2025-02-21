import "./TabSelector.css"

const TabSelector = ({ has_realtimes, tab, setTab }) => {

  return (
    has_realtimes ?
      <div className="tab-container">
          <div 
            className={`tab ${tab === 'realTime' ? 'selected' : ''}`}
            onClick={() => setTab('realTime')}
          >
            실시간
          </div>
          <div 
            className={`tab ${tab === 'schedule' ? 'selected' : ''}`}
            onClick={() => setTab('schedule')}
          >
            시간표
          </div>
      </div> :
      <div className="tab-container">
        <div 
          className={`tab ${tab === 'schedule' ? 'selected' : ''}`}
          onClick={() => setTab('schedule')}
        >
          시간표
        </div>
      </div>
    );
};  

export default TabSelector;