import "./TabSelector.css"

const TabSelector = ({ has_realtimes, tab, setTab }) => {
  return (
    <div className="tab-container">
        {has_realtimes && <TabBadge tabName={"realTime"} selectedTab={tab} setTab={setTab}/>}
        <TabBadge tabName={"schedule"} selectedTab={tab} setTab={setTab}/>
    </div> 
  );
};  

export default TabSelector;

const TabBadge = ({tabName, selectedTab, setTab}) => {
  const tabNameKor = tabName == "realTime" ? "실시간" : "시간표"

  return (
    <div 
      className={`tab ${selectedTab === tabName ? 'selected' : ''}`}
      onClick={() => setTab(tabName)}
    >
      {tabNameKor}
    </div>
  );
};