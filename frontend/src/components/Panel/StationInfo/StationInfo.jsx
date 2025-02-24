import { useState, useEffect } from 'react';
import "../Panel.css"
import "./StationInfo.css"
import CONFIG from '../../Config';
import LineSelector from './components/LineSelector';
import StationNameContainer from './components/StationNameContainer';
import TabSelector from './components/TabSelector';
import Tab from './components/Tab';

const StationInfo = ({ isModalOpen, setIsModalOpen, stationPublicCode, setStationPublicCode }) => {
    const [stationInformation, setStationInformation] = useState(null); // SearchBar의 입력값
    const [realtimeData, setRealtimeData] = useState(null);
    const [tab, setTab] = useState("realTime");

    useEffect(() => {
        if (stationPublicCode !== null) {
            fetchStationInformation(stationPublicCode).then((stationInformation) => {
                setStationInformation(stationInformation);
                setRealtimeData(null); // Reset
                if (!stationInformation.has_realtimes) {
                    setTab('schedule');
                } else {
                    setTab('realTime');
                }
            })
        }
    }, [stationPublicCode]);

    return (
        stationInformation !== null ?
        <div className="station-info-container">
            <div className="fixed-content">
                <LineSelector stationInformation={stationInformation} setStationPublicCode={setStationPublicCode}/>
                <StationNameContainer isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} stationInformation={stationInformation} setStationPublicCode={setStationPublicCode}/>
                <TabSelector has_realtimes={stationInformation.has_realtimes} tab={tab} setTab={setTab}/>
            </div>

            <div className="scrollable-content">
                <Tab tab={tab} stationInformation={stationInformation} realtimeData={realtimeData} setRealtimeData={setRealtimeData}/>
            </div>
        </div> :
        <NotSelectedStation />
    );
};
  
export default StationInfo;

const fetchStationInformation = async (stationPublicCode) => {
    try {
        const response = await fetch(`${CONFIG.stationInformation}/${stationPublicCode}`); 
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error :", error);
    }
};

const NotSelectedStation = () => {
    return (
        <div className="station-info-container no-station">
            <div className="station-info-text">
                노선도에서 역을 선택하거나 역을 검색하세요.
            </div>
        </div>
    );
}