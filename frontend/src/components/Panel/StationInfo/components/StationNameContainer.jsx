import { useState, useEffect } from "react";
import "./StationNameContainer.css"

const StationNameContainer = ({ isModalOpen, setIsModalOpen, stationInformation, setStationPublicCode }) => {
  const [clickDirection, setClickDirection] = useState(null);

  // Close dropdown when clicking outside of the dropdown
    useEffect(() => {
      const adjacentStationSelector = document.querySelector(".adjacent-station-selector-container");
      const handleClickOutside = (event) => {
        if (adjacentStationSelector && !adjacentStationSelector.contains(event.target)) {
          setIsModalOpen(false);
          setClickDirection(null);
        }
      };

      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }, [isModalOpen]);
  
  return (
    <div className="station-line-container">
      <AdjecentStation direction={"left"} stationInformation={stationInformation} setStationPublicCode={setStationPublicCode} setIsModalOpen={setIsModalOpen} setClickDirection={setClickDirection}/>
      <CurrentStation stationInformation={stationInformation} />
      <AdjecentStation direction={"right"} stationInformation={stationInformation} setStationPublicCode={setStationPublicCode} setIsModalOpen={setIsModalOpen} setClickDirection={setClickDirection}/>
      {isModalOpen && <AdjecentStationSelector stationInformation={stationInformation} clickDirection={clickDirection} setStationPublicCode={setStationPublicCode} setIsModalOpen={setIsModalOpen}/>}
    </div>
  );
};

export default StationNameContainer;

const CurrentStation = ({stationInformation}) => {
  return (
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
  );
};

const AdjecentStationSelector = ({stationInformation, clickDirection, setStationPublicCode, setIsModalOpen}) => {
  const adjacentStations = stationInformation.adjacent_stations[clickDirection];
  return (
    <div className="adjacent-station-selector-container"  style={{ backgroundColor: `#${stationInformation.line.line_color}` }}>
      {
        adjacentStations.map((station) => {
          return (
            <div 
              className="adjacent-station-selector"
              key={station.station_public_code}
              onClick={() => {
                setStationPublicCode(station.station_public_code);
                setIsModalOpen(false);
              }}
            >
              {station.station_name}
            </div>
          );
        })
      }
    </div> 
  );
};

const AdjecentStation = ({stationInformation, direction, setStationPublicCode, setIsModalOpen, setClickDirection}) => {
  const adjacentStations = stationInformation.adjacent_stations[direction];

  const stationName = (
    adjacentStations.length > 0 ?
      `${adjacentStations.map(station => station.station_name).join("/")}` :
      '종점'
  );

  // Check last station
  const isLastStation = adjacentStations.length == 0;

  // Click function
  const onClick = (
    isLastStation ?
    () => {}:
    () => {
      if (adjacentStations.length > 1) {
        setIsModalOpen(true);
        setClickDirection(direction);
      } else {
        setStationPublicCode(adjacentStations[0].station_public_code)
      }
    }
  );

  return (
    <div 
      className={`adjacent-station ${direction} ${isLastStation && 'last'}`}
      style={{ backgroundColor: `#${stationInformation.line.line_color}` }}
      onClick={onClick}
    >
      <span className="station-name-text">{stationName}</span>
    </div>
  );
};