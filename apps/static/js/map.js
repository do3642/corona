// map.js에서 불필요한 코드 제거

// 병원 데이터 처리
const hospitalData = JSON.parse(hospitals); // 병원 데이터 파싱

// 마커 추가
hospitalData.forEach(function(hospital) {
  if (hospital.lat && hospital.lng) {
    // 마커 위치 설정
    const markerPosition = new kakao.maps.LatLng(hospital.lat, hospital.lng);
    
    // 마커 생성
    const marker = new kakao.maps.Marker({
      position: markerPosition,
      map: map,
      title: hospital.name
    });

    // 정보창 내용 설정
    const infowindow = new kakao.maps.InfoWindow({
      content: `<div style="padding:5px;">${hospital.name}<br>${hospital.address}<br>전화: ${hospital.tel || '정보 없음'}</div>`
    });

    // 마커에 마우스 오버 이벤트 추가
    kakao.maps.event.addListener(marker, 'mouseover', function() {
      infowindow.open(map, marker); // 정보창 열기
    });

    // 마커에 마우스 아웃 이벤트 추가
    kakao.maps.event.addListener(marker, 'mouseout', function() {
      infowindow.close(); // 정보창 닫기
    });
  }
});
