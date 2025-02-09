import { useState, useEffect } from 'react';
import './Tab.css';

const Tab = ({ tab, stationInformation, realtimeData, setRealtimeData }) => { 
    const [selectedDay, setSelectedDay] = useState('weekday');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const REFRESH_INTERVAL = 15000; // 15초

    const handleRealtimeRefresh = async () => {
        try {
            const response = await fetch(`/api/metro/information/realtimes/${stationInformation.station.station_public_code}`);
            if (!response.ok) throw new Error('Failed to fetch realtime data');
            
            const data = await response.json();
            setRealtimeData(data.station);
            // stationInformation 업데이트
            stationInformation.realtime_station = data;
            
            return data;
        } catch (error) {
            console.error('Error refreshing realtime data:', error);
            throw error;
        }
    };

    const handleRefreshClick = async () => {
        setIsRefreshing(true);
        try {
            await handleRealtimeRefresh();
        } finally {
            setIsRefreshing(false);
        }
    };

    // 자동 새로고침 설정
    useEffect(() => {
        let intervalId;

        if (tab === "realTime") {
            // 컴포넌트 마운트 시 즉시 첫 새로고침
            handleRefreshClick();

            // 15초마다 새로고침
            intervalId = setInterval(() => {
                handleRefreshClick();
                console.log("새로고침 중")
            }, REFRESH_INTERVAL);
        }

        // 클린업 함수
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [tab, stationInformation.station]);
    
    return (
        tab === "realTime" ? (
            <div className="arrival-info">
                <div className="arrival-title">
                    <h3>도착 정보</h3>
                    <div className="arrival-refresh-button-container">
                        <button 
                            className={`arrival-refresh-button ${isRefreshing ? 'refreshing' : ''}`}
                            onClick={handleRefreshClick}
                            disabled={isRefreshing}
                        >
                            새로고침
                        </button>
                    </div>
                </div>
                <div className="arrival-lists-container">
                    <div className="arrival-list left">
                        <div>
                            <span className="direction">
                                {stationInformation.adjacent_stations.left.length > 0 ? (
                                    <span className="station-name-text">
                                    {stationInformation.adjacent_stations.left[0].station_name} 방면
                                    </span> 
                                ) : (
                                    <span>종점</span>
                                )}
                            </span>
                        </div>
                        {
                            realtimeData !== null && realtimeData.left.length > 0 ?
                            realtimeData.left.map((station, index) => (
                                <div className="arrival-item" key={index}>
                                    <span className="direction">{station.last_station_name}</span>
                                    <span className="time">{station.information_message.replace(/\[(\d+)\]/, "$1").replace(/\(.*\)/, "")}</span>
                                </div>
                            ))
                            : <div>
                                정보가 없습니다.
                            </div>
                        }

                    </div>
                    <div className="arrival-list right">
                        <div>
                            <span className="direction">{stationInformation.adjacent_stations.right.length > 0 ? (
                                    <span className="station-name-text">
                                    {stationInformation.adjacent_stations.right[0].station_name} 방면
                                    </span> 
                                ) : (
                                    <span>종점</span>
                                )}</span>
                        </div>
                        {
                            realtimeData !== null && realtimeData.right.length > 0 ?
                            realtimeData.right.map((station, index) => (
                                <div className="arrival-item" key={index}>
                                    <span className="direction">{station.last_station_name}</span>
                                    <span className="time">{station.information_message.replace(/\[(\d+)\]/, "$1").replace(/\(.*\)/, "")}</span>
                                </div>
                            ))
                            : <div>
                                정보가 없습니다.
                            </div>
                        }
                    </div>
                </div>
            </div>
        ):
        (
            <div className="arrival-info">
                <div className="timetable-title">
                    <h3>시간표 정보</h3>
                    <div className="timetable-selector">
                        <button 
                        className={`day-button ${selectedDay === 'weekday' ? 'selected' : ''}`}
                        onClick={() => setSelectedDay('weekday')}
                        >
                            평일
                        </button>
                        <button 
                        className={`day-button ${selectedDay === 'weekend' ? 'selected' : ''}`}
                        onClick={() => setSelectedDay('weekend')}
                        >
                            주말
                        </button>
                    </div>
                </div>
                {
                    selectedDay === 'weekday' ? (
                        <div className="arrival-lists-container">
                            <div className="arrival-list left">
                                {
                                    stationInformation.timetables.weekday.left.filter((timetable) => timetable.department_time !== null).map((timetable, index) => (
                                        <div className="arrival-item" key={index}>
                                            <span className="time">{timetable.last_station_name}</span>
                                            <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                                        </div>
                                    ))
                                }
                            </div>
                            <div className="arrival-list right">
                                {
                                    stationInformation.timetables.weekday.right.filter((timetable) => timetable.department_time !== null).map((timetable, index) => (
                                        <div className="arrival-item" key={index}>
                                            <span className="time">{timetable.last_station_name}</span>
                                            <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                                        </div>
                                    ))
                                }
                            </div>
                        </div>
                    ):(
                        <div className="arrival-lists-container">
                            <div className="arrival-list left">
                                {
                                    stationInformation.timetables.holiday.left.filter((timetable) => timetable.department_time !== null).map((timetable, index) => (
                                        <div className="arrival-item" key={index}>
                                            <span className="time">{timetable.last_station_name}</span>
                                            <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                                        </div>
                                    ))
                                }
                            </div>
                            <div className="arrival-list right">
                                {
                                    stationInformation.timetables.holiday.right.filter((timetable) => timetable.department_time !== null).map((timetable, index) => (
                                        <div className="arrival-item" key={index}>
                                            <span className="time">{timetable.last_station_name}</span>
                                            <span className="direction">{timetable.department_time.replace(/(\d{2}):(\d{2}):(\d{2})/, '$1:$2')}</span>
                                        </div>
                                    ))
                                }
                            </div>
                        </div>
                    )
                }
            </div>
        )
    );
}

export default Tab;
