import { useState, useEffect } from 'react';
import './Tab.css';
import CONFIG from '../../../Config';

const Tab = ({ tab, stationInformation, realtimeData, setRealtimeData }) => { 
    const [selectedDay, setSelectedDay] = useState('weekday');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const REFRESH_INTERVAL = 13000; // 13초

    // Refreshing
    const handleRealtimeRefresh = () => {
        setIsRefreshing(true);
        realtimeRefresh(stationInformation.station.station_public_code).then((data) => {
            console.log(`Refershing at ${new Date()}`)
            setRealtimeData(data.station);
            setIsRefreshing(false);
        });
    }

    // Auto Refresh
    useEffect(() => {
        let intervalId;
        if (tab === "realTime") {
            // Initial refresh
            handleRealtimeRefresh();

            // Set the auto refresh
            intervalId = setInterval(() => {
                handleRealtimeRefresh();
            }, REFRESH_INTERVAL);
        }
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [tab, stationInformation.station]);
    
    return (
        tab === "realTime" 
        ? <ArrivalInfo isRefreshing={isRefreshing} onClick={handleRealtimeRefresh} stationInformation={stationInformation} realtimeData={realtimeData} />
        : <TimetableInfo selectedDay={selectedDay} setSelectedDay={setSelectedDay} stationInformation={stationInformation} />
    );
}

export default Tab;

const RefreshButton = ({isRefreshing, onClick}) => {
    return (
        <div className="arrival-refresh-button-container">
            <button 
                className={`arrival-refresh-button ${isRefreshing ? 'refreshing' : ''}`}
                onClick={onClick}
                disabled={isRefreshing}
            >
                새로고침
            </button>
        </div>
    );
};

const realtimeRefresh = async (stationPublicCode) => {
    try {
        const response = await fetch(`${CONFIG.stationRealtime}/${stationPublicCode}`);
        if (!response.ok) throw new Error('Failed to fetch realtime data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error refreshing realtime data:', error);
        throw error;
    }
};

const AdjacentStationDirection = ({stationInformation}) => {
    return (
        <div className='adjcent-station-direction'>
            <span className="direction">
                {stationInformation.adjacent_stations.left.length > 0 ? (
                    <span>
                    {stationInformation.adjacent_stations.left[0].station_name} 방면
                    </span> 
                ) : (
                    <span>종점</span>
                )}
            </span>
            <span className="direction">
                {stationInformation.adjacent_stations.right.length > 0 ? (
                    <span>
                    {stationInformation.adjacent_stations.right[0].station_name} 방면
                    </span> 
                ) : (
                    <span>종점</span>
                )}
            </span>
        </div>
    );
};

const ArrivalInfo = ({isRefreshing, onClick, stationInformation, realtimeData}) => {
    return (
        <div className="tab-info">
            <div className='sticky-header'>
                <div className="tab-header arrival">
                    <div className='tab-header-title'>도착 정보</div>
                    <RefreshButton 
                        isRefreshing={isRefreshing} 
                        onClick={onClick}
                    />
                </div>
                <AdjacentStationDirection stationInformation={stationInformation}/>
            </div>
            <ArrivalListsContainer realtimeData={realtimeData}/>
        </div>
    );
};

const ArrivalListsContainer = ({realtimeData}) => {
    return (
        <div className="lists-container arrival">
            <ArrivalList direction={'left'} realtimeData={realtimeData}/>
            <ArrivalList direction={'right'} realtimeData={realtimeData}/>
        </div>
    );
};

const ArrivalList = ({direction, realtimeData}) => {
    return (
        <div className={`data-list arrival ${direction}`}>
            {
                realtimeData !== null && realtimeData[direction].length > 0 ?
                realtimeData.left.map((station, index) => (
                    <div className="data-item" key={index}>
                        <span className="direction">{station.last_station_name}</span>
                        <span className="time">{station.information_message.replace(/\[(\d+)\]/, "$1").replace(/\(.*\)/, "")}</span>
                    </div>
                ))
                : <div>
                    정보가 없습니다.
                </div>
            }
        </div>
    );
};

const TimetableDaySelector = ({selectedDay, setSelectedDay}) => {
    return (
        <div className="timetable-selector">
            <TimetableDayButton day={"weekday"} selectedDay={selectedDay} setSelectedDay={setSelectedDay}/>
            <TimetableDayButton day={"holiday"} selectedDay={selectedDay} setSelectedDay={setSelectedDay}/>
        </div>
    );
};

const TimetableDayButton = ({day, selectedDay, setSelectedDay}) => {
    const dayKor = day == "weekday" ? "평일" : "주말"

    return (
        <button 
            className={`day-button ${selectedDay === day ? 'selected' : ''}`}
            onClick={() => setSelectedDay(day)}
        >
            {dayKor}
        </button>
    );
};

const TimetableInfo = ({selectedDay, setSelectedDay, stationInformation}) => {
    return (
        <div className="tab-info">
            <div className='sticky-header'>
                <div className="tab-header timetable">
                    <div className='tab-header-title'>시간표 정보</div>
                    <TimetableDaySelector selectedDay={selectedDay} setSelectedDay={setSelectedDay}/>
                </div>
                <AdjacentStationDirection stationInformation={stationInformation}/>
            </div>
            <TimetableListsContainer selectedDay={selectedDay} stationInformation={stationInformation}/>
        </div>
    );
};

const TimetableListsContainer = ({selectedDay, stationInformation}) => {
    return (
        selectedDay == "weekday" ?
        <div className="lists-container timetable">
            <TimetableList selectedDay={selectedDay} direction={"left"}  stationInformation={stationInformation} />
            <TimetableList selectedDay={selectedDay} direction={"right"} stationInformation={stationInformation} />
        </div> :
        <div className="lists-container timetable">
            <TimetableList selectedDay={selectedDay} direction={"left"}  stationInformation={stationInformation} />
            <TimetableList selectedDay={selectedDay} direction={"right"} stationInformation={stationInformation} />
        </div>
    );
};

const TimetableList = ({selectedDay, stationInformation, direction}) => {
    return (
        <div className={`data-list timetable ${direction}`}>
            {
                stationInformation.timetables[selectedDay][direction]
                .filter((timetable) => timetable.department_time !== null)
                .map((timetable, index) => (
                    <div className="data-item" key={index}>
                        <span className="time">{timetable.last_station_name}</span>
                        <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                    </div>
                ))
            }
        </div>
    );
};