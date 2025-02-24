import "./LineSelector.css"

const LineSelector = ({ stationInformation, setStationPublicCode }) => {

  return (
    <div className="line-selector-container">
      <div className="line-selector">
        {
          stationInformation.transfer_lines.map((transferLineInfo) => {
            const colors = selectColor(transferLineInfo, stationInformation);
            const transferStationPublicCode = transferLineInfo.station_public_code
            
            return (
              
                  <TransferLineBadge 
                    transferLineInfo={transferLineInfo} 
                    onClick={() => {setStationPublicCode(transferStationPublicCode)}}
                    {...colors}
                  />
              
            );
          })
        }         
      </div>
    </div>
  );
};
  
export default LineSelector;

// Line Badge Componenet
const TransferLineBadge = ({transferLineInfo, onClick, bgColor, bdColor, textColor}) => {
  return (
    <div 
      key={transferLineInfo.line_id}
      className="line-badge selected"
      style={{ 
        backgroundColor: bgColor,
        borderColor: bdColor,
        color: textColor
      }}
      onClick={onClick}
    >
      {transferLineInfo.line_name}
    </div>
  );
}

// Color selection logic
const selectColor = (transferLineInfo, stationInformation) => {
  const bgColor = (
    transferLineInfo.line_id === stationInformation.line.line_id 
      ? `#${transferLineInfo.line_color}` 
      : "#FFFFFF"
  );
  const bdColor = `#${transferLineInfo.line_color}`;
  const textColor = (
    transferLineInfo.line_id === stationInformation.line.line_id 
      ? "#FFFFFF" 
      : `#${transferLineInfo.line_color}`
  );
  return {bgColor, bdColor, textColor};
}
  