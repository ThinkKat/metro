import "./StationNameContainer.css"

const StationNameContainer = ({ stationInformation, setStationPublicCode }) => {
    
    return (
      <div className="station-line-container">
        {/* 왼쪽 인접역 */}
        <div 
          className="adjacent-station left"
          style={{ backgroundColor: `#${stationInformation.line.line_color}` }}
          onClick={() => {
            if (stationInformation.adjacent_stations.left.length > 1) {
              setStationPublicCode(stationInformation.adjacent_stations.left[0].station_public_code);
            } else if (stationInformation.adjacent_stations.left.length === 1) {
              setStationPublicCode(stationInformation.adjacent_stations.left[0].station_public_code);
            }
          }}
        >
          {stationInformation.adjacent_stations.left.length > 0 ? (
            <span className="station-name-text">
              ←{stationInformation.adjacent_stations.left[0].station_name}
            </span> 
          ) : (
            <span>종점</span>
          )}
        </div>
        
        {/* 가운데 현재역 */}
        <div 
          className="current-station"
          style={{ borderColor: `#${stationInformation.line.line_color}` }}
        >
          <div 
            className="station-circle"
            style={{ backgroundColor: `#${stationInformation.line.line_color}` }}
          >
            {stationInformation.station.station_public_code}
          </div>
          <div 
            className="station-name"
            style={{ color: `#${stationInformation.line.line_color}` }}
          >
            {stationInformation.station.station_name}
          </div>
        </div>
  
        {/* 오른쪽 인접역 */}
        <div 
          className="adjacent-station right"
          style={{ backgroundColor: `#${stationInformation.line.line_color}` }}
          onClick={() => {
            if (stationInformation.adjacent_stations.right.length > 1) {
              setStationPublicCode(stationInformation.adjacent_stations.right[0].station_public_code);
            } else if (stationInformation.adjacent_stations.right.length === 1) {
              setStationPublicCode(stationInformation.adjacent_stations.right[0].station_public_code);
            }
          }}
        >
          {stationInformation.adjacent_stations.right.length > 0 ? (
            <span className="station-name-text">
              {stationInformation.adjacent_stations.right[0].station_name}→
            </span> 
          ) : (
            <span>종점</span>
          )}
        </div>
      </div>
    );
  };
  
  export default StationNameContainer;