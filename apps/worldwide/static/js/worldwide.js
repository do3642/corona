
// 키워드: 전세계 일간현황, 최초 일간현황 데이터 삽입, 로딩svg삽입,셀렉트 항목 변경
// 페이지 방문 시 작동할 기본세팅 (data불러오기)
document.addEventListener('DOMContentLoaded', () => {
  // 셀렉트 박스 오늘로 설정 (html에서도 선택되어 있지만 데이터 초기값 불러올라고 지정)
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
      element.innerHTML = `
      <svg version="1.1" id="loader-1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
        width="14px" height="14px" viewBox="0 0 40 40" enable-background="new 0 0 40 40" xml:space="preserve">
        <path opacity="0.2" fill="#000" d="M20.201,5.169c-8.254,0-14.946,6.692-14.946,14.946c0,8.255,6.692,14.946,14.946,14.946
          s14.946-6.691,14.946-14.946C35.146,11.861,28.455,5.169,20.201,5.169z M20.201,31.749c-6.425,0-11.634-5.208-11.634-11.634
          c0-6.425,5.209-11.634,11.634-11.634c6.425,0,11.633,5.209,11.633,11.634C31.834,26.541,26.626,31.749,20.201,31.749z"/>
        <path fill="#000" d="M26.013,10.047l1.654-2.866c-2.198-1.272-4.743-2.012-7.466-2.012h0v3.312h0
          C22.32,8.481,24.301,9.057,26.013,10.047z">
          <animateTransform attributeType="xml"
            attributeName="transform"
            type="rotate"
            from="0 20 20"
            to="360 20 20"
            dur="0.5s"
            repeatCount="indefinite"/>
        </path>
      </svg>
    `;
      element.classList.add('loading'); 
    });
  
    // 데이터 로드
    await fetchCovidData(selectedDateType);
  
    // 로딩 클래스 제거 및 데이터 갱신
    elementsToLoad.forEach(selector => {
      const element = document.querySelector(selector);
      element.classList.remove('loading'); 
    });
  });
  

  // 초기 데이터 로드 (오늘 상태로)
  fetchCovidData(selectedDateType);

});



// 키워드: 전세계 일간현황, 어제,오늘,내일에 해당하는 데이터 비동기 요청
// 서버에서 COVID-19 데이터를 가져오는 함수
async function fetchCovidData(dateType) {
  try {
    const response = await fetch(`/worldwide/covid-data/${dateType}`);
    

    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }
    const data = await response.json();
    // console.log(data)
    
    // 데이터를 화면에 반영하는 함수 호출
    updateCovidData(data);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// 키워드: 전세계 일간현황, 숫자 카운터 애니메이션 함수
function animateCount(targetElement, start, end, callback) {
  const randomDuration = Math.random() * 500 + 500; // 500ms ~ 1000ms 사이의 랜덤 지속 시간
  const totalFrames = Math.ceil(randomDuration / 16); // 프레임 수 계산
  let current = start;
  let remainingFrames = totalFrames;

  function stepCount() {
    const randomIncrement = Math.ceil((end - current) / remainingFrames) + Math.floor(Math.random() * 5); 
    current += randomIncrement;

    if (current >= end) {
      current = end; // 목표값 정확하게 도달
      targetElement.textContent = `${current.toLocaleString()} 명`;
      if (callback) callback(current); // 콜백 실행
      return;
    }

    targetElement.textContent = `${current.toLocaleString()} 명`;
    remainingFrames--;
    requestAnimationFrame(stepCount);
  }

  stepCount();
}


//키워드: 전세계 일간현황, 데이터를 화면에 업데이트하는 함수
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
    // document.querySelector(field.selector).textContent = `${Number(field.value).toLocaleString()} 명`;
    const targetElement = document.querySelector(field.selector);
    animateCount(targetElement, 0, Number(field.value), (currentValue) => {
      // 텍스트 업데이트는 애니메이션 중에 이루어짐
      targetElement.textContent = `${currentValue.toLocaleString()} 명`;
    });
    updateChange(`${field.selector}-change`, field.change);
  });
}

// 키워드: 전세계 일간현황, 증가,감소 텍스트 삽입
// 값에 따라 포맷된 텍스트와 클래스 업데이트
function updateChange(selector, value) {
  const element = document.querySelector(selector);
  const number = Number(value);

  // 0인 경우에는 변동 없음
  if (number === 0) {
    element.textContent = `(변동 없음)`; // 0일 때 표시할 텍스트
    element.classList.add('zero'); // zero 클래스 추가
    element.classList.remove('plus', 'minus'); // plus, minus 클래스 제거
  } else {
    const isPositiveOrZero = number > 0; // 양수일 경우 plus 클래스, 음수일 경우 minus 클래스
    const absoluteValue = Math.abs(number);

    // 애니메이션 적용 (0부터 목표 숫자까지 카운트)
    animateCount(element, 0, absoluteValue, (currentValue) => {
      // 애니메이션 중에 값 업데이트
      element.textContent = `(${currentValue.toLocaleString()}${isPositiveOrZero ? ' ▲' : ' ▼'})`;
    });

    // 클래스 토글
    element.classList.toggle('plus', isPositiveOrZero);
    element.classList.toggle('minus', !isPositiveOrZero);
    element.classList.remove('zero'); // zero 클래스 제거
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
                    const countryName = feature.properties.name_ko || feature.properties.sovereignt || feature.properties.name;
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




const graph = () => {
  const countryListItems = document.querySelectorAll('.country-list li');
  const graphViews = document.querySelectorAll('.graph-view');
  let pieCharts = []; // 각 기간에 대해 별도 그래프 저장
  let chartType = 'pie'; // 초기 그래프 타입 설정 (원형 그래프)

  // 그래프 생성 함수
  const createCharts = (country, data) => {
    // 그래프 초기화
    pieCharts.forEach(chart => chart.destroy());
    pieCharts = [];

    // 그래프 데이터를 렌더링
    const periods = ['daily', 'weekly', 'monthly'];
    periods.forEach((period, index) => {
      const graphView = graphViews[index];
      const { new_cases, new_recoveries, new_deaths } = data[period];
      

      // 데이터 렌더링
      const sanitizedData = [new_cases, new_recoveries, new_deaths].map(value => {
        // 값이 숫자 타입으로 강제 변환되도록 함
        value = Number(value);
        return value === 0 ? 0.1 : value;
      });
      const total = sanitizedData.reduce((sum, val) => sum + val, 0);
      graphView.querySelector('.graph-left').innerHTML = `
        <h4>${period === 'daily' ? '일간' : period === 'weekly' ? '주간' : '월간'}</h4>
        <div class="graph-details">
        <p>확진자</p>
        <p>${parseInt(new_cases, 10).toLocaleString()}명</p>
        <p>완치자</p>
        <p>${parseInt(new_recoveries, 10).toLocaleString()}명</p>
        <p>사망자</p>
        <p>${parseInt(new_deaths, 10).toLocaleString()}명</p>
        </div>
      `;

      // 그래프 생성
      const ctx = graphView.querySelector('canvas').getContext('2d');
      const chartLabels = chartType === 'pie' ? [] : ['확진자', '완치자', '사망자'];
      const chartCanvas = graphView.querySelector('canvas');
        if (chartType === 'pie') {
          chartCanvas.width = 250; // 실제 크기
          chartCanvas.height = 150;
          chartCanvas.style.width = '250px'; // 시각적 크기
          chartCanvas.style.height = '150px';
        } else {
          chartCanvas.width = 250;
          chartCanvas.height = 250;
          chartCanvas.style.width = '250px';
          chartCanvas.style.height = '250px';
        }

      const chart = new Chart(ctx, {
        type: chartType, // 동적으로 그래프 타입 설정
        data: {
          labels: chartLabels,
          datasets: [
            {
              label: `${period} COVID-19 Data`,
              data: sanitizedData,
              backgroundColor: ['#ef476f', '#118ab2', '#073b4c'], // 각 구역에 색상 적용
              borderColor: ['#F3722C', '#43AA8B', '#4D908E'],
              borderWidth: 2,
            }
          ]
        },
        options: {
          responsive: true,
          // aspectRatio: chartType === 'pie' ? 1 : 2, // 파이 그래프는 1:1 비율, 나머지 그래프는 2:1 비율로 설정
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              callbacks: {
                label: function (tooltipItem) {
                  const originalValue = tooltipItem.raw; // 실제 값
                  return tooltipItem.label + ': ' + (originalValue === 0.1 ? 0 : originalValue.toLocaleString());
                }
              }
            },
            // datalabels 플러그인 적용
            datalabels: {
              formatter: (value, context) => {
                const percentage = ((value / total) * 100).toFixed(1); // 비율 계산
                return `${percentage}%`; // 데이터 값과 비율 표시
              },
              color: (context) => {
                return '#fff';
              },
              font: {
                weight: 'bold',
                size: 14,
              },
              padding: 5,
            }
          },
          layout: {
            padding: 10
          }
        },
        plugins: [ChartDataLabels] // datalabels 플러그인 사용 명시
      });

      pieCharts.push(chart); // 그래프 저장
    });
  };

  // 국가 데이터 가져오기
  const fetchDataAndRender = (country) => {
    fetch(`/worldwide/get-daily-data?country=${country}`)
      .then(response => response.json())
      .then(data => {
        createCharts(country, data); // 그래프와 데이터 렌더링
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  };

  // 국가 목록 클릭 이벤트
  countryListItems.forEach(item => {
    item.addEventListener('click', (e) => {
      const country = e.target.closest('li').getAttribute('data-country');
      const clickedItem  = e.target.closest('li');

      countryListItems.forEach(el => el.classList.remove('active'));
      clickedItem.classList.add('active');
      // 선택된 상태 표시
      countryListItems.forEach(el => el.classList.remove('selected'));
      e.target.closest('li').classList.add('selected');

      // 데이터 가져와 렌더링
      fetchDataAndRender(country);
    });
  });

  // 그래프 타입 변경 함수
  const changeGraphType = (type) => {
    chartType = type;
    // 그래프 타입 변경 후 다시 그래프 렌더링
    const selectedCountry = document.querySelector('.country-list .selected').getAttribute('data-country');
    fetchDataAndRender(selectedCountry);
  };

  // 버튼 클릭 이벤트 리스너
  document.getElementById('pieGraphBtn').addEventListener('click', () => changeGraphType('pie'));
  document.getElementById('barGraphBtn').addEventListener('click', () => changeGraphType('bar'));
  document.getElementById('lineGraphBtn').addEventListener('click', () => changeGraphType('line'));

  // 초기 화면 설정
  const defaultCountry = 'Republic of Korea';
  const defaultItem = Array.from(countryListItems).find(item => item.getAttribute('data-country') === defaultCountry);
  if (defaultItem) {
    defaultItem.classList.add('selected'); // 선택 상태 표시
    fetchDataAndRender(defaultCountry); // 초기 데이터 렌더링
  }
};

graph();



// 보는 화면에 맞게 지도크기 제어
function adjustMiddleContentHeight() {
  const mapBox = document.querySelector('#map-container');

  const dailyData = document.querySelector('.world-wide-daily');
  const nav = document.querySelector('nav');
  const graphData = document.querySelector('.graph-box')

  const countryList = document.querySelector('.country-list ul');

  const updateBox = document.querySelector('.update-day');
  const searchBox = document.querySelector('.search-box');

  
  // 화면 전체 높이에서 헤더,일간현황,그래프의 높이를 뺀 값 계산
  const availableHeight = window.innerHeight - nav.offsetHeight - dailyData.offsetHeight - graphData.offsetHeight - 25; // 50은 여유 마진값
  const availableHeightLeft = window.innerHeight - nav.offsetHeight - updateBox.offsetHeight - searchBox.offsetHeight - 25;
  mapBox.style.height = `${availableHeight}px`;
  countryList.style.height = `${availableHeightLeft}px`;




}

// 페이지 로드와 리사이즈 시 실행
window.addEventListener('load', adjustMiddleContentHeight);
window.addEventListener('resize', adjustMiddleContentHeight);






document.addEventListener('DOMContentLoaded', () => {
  const updateDayElement = document.querySelector('.update-day');
  const datePopup = document.querySelector('#date-popup');
  const datePicker = document.querySelector('#date-picker');
  const submitDateButton = document.querySelector('#submit-date');
  const cancelDateButton = document.querySelector('#cancel-date');

  // 날짜 범위 정의
  const minDate = new Date('2020-01-04');
  const maxDate = new Date('2024-11-16');

  // 1. .update-day 클릭 시 #date-popup의 hidden 클래스를 토글
  updateDayElement.addEventListener('click', () => {
      // 팝업이 열려 있으면 외부 클릭 이벤트 등록
      datePopup.classList.toggle('hidden');
      if (!datePopup.classList.contains('hidden')) {
          document.addEventListener('click', handleOutsideClick);
      }
  });

  // 2. #submit-date 클릭 시 서버로 선택된 날짜 전송
  submitDateButton.addEventListener('click', () => {
      const selectedDate = datePicker.value;

      if (!selectedDate) {
          alert('날짜를 선택해주세요.');
          return;
      }

      const selectedDateObj = new Date(selectedDate);

      // 선택된 날짜가 범위를 벗어났는지 확인
      if (selectedDateObj < minDate || selectedDateObj > maxDate) {
          alert(`날짜는 ${minDate.toLocaleDateString()} 부터 ${maxDate.toLocaleDateString()} 까지 선택할 수 있습니다.`);
          return;
      }
      console.log(selectedDate)
        // 서버로 날짜 전송 (GET 방식)
      fetch(`/worldwide?date=${selectedDate}`)
      .then(response => {
          if (!response.ok) throw new Error('서버 요청 실패');
          // 응답을 받지 않고, 그냥 성공만 확인
          console.log("날짜 전송 완료");
      })
      .catch(error => {
          console.error('에러 발생:', error);
          alert('날짜 전송 중 오류가 발생했습니다.');
      });


      // 팝업 닫기
      datePopup.classList.add('hidden');
      document.removeEventListener('click', handleOutsideClick); // 외부 클릭 이벤트 제거
  });

  // 3. #cancel-date 클릭 시 팝업 닫기 및 외부 클릭 처리
  cancelDateButton.addEventListener('click', (event) => {
      event.stopPropagation(); // 부모 요소로의 이벤트 전파 방지
      datePopup.classList.add('hidden');
      document.removeEventListener('click', handleOutsideClick); // 외부 클릭 이벤트 제거
  });

  // 외부 클릭 시 팝업 닫기
  function handleOutsideClick(event) {
      if (!datePopup.contains(event.target) && !updateDayElement.contains(event.target)) {
          datePopup.classList.add('hidden');
          document.removeEventListener('click', handleOutsideClick); // 외부 클릭 이벤트 제거
      }
  }

  // 4. #date-popup 내부 클릭 이벤트가 외부로 전파되지 않도록
  datePopup.addEventListener('click', (event) => {
      event.stopPropagation(); // 클릭 이벤트 전파 방지
  });
});
