
// 페이지 방문 시 작동할 기본세팅 (data불러오기)
document.addEventListener('DOMContentLoaded', () => {
  // 기본적으로 '오늘' 상태로 설정
  let selectedDateType = 'today';

  // 날짜 선택 박스 이벤트 리스너 추가
  const dateSelect = document.querySelector('#date-select');
  dateSelect.addEventListener('change', async (event) => {
    selectedDateType = event.target.value; // 선택한 날짜 가져오기
  
    // 모든 "로딩 중" 태그를 선택
    const elementsToLoad = [
      '.new-cases',
      '.new-cases-change',
      '.new-recoveries',
      '.new-recoveries-change',
      '.new-deaths',
      '.new-deaths-change'
    ];
  
    // 로딩 클래스 추가
    elementsToLoad.forEach(selector => {
      const element = document.querySelector(selector);
      element.textContent = '로딩 중'; // 기본 텍스트
      element.classList.add('loading','loading-blink'); 
    });
  
    // 데이터 로드
    await fetchCovidData(selectedDateType);
  
    // 로딩 클래스 제거 및 데이터 갱신
    elementsToLoad.forEach(selector => {
      const element = document.querySelector(selector);
      element.classList.remove('loading', 'loading-blink'); 
    });
  });
  

  // 초기 데이터 로드 (오늘 상태로)
  fetchCovidData(selectedDateType);
});




// 서버에서 COVID-19 데이터를 가져오는 함수
async function fetchCovidData(dateType) {
  try {
    const response = await fetch(`/worldwide/covid-data/${dateType}`);

    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }
    const data = await response.json();
    
    // 데이터를 화면에 반영하는 함수 호출
    updateCovidData(data);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// 데이터를 화면에 업데이트하는 함수
function updateCovidData(data) {
  const fields = [
    { selector: '.new-cases', value: data.new_cases, change: data.new_cases_change },
    { selector: '.new-recoveries', value: data.new_recoveries, change: data.new_recoveries_change },
    { selector: '.new-deaths', value: data.new_deaths, change: data.new_deaths_change },
    { selector: '.total-cases', value: data.total_cases, change: data.total_cases_change },
    { selector: '.total-recoveries', value: data.total_recoveries, change: data.total_recoveries_change },
    { selector: '.total-deaths', value: data.total_deaths, change: data.total_deaths_change },
  ];

  fields.forEach(field => {
    document.querySelector(field.selector).textContent = `${Number(field.value).toLocaleString()} 명`;
    updateChange(`${field.selector}-change`, field.change);
  });
}

// 값에 따라 포맷된 텍스트와 클래스 업데이트
function updateChange(selector, value) {
  const element = document.querySelector(selector);
  const number = Number(value);

  // 0인 경우에는 변동 없음
  if (number === 0) {
    element.textContent = `(변동 없음)`;  // 0일 때 표시할 텍스트
    element.classList.add('zero');  // zero 클래스 추가
    element.classList.remove('plus', 'minus');  // plus, minus 클래스 제거
  } else {
    const isPositiveOrZero = number > 0;  // 양수일 경우 plus 클래스, 음수일 경우 minus 클래스
    element.textContent = `(${Math.abs(number).toLocaleString()}${isPositiveOrZero ? ' ▲' : ' ▼'})`;
    element.classList.toggle('plus', isPositiveOrZero);  // 양수일 경우 plus 클래스 추가
    element.classList.toggle('minus', !isPositiveOrZero);  // 음수일 경우 minus 클래스 추가
    element.classList.remove('zero');  // zero 클래스 제거
  }
}




// ----------------검색 기능
document.getElementById('search-input').addEventListener('keydown', function(event) {
  // 엔터 키가 눌렸을 때만 검색
  if (event.key === 'Enter') {
    searchCountries();
  }
});
document.querySelector('.search-icon').addEventListener('click', function() {
  // 검색 아이콘 클릭 시 검색
  searchCountries();
});
document.getElementById('search-input').addEventListener('input', function() {
  // 검색어가 비었으면 전체 리스트를 다시 표시
  if (this.value === '') {
    showAllCountries();
  }
});

function searchCountries() {
  const searchTerm = document.getElementById('search-input').value.toLowerCase(); // 입력한 검색어
  const listItems = document.querySelectorAll('.country-list li'); // 모든 국가 리스트 항목

  // 검색어가 비어 있으면 아무 것도 하지 않음 (change와 충돌방지겸)
  if (searchTerm === '') return;

   // 검색어가 있으면 해당 항목만 표시
  listItems.forEach(item => {
    const countryName = item.querySelector('p strong').textContent.toLowerCase(); // 첫 번째 p 안의 strong 태그 (국가명)
    const countryEnglishName = item.querySelector('.country-english').textContent.toLowerCase(); // 영어 국가명
    if (countryName.includes(searchTerm) || countryEnglishName.includes(searchTerm)) {
      item.classList.remove('hidden'); // 일치하는 항목 표시
    } else {
      item.classList.add('hidden'); // 일치하지 않는 항목 숨김
    }
  });
}

function showAllCountries() {
  const listItems = document.querySelectorAll('.country-list li');
  listItems.forEach(item => {
    item.classList.remove('hidden'); // 모든 항목 표시
  });
}

// --------------

// 국가리스트 클릭 시 서버에 국가명을 보내고 지도값을 받아 html에 적용

document.addEventListener('DOMContentLoaded', function () {
  // fetch로 markerData 받아오기
  fetch('/worldwide/request/marker-data')
    .then(response => response.json())
    .then(markerData => {
      const map = L.map('map-container');
      map.setView([20, 0], 2);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '© OpenStreetMap contributors',
      }).addTo(map);

      const markerCluster = L.markerClusterGroup().addTo(map);

      // markerData를 사용하여 마커 추가
      markerData.forEach(marker => {
          L.marker([marker.lat, marker.lng])
              .bindPopup(`<strong>${marker.country}</strong>`)
              .addTo(markerCluster);
      });

      // GeoJSON 데이터 추가
      fetch('/worldwide/static/data/world_countries.json')
        .then(response => response.json())
        .then(geojsonData => {
            const geojsonLayer = L.geoJson(geojsonData, {
                style: {
                    color: 'transparent',
                    weight: 2,
                    opacity: 0,
                    fillOpacity: 0.3,
                },
                onEachFeature: function (feature, layer) {
                    const countryName = feature.properties.sovereignt || feature.properties.name;
                    layer.bindPopup(`<strong>${countryName}</strong>`);
                },
            }).addTo(map);

            // 국가 리스트 클릭 시 해당 국가로 이동 및 색칠
            const countryListItems = document.querySelectorAll('.country-list li');
            countryListItems.forEach(item => {
                item.addEventListener('click', function () {
                    const lat = parseFloat(item.getAttribute('data-lat'));
                    const lng = parseFloat(item.getAttribute('data-lng'));
                    const countryName = item.getAttribute('data-country').trim();  // 공백 제거

                    if (!lat || !lng || !countryName) {
                        console.error("Invalid country data:", item);
                        return;
                    }

                    map.flyTo([lat, lng], 5);

                    geojsonLayer.eachLayer(function (layer) {
                        const geoJsonCountry = layer.feature.properties.sovereignt || layer.feature.properties.name;
                        const geoJsonNameLong = layer.feature.properties.name_long || '';
                        const geoJsonFormalEn = layer.feature.properties.formal_en || '';
                        const geoJsonNameCiawf = layer.feature.properties.name_ciawf || '';
                        const geoJsonBrkName = layer.feature.properties.brk_name || '';
                        const geoJsonNameKo = layer.feature.properties.name_ko || '';
                        const geoJsonNamePt = layer.feature.properties.name_pt || '';  // 추가된 속성

                        if (!geoJsonCountry) {
                            console.warn("GeoJSON data missing country name:", layer.feature);
                            return;
                        }

                        // 클릭한 국가명에서 괄호를 제거
                        const normalizedCountryName = countryName.trim().toLowerCase().replace(/\(.*\)/, '').trim();
                        
                        // GeoJSON 데이터 속성들 비교
                        const isClickedCountry = [
                            geoJsonCountry,
                            geoJsonNameLong,
                            geoJsonFormalEn,
                            geoJsonNameCiawf,
                            geoJsonBrkName,
                            geoJsonNameKo,
                            geoJsonNamePt  // 비교 항목에 name_pt 추가
                        ].some(name => name.toLowerCase().replace(/\(.*\)/, '').trim() === normalizedCountryName);

                        if (isClickedCountry) {
                            layer.setStyle({
                                fillColor: 'orange',
                                fillOpacity: 0.5,
                                color: 'red',
                                weight: 3
                            });
                            layer.openPopup();
                        } else {
                            layer.setStyle({
                                fillColor: 'transparent',
                                fillOpacity: 0.3,
                                color: 'transparent',
                                weight: 2
                            });
                        }
                    });
                });
            });
        })
        .catch(error => console.error("Error fetching GeoJSON data:", error));
    })
    .catch(error => console.error("Error fetching marker data:", error));
});




// 그래프
const graph = () => {
  const countryListItems = document.querySelectorAll('.country-list li');
  let pieChart;
  countryListItems.forEach(item => {
    item.addEventListener('click', (e) => {
      // 클릭된 li 태그에서 data-country 값을 가져옴
      const country = e.target.closest('li').getAttribute('data-country');
      
      // GET 요청으로 데이터 전송
      fetch(`/worldwide/get-daily-data?country=${country}`, {
        method: 'GET',
      })
      .then(response => response.json())  // 응답을 JSON 형식으로 파싱
      .then(data => {
        // 원형 그래프 그리기
        // 그래프가 이미 존재한다면 삭제
        if (pieChart) {
          pieChart.destroy();
        }
        const ctx = document.getElementById('pieChart').getContext('2d');
          
        pieChart = new Chart(ctx, {
          type: 'pie', // 원형 그래프
          data: {
            labels: ['확진자', '완치자', '사망자'],
            datasets: [{
              label: 'COVID-19 Data',
              data: [data.new_cases, data.new_recoveries, data.new_deaths], // 가져온 데이터
              backgroundColor: ['#FF5733', '#33FF57', '#3357FF'], // 색상
              borderColor: ['#C70039', '#28B463', '#1F77B4'],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function(tooltipItem) {
                    return tooltipItem.label + ': ' + tooltipItem.raw;
                  }
                }
              }
            }
          }
        });
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });
};

graph();
