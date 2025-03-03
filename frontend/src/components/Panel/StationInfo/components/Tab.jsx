import { useState, useEffect } from 'react';
import './Tab.css';
import CONFIG from '../../../Config';

const Tab = ({ tab, stationInformation, realtimeData, setRealtimeData }) => { 
    const [selectedDay, setSelectedDay] = useState('weekday');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [refreshTime, setRefershTime] = useState('');
    const [additionalInfoOpen, setAdditionalInfoOpen] = useState(false);
    const REFRESH_INTERVAL = 13000; // 13초

    // Refreshing
    const handleRealtimeRefresh = () => {
        setIsRefreshing(true);
        realtimeRefresh(stationInformation.station.station_public_code).then((data) => {
            const newRefreshTime = new Date();
            const newRefreshTimeStr = `${newRefreshTime.getHours().toString().padStart(2,'0')}:${newRefreshTime.getMinutes().toString().padStart(2,'0')}`
            
            console.log(`Refershing at ${new Date()}`)
            setRealtimeData(data.station);
            setIsRefreshing(false);
            setRefershTime(newRefreshTimeStr);
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
        ? <ArrivalInfo isRefreshing={isRefreshing} refreshTime={refreshTime} onClick={handleRealtimeRefresh} stationInformation={stationInformation} realtimeData={realtimeData} additionalInfoOpen={additionalInfoOpen} setAdditionalInfoOpen={setAdditionalInfoOpen}/>
        : <TimetableInfo selectedDay={selectedDay} setSelectedDay={setSelectedDay} stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen} setAdditionalInfoOpen={setAdditionalInfoOpen}/>
    );
}

export default Tab;

const RefreshButton = ({refreshTime, isRefreshing, onClick}) => {
    return (
        <div className="arrival-refresh-button-container">
            <div className='refresh-time-container'>
                <span className='refresh-time'>{refreshTime}</span>
            </div>
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

const ArrivalInfo = ({isRefreshing, refreshTime, onClick, stationInformation, realtimeData, additionalInfoOpen, setAdditionalInfoOpen}) => {
    return (
        <div className="tab-info">
            <div className='sticky-header'>
                <div className="tab-header arrival">
                    <div className='tab-header-title'>
                        도착 정보
                        <button className="additional-info" onClick={() => setAdditionalInfoOpen(!additionalInfoOpen)}>
                            추가정보
                        </button>
                    </div>
                    <RefreshButton 
                        refreshTime={refreshTime}
                        isRefreshing={isRefreshing} 
                        onClick={onClick}
                    />
                </div>
                <AdjacentStationDirection stationInformation={stationInformation}/>
            </div>
            <ArrivalListsContainer realtimeData={realtimeData} additionalInfoOpen={additionalInfoOpen}/>
        </div>
    );
};

const ArrivalListsContainer = ({realtimeData, additionalInfoOpen}) => {
    return (
        <div className="lists-container arrival">
            <ArrivalList direction={'left'} realtimeData={realtimeData} additionalInfoOpen={additionalInfoOpen}/>
            <ArrivalList direction={'right'} realtimeData={realtimeData} additionalInfoOpen={additionalInfoOpen}/>
        </div>
    );
};

const ArrivalList = ({direction, realtimeData, additionalInfoOpen}) => {
    return (
        <div className={`data-list arrival ${direction}`}>
            {
                realtimeData !== null && realtimeData[direction].length > 0 ?
                realtimeData[direction].map((arrival, index) => {
                    const expArrTime = new Date(arrival.expected_arrival_time);
                    const expArrTimeStr = `${expArrTime.getHours().toString().padStart(2,'0')}:${expArrTime.getMinutes().toString().padStart(2,'0')}`
                    const delayedTime = arrival.current_delayed_time > 0 && `약 ${parseInt(arrival.current_delayed_time/60)}분 ${parseInt(arrival.current_delayed_time%60)}초 지연`

                    return (
                        <div className = 'data-item-container'>
                            <div className="data-item" key={index}>
                                <span className="direction">{arrival.last_station_name}</span>
                                <span className="time">{arrival.information_message.replace(/\[(\d+)\]/, "$1").replace(/\(.*\)/, "")}</span>
                            </div>
                            {
                                additionalInfoOpen && (
                                    <div>
                                        {arrival.expected_arrival_time && <div className='expected-arrival-time'>예상도착시각 {expArrTimeStr}</div>}
                                        {arrival.current_delayed_time && <div className='delayed-time'>{delayedTime}</div>}
                                        <div className='train-id'>열차번호 {arrival.train_id}</div>
                                    </div>
                                )
                            }
                        </div>
                    );
                })
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

const TimetableInfo = ({selectedDay, setSelectedDay, stationInformation, additionalInfoOpen, setAdditionalInfoOpen}) => {
    return (
        <div className="tab-info">
            <div className='sticky-header'>
                <div className="tab-header timetable">
                    <div className='tab-header-title'>
                        시간표 정보
                        <button className="additional-info" onClick={() => setAdditionalInfoOpen(!additionalInfoOpen)}>
                            추가정보
                        </button>
                    </div>
                    <TimetableDaySelector selectedDay={selectedDay} setSelectedDay={setSelectedDay}/>
                </div>
                <AdjacentStationDirection stationInformation={stationInformation}/>
            </div>
            <TimetableListsContainer selectedDay={selectedDay} stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen}/>
        </div>
    );
};

const TimetableListsContainer = ({selectedDay, stationInformation, additionalInfoOpen}) => {
    return (
        selectedDay == "weekday" ?
        <div className="lists-container timetable">
            <TimetableList selectedDay={selectedDay} direction={"left"}  stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen}/>
            <TimetableList selectedDay={selectedDay} direction={"right"} stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen}/>
        </div> :
        <div className="lists-container timetable">
            <TimetableList selectedDay={selectedDay} direction={"left"}  stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen}/>
            <TimetableList selectedDay={selectedDay} direction={"right"} stationInformation={stationInformation} additionalInfoOpen={additionalInfoOpen}/>
        </div>
    );
};

const TimetableList = ({selectedDay, stationInformation, direction, additionalInfoOpen}) => {
    return (
        <div className={`data-list timetable ${direction}`}>
            {
                stationInformation.timetables[selectedDay][direction]
                .filter((timetable) => timetable.department_time !== null)
                .map((timetable, index) => (
                    <div className = 'data-item-container'>
                        <div className="data-item" key={index}>
                            <span className="time">{timetable.last_station_name}</span>
                            <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                        </div>
                        {
                            additionalInfoOpen && (
                                <div>
                                    <div className='train-id'>열차번호 {timetable.train_id}</div>
                                </div>
                            )
                        }
                        
                    </div>
                ))
            }
        </div>
    );
};