import { useState, useEffect, useRef } from 'react';
import './SubwayMap.css';

const SubwayMap = ({isDrawerOpen, setIsDrawerOpen, stationPublicCode, setStationPublicCode}) => {
  const [svgContent, setSvgContent] = useState('');
  const containerRef = useRef(null);
  const [selectedStation, setSelectedStation] = useState(null);
  const [transform, setTransform] = useState({
    scale: 1.2,
    x: -100,
    y: -100,
    dragging: false,
    startX: 0,
    startY: 0
  });

  useEffect(() => {
    const fetchSvg = async () => {
      try {
        const response = await fetch('http://localhost:8000/static/seoul_metro_map_test.svg');
        const svgText = await response.text();
        setSvgContent(svgText);

        // SVG 문자열을 파싱하여 DOM 객체로 변환
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svgText, 'image/svg+xml');
        const svgElement = svgDoc.documentElement;

        // viewBox 속성 설정
        // viewBox="x y width height" 형식
        // x, y는 시작점, width, height는 보여질 영역의 크기
        svgElement.setAttribute('viewBox', '0 0 3600 2500');
        
        // 수정된 SVG를 문자열로 변환
        const serializer = new XMLSerializer();
        const modifiedSvgText = serializer.serializeToString(svgElement);
        
        setSvgContent(modifiedSvgText);
      } catch (error) {
        console.error('SVG 로딩 실패:', error);
      }
    };

    fetchSvg();
  }, []);

  useEffect(() => {
    if (svgContent && containerRef.current) {
      // SVG가 DOM에 마운트된 후에 이벤트 리스너 추가
      const svgWrapper = containerRef.current.querySelector('.svg-wrapper');
      if (svgWrapper) {
        const stations = svgWrapper.querySelectorAll('.station');
        console.log('찾은 역 요소 수:', stations.length);
        
        stations.forEach(station => {
          station.addEventListener('click', (e) => {
            e.stopPropagation();
            handleStationClick(station);
          });
        });
      }
    }
  }, [svgContent]);

  useEffect(() => {
    // wheel 이벤트에 대한 passive 옵션을 false로 설정
    const container = containerRef.current;
    const handleWheelEvent = (e) => {
      e.preventDefault();
      handleWheel(e);
    };

    if (container) {
      container.addEventListener('wheel', handleWheelEvent, { passive: false });
    }

    return () => {
      if (container) {
        container.removeEventListener('wheel', handleWheelEvent);
      }
    };
  }, [transform]); // transform이 의존성 배열에 필요한 경우 추가

  // 휠 이벤트 처리
  const handleWheel = (e) => {
    const delta = e.deltaY;
    const currentScale = transform.scale;
    // 현재 스케일이 최대/최소값일 때 추가 확대/축소 방지
    if ((currentScale >= 4 && delta < 0) || // 최대 확대 상태에서 더 확대하려 할 때
        (currentScale <= 1.2 && delta > 0)) { // 최소 축소 상태에서 더 축소하려 할 때
      e.preventDefault();
      return; // 추가 처리 중단
    }
    const scaleChange = delta > 0 ? 0.9 : 1.1; // 휠 방향에 따라 확대/축소
    const newScale = Math.min(Math.max(transform.scale * scaleChange, 1.2), 4); // 최소 1.2배, 최대 4배

    // 마우스 포인터 위치를 기준으로 확대/축소
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const newX = transform.x - ((mouseX - transform.x) * (scaleChange - 1));
    const newY = transform.y - ((mouseY - transform.y) * (scaleChange - 1));

    setTransform(prev => ({
      ...prev,
      scale: newScale,
      x: newX,
      y: newY
    }));
  };

  // 드래그 시작
  const handleMouseDown = (e) => {
    // 텍스트 선택 방지
    e.preventDefault();
    // SVG가 컨테이너보다 작으면 드래그 시작하지 않음
    // if (!canDrag()) return;
    setTransform(prev => ({
      ...prev,
      dragging: true,
      startX: e.clientX - prev.x,
      startY: e.clientY - prev.y
    }));
  };

//   const canDrag = () => {
//     const container = containerRef.current;
//     if (!container) return false;

//     const svgWrapper = container.querySelector('.svg-wrapper');
//     if (!svgWrapper) return false;

//     // SVG의 실제 크기 계산
//     const svgWidth = svgWrapper.offsetWidth * transform.scale;
//     const svgHeight = svgWrapper.offsetHeight * transform.scale;
//     const containerRect = container.getBoundingClientRect();

//     // SVG가 컨테이너보다 크면 드래그 가능
//     return svgWidth > containerRect.width || svgHeight > containerRect.height;
//   };

  // 드래그 제한 범위 설정
  const getBoundaries = () => {
    const container = containerRef.current;
    if (!container) return { minX: 0, maxX: 0, minY: 0, maxY: 0 };

    const containerRect = container.getBoundingClientRect();
    const svgWrapper = container.querySelector('.svg-wrapper');
    if (!svgWrapper) return { minX: 0, maxX: 0, minY: 0, maxY: 0 };

    // SVG의 실제 크기 계산
    const svgWidth = svgWrapper.offsetWidth * transform.scale;
    const svgHeight = svgWrapper.offsetHeight * transform.scale;

    // 드래그 가능한 범위 계산
    const minX = containerRect.width - svgWidth;
    const minY = containerRect.height - svgHeight;

    return {
      minX: Math.min(0, minX), // 음수값 (왼쪽/위쪽 제한)
      maxX: 0,                 // 0 (오른쪽 제한)
      minY: Math.min(0, minY), // 음수값 (위쪽 제한)
      maxY: 0                  // 0 (아래쪽 제한)
    };
  };

  // 드래그 중
  const handleMouseMove = (e) => {
    if (transform.dragging) {
      const newX = e.clientX - transform.startX;
      const newY = e.clientY - transform.startY;
      // 경계값 계산
      const boundaries = getBoundaries();

      // 경계 내로 제한된 새로운 위치
      const limitedX = Math.min(Math.max(newX, boundaries.minX), boundaries.maxX);
      const limitedY = Math.min(Math.max(newY, boundaries.minY), boundaries.maxY);
      setTransform(prev => ({
        ...prev,
        x: limitedX,
        y: limitedY
      }));
    }
  };

  // 드래그 종료
  const handleMouseUp = () => {
    setTransform(prev => ({
      ...prev,
      dragging: false
    }));
  };

  // 역 클릭 핸들러
  const handleStationClick = (station) => {
    const stationPublicCode = station.getAttribute('data-station-code');
    setSelectedStation(station);
    // Public code 전달
    setStationPublicCode(stationPublicCode);
    // 중앙 정렬
    centerOnElement(station);
  };

  const centerOnElement = (element) => {
    if (!containerRef.current || !element) return;

    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();
    
    // SVG 요소의 위치와 크기 정보 가져오기
    const elementRect = element.getBoundingClientRect();
    
    // 컨테이너의 중심점
    const containerCenterX = containerRect.width / 2;
    const containerCenterY = containerRect.height / 2;
    
    // 요소의 중심점
    const elementCenterX = elementRect.left + elementRect.width / 2;
    const elementCenterY = elementRect.top + elementRect.height / 2;
    
    // 이동해야 할 거리 계산
    const dx = containerCenterX - elementCenterX;
    const dy = containerCenterY - elementCenterY;

    // transform 상태 업데이트
    setTransform(prev => ({
      ...prev,
      x: prev.x + dx,
      y: prev.y + dy
    }));
  };

  return (
    <div 
        className={`subway-map-container ${isDrawerOpen ? 'drawer-open' : ''}`}
        ref={containerRef}
        // onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
    >
        {svgContent && (
            <div 
                className='svg-wrapper'
                dangerouslySetInnerHTML={{ __html: svgContent }} 
                style={{
                    transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
                    transformOrigin: '0 0'
                }}
            />
        )}
    
    </div>
    
  );
};

export default SubwayMap;
