function onEachFeature(feature, layer) {
  layer.on('click', function () {
      var regionName = feature.properties.CTP_KOR_NM;
      if (regionName) {
          // 클릭 시 페이지 이동
          window.location.href = '/domestic/' + encodeURIComponent(regionName);
      }
  });
}

function addMapEventListeners() {
  // 지도 객체 확인
  if (!window.map) {
      console.error("Map object is not initialized.");
      return;
  } else {
    console.log(window.map)
    console.log(window.map.layer)
  }

  // 각 레이어에 이벤트 추가
  if (typeof window.map.eachLayer === 'function') {
      window.map.eachLayer(function (layer) {
          if (layer.feature && layer.feature.properties) {
              onEachFeature(layer.feature, layer);
          }
      });
  } else {
      console.error("eachLayer is not a function on the map object.");
  }
}

// DOMContentLoaded 이후 이벤트 바인딩
document.addEventListener("DOMContentLoaded", function () {
  if (window.map) {
      console.log("Adding event listeners to the map.");
      addMapEventListeners();
  } else {
      console.error("Map object is not available yet. Check initialization.");
  }
});
