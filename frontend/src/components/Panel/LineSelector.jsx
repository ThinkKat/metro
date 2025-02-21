import "./LineSelector.css"

const LineSelector = ({ stationInformation, setStationPublicCode }) => {
  
    return (
      <div className="line-selector">
        {stationInformation != null ? (
          stationInformation.transfer_lines.map((items) => {
            const bdColor = `#${items.line_color}`;
            const textColor = (
              items.line_id === stationInformation.line.line_id 
                ? "#FFFFFF" 
                : `#${items.line_color}`
            );
            const bgColor = (
              items.line_id === stationInformation.line.line_id 
                ? `#${items.line_color}` 
                : "#FFFFFF"
            );
            
            return (
              <div 
                key={items.line_id}
                className="line-badge selected"
                style={{ 
                  backgroundColor: bgColor,
                  borderColor: bdColor,
                  color: textColor
                }}
                onClick={() => {
                  setStationPublicCode(items.station_public_code);
                }}
              >
                {items.line_name}
              </div>
            );
          })
        ) : (
          <div></div>
        )}
      </div>
    );
  };
  
  export default LineSelector;