import { useState, useEffect, useRef } from 'react';
import './SearchBar.css';

const SearchBar = ({stationPublicCode, setStationPublicCode}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [dropdownData, setDropdownData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // 1. 데이터 가져오기
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/subways/search/stations");
        const data = await response.json();
        setDropdownData(data);
        setFilteredData(data);
      } catch (error) {
        console.error("Error fetching dropdown data:", error);
      }
    };

    fetchData();
  }, []);

  // 2. 검색어 필터링
  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredData([]);
    } else {
      const lowerCaseQuery = searchQuery.toLowerCase();
      const filtered = dropdownData.filter((item) =>
        item.station_name.toLowerCase().includes(lowerCaseQuery)
      );
      setFilteredData(filtered);
    }
  }, [searchQuery, dropdownData]);

  // 3. 드롭다운 항목 클릭 처리
  const handleItemClick = (station) => {
    setSearchQuery(station.station_name);
    setStationPublicCode(station.station_public_code);
    setIsDropdownOpen(false);
  };

  // 드롭다운 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="search-dropdown-container" ref={dropdownRef}>
      <input
        type="text"
        placeholder="Search station..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onFocus={() => setIsDropdownOpen(true)}
        className="search-input"
      />

      {isDropdownOpen && (
        <div className="dropdown-menu">
          {filteredData.length > 0 ? (
            filteredData.map((item) => (
              <div
                key={item.station_public_code}
                className="dropdown-item"
                onClick={() => handleItemClick(item)}
              >
                <span className="station-info">
                  {item.station_name} {item.line_name}
                </span>
                <div
                  className="line-indicator"
                  style={{ backgroundColor: `#${item.line_color}` }}
                ></div>
              </div>
            ))
          ) : (
            <div className="no-results">검색 결과가 없습니다.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;