import { useState, useEffect, memo } from 'react';
import './MetroMap.css';
import MetroMapSVG from '../../assets/seoul_metro_map_test_compress.svg'
// For interactions with svg
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

const transfromConfig = {
  'initialScale': 3,
  'centerOnInit': true,
  'minScale': 1.5,
  'maxScale': 8, 
  'doubleClick': {'disabled': true} // Error raise when click svg after clicking station element in svg
};

const MetroMap = ({setStationPublicCode}) => {
  const [svgContent, setSvgContent] = useState(null);

  useEffect(() => {
    fetchSvg().then(
      (map) => {
        setSvgContent(map);
      });
  }, []);

  useEffect(() => {
    // After mounting svg, add event to station element in SVG
    if (svgContent) {
      const svgWrapper = document.querySelector('.svg-wrapper');
      if (svgWrapper) {
        const stations = svgWrapper.querySelectorAll('.station');
        
        stations.forEach(station => {
          station.addEventListener('click', (e) => {
            e.stopPropagation(); 
            const stationPublicCode = station.getAttribute('data-station-code');
            setStationPublicCode(stationPublicCode);
          });
        });
      }
    }
  }, [svgContent])

  return (
    <div className='svg-container'>
      <TransformWrapper {...transfromConfig}>
        <TransformComponent>
          <div 
              className='svg-wrapper'
              dangerouslySetInnerHTML={{ __html: svgContent }} 
          />
        </TransformComponent>
      </TransformWrapper>
    </div>
  );
}

export default memo(MetroMap); // Avoid re-rendering

// Functions for metro-map
async function fetchSvg() {
  try {
      const response = await fetch(MetroMapSVG);
      const svgText = await response.text();
      return svgText;
  } catch (error) {
      console.error('SVG 로딩 실패:', error);
  }
};