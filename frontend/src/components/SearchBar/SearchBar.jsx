import { useState, useEffect, useRef } from 'react';
import CONFIG from "../Config"
import './SearchBar.css';

const SearchBar = ({setStationPublicCode, setIsPanelOpen}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [dropdownData, setDropdownData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Get dropdown data
  useEffect(() => {
    fetchStationData().then((data) => {
      setDropdownData(data);
      setFilteredData(data);
    })
  }, []);

  // Filtering
  useEffect(() => {
    setFilteredData(filterData(searchQuery, dropdownData));
  }, [searchQuery, dropdownData]);

  // Close dropdown when clicking outside of the dropdown
  useEffect(() => {
    const searchDropdownContainer = document.querySelector(".search-dropdown-container");
    const handleClickOutside = (event) => {
      if (searchDropdownContainer && !searchDropdownContainer.contains(event.target)) {
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
      <SearchBarInput searchQuery={searchQuery} setSearchQuery={setSearchQuery} setIsDropdownOpen={setIsDropdownOpen}/>
      <DropdownMenu 
        isDropdownOpen={isDropdownOpen} 
        filteredData={filteredData} 
        onClick = {(station) => {
          setSearchQuery(station.station_name);
          setStationPublicCode(station.station_public_code);
          setIsPanelOpen(true);
          setIsDropdownOpen(false);
        }}
      />
    </div>
  );
};

export default SearchBar;

const fetchStationData = async () => {
  try {
    const response = await fetch(CONFIG.searchStations);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching dropdown data:", error);
  }
};

// Filtering dropdown data
const filterData = (searchQuery, dropdownData) => {
  // Filtering logic
  if (searchQuery.trim() === "") {
    return [];
  } else {
    const lowerCaseQuery = searchQuery.toLowerCase();
    const filtered = dropdownData.filter((item) =>
      item.station_name.toLowerCase().includes(lowerCaseQuery)
    );
    return filtered;
  }
};

const SearchBarInput = ({searchQuery, setSearchQuery, setIsDropdownOpen}) => {
  return (
    <input
      type="text"
      placeholder="역명을 입력해주세요."
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      onFocus={() => setIsDropdownOpen(true)}
      className="search-input"
    />
  );
}

const DropdownMenu = ({isDropdownOpen, filteredData, onClick}) => {
  if (isDropdownOpen) {
    return (
      <div className='dropdown-menu-container'>
        <div className="dropdown-menu">
          {filteredData.length > 0 ? (
            filteredData.map((station) => (
              <DropdownItem 
                station={station} 
                onClick={() => onClick(station)}
              />
            ))
          ) : (
            <div className="no-results">검색 결과가 없습니다.</div>
          )}
        </div>
      </div>
        
    );
  }
};

const DropdownItem = ({station, onClick}) => {
  return (
    <div
      key={station.station_public_code}
      className="dropdown-item"
      onClick={onClick}
    >
      <div
        className="line-indicator"
        style={{ backgroundColor: `#${station.line_color}` }}
      ></div>
      <span className="station-info">
        {station.station_name} {station.line_name}
      </span>
    </div>
  );
};