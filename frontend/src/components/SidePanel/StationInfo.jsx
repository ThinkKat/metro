import { useState, useEffect } from 'react';
import "./SidePanel.css"
import "./StationInfo.css"
import LineSelector from './LineSelector';
import StationNameContainer from './StationNameContainer';
import TabSelector from './TabSelector';
import Tab from './Tab';

const StationInfo = ({ stationPublicCode, setStationPublicCode }) => {
    const [stationInformation, setstationInformation] = useState(null); // SearchBar의 입력값
    const [realtimeData, setRealtimeData] = useState(null);
    const [tab, setTab] = useState("realTime");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`/subways/information/${stationPublicCode}`); 
                const data = await response.json();
                // console.log(data)
                setstationInformation(data); // 전체 데이터를 상태로 저장
                setRealtimeData(data.realtime_station);

                // 실시간 데이터가 없는 경우 시간표 탭으로 이동 
                if (!data.has_realtimes) {
                    setTab('schedule');
                } else {
                    setTab('realTime');
                }
            } catch (error) {
                console.error("Error :", error);
            }
        };
        if (stationPublicCode !== null) {
            console.log(stationPublicCode);
            fetchData();
        }
    }, [stationPublicCode]);

    return (
        stationInformation !== null ?
        <div className="station-info-container">
            <div className="fixed-content">
                <LineSelector stationInformation={stationInformation} setStationPublicCode={setStationPublicCode}/>
                <StationNameContainer stationInformation={stationInformation} setStationPublicCode={setStationPublicCode}/>
                <TabSelector has_realtimes={stationInformation.has_realtimes} tab={tab} setTab={setTab}/>
            </div>
            <div className="scrollable-content">
                <Tab tab={tab} stationInformation={stationInformation} realtimeData={realtimeData} setRealtimeData={setRealtimeData}/>
            </div>
        </div> :
        <div className="station-info-container no-station">
            <div className="station-info-text">
                역을 검색하세요.
            </div>
        </div>
    );
  };
  
  export default StationInfo;