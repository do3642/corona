// ----------------유틸리티 함수 (국가리스트 선택자)
function getCountryListItems() {
  return document.querySelectorAll('.country-list li'); // 국가 리스트 항목 가져오기
}

// -----------------svg 리턴함수
function getLoadingSVG() {
  return `
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
}


// '오늘','어제','내일','내일(예측) 코로나 데이터 호출 및 로딩중 표시
document.addEventListener('DOMContentLoaded', () => {

  // 기본값 설정
  let selectedDateType = 'today';
  const dateSelect = document.querySelector('#date-select');
    // 데이터가 들어갈 위치 선택 (로딩중을 표시하려고)
  const elementsToLoad = document.querySelectorAll('[data-loading-target]');


  dateSelect.addEventListener('change', async (event) => {
    selectedDateType = event.target.value;
  
    // 로딩 클래스 추가 및 svg 삽입
    elementsToLoad.forEach(element  => {
      element.innerHTML = getLoadingSVG(); 
      element.classList.add('loading'); 
    });
    // 데이터 로드
    await fetchCovidData(selectedDateType);
    // 로딩 클래스 제거 및 데이터 갱신
    elementsToLoad.forEach(element => {
      element.classList.remove('loading'); 
    });
  });
  // 초기 데이터 로드 (오늘 상태로)
  fetchCovidData(selectedDateType);
});

// 서버에서 COVID-19 전세계 일일 데이터를 가져오는 함수
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
    console.log("fetchCovidData함수를 통해 데이터 호출 실패했습니다.")
  }
}

// 전세계 일간현황 숫자 카운터 애니메이션 함수
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


//전세계 일간현황 데이터를 화면에 업데이트하는 함수
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
    animateCount(targetElement, 0, Number(field.value)); 
    updateChange(`${field.selector}-change`, field.change);
  });
}

// 값에 따라 포맷된 텍스트와 클래스 업데이트 (증가량,감소량 표기)
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

// 폼 제출 시 검색 처리 (엔터,아이콘 클릭)
document.getElementById('search-form').addEventListener('submit', function(event) {
  event.preventDefault();  // 기본 폼 제출 방지
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
  const listItems = getCountryListItems(); // 모든 국가 리스트 항목

  // 검색어가 비어 있으면 아무 것도 하지 않음 (change와 충돌방지겸)
  if (searchTerm === '') return;

   // 검색어가 있으면 해당 항목만 표시
  listItems.forEach(item => {
    const countryName = item.querySelector('p strong').textContent.toLowerCase(); // 첫 번째 p 안의 strong 태그 (한글 국가명)
    const countryEnglishName = item.querySelector('.country-english').textContent.toLowerCase(); // 영어 국가명
    if (countryName.includes(searchTerm) || countryEnglishName.includes(searchTerm)) {
      item.classList.remove('hidden'); // 일치하는 항목 표시
    } else {
      item.classList.add('hidden'); // 일치하지 않는 항목 숨김
    }
  });
}

function showAllCountries() {
  const listItems = getCountryListItems();
  listItems.forEach(item => {
    item.classList.remove('hidden'); // 모든 항목 표시
  });
}

// --------------

// 국가리스트 클릭 시 서버에 국가명을 보내고 지도값을 받아 html에 적용

document.addEventListener('DOMContentLoaded', function () {
  // 데이터를 병렬로 fetch
  Promise.all([
    fetch('/worldwide/request/marker-data').then(res => res.json()),
    fetch('/worldwide/static/data/world_countries.json').then(res => res.json()),
  ])
    .then(([markerData, geojsonData]) => {
      // 맵 초기화
      const map = L.map('map-container').setView([20, 0], 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors',
      }).addTo(map);

      // 마커 클러스터 추가
      const markerCluster = L.markerClusterGroup().addTo(map);
      markerData.forEach(marker => {
        const leafletMarker = L.marker([marker.lat, marker.lng]).bindPopup(`<strong>${marker.country}</strong>`);
        leafletMarker.on('popupopen', () => createRippleEffect(leafletMarker));
        markerCluster.addLayer(leafletMarker);
      });

      // GeoJSON 레이어 추가
      const geojsonLayer = L.geoJson(geojsonData, {
        style: {
          color: 'transparent',
          weight: 2,
          opacity: 0,
          fillOpacity: 0.3,
        },
        onEachFeature: (feature, layer) => {
          const countryName = feature.properties.name_ko || feature.properties.sovereignt || feature.properties.name;
          layer.bindPopup(`<strong>${countryName}</strong>`);
          layer.on('popupopen', () => createRippleEffect(layer));
        },
      }).addTo(map);

      // 국가 리스트 클릭 이벤트
      const countryListItems = getCountryListItems();
      countryListItems.forEach(item => {
        item.addEventListener('click', () => {
          const lat = parseFloat(item.dataset.lat);
          const lng = parseFloat(item.dataset.lng);
          const countryName = item.dataset.country.trim();

          if (!lat || !lng || !countryName) {
            console.error("Invalid country data:", item);
            return;
          }

          map.flyTo([lat, lng], 5);

          geojsonLayer.eachLayer(layer => {
            const countryProps = layer.feature.properties;
            const possibleNames = [
              countryProps.sovereignt,
              countryProps.name,
              countryProps.name_long,
              countryProps.formal_en,
              countryProps.name_ciawf,
              countryProps.brk_name,
              countryProps.name_ko,
              countryProps.name_pt,
            ].filter(Boolean); // null/undefined 속성 제거
           
            const normalizedCountryName = countryName.toLowerCase().replace(/\(.*\)/, '').trim();
            const isClickedCountry = possibleNames.some(ctyname =>
              ctyname.toLowerCase().replace(/\(.*\)/, '').trim() === normalizedCountryName,
            );
          
            layer.setStyle({
              fillColor: isClickedCountry ? 'orange' : 'transparent',
              fillOpacity: isClickedCountry ? 0.5 : 0.3,
              color: isClickedCountry ? 'red' : 'transparent',
              weight: isClickedCountry ? 3 : 2,
            });
          
            if (isClickedCountry) layer.openPopup();
          });
        });
      });
    })
    .catch(error => {
      console.error("Error fetching data:", error);
      alert("지도를 로드하는 중 문제가 발생했습니다. 다시 시도해주세요.");
    });

  // 팝업에 물결 효과를 추가하는 함수
  function createRippleEffect(target) {
    const popupContainer = target.getPopup().getElement();
    if (!popupContainer.querySelector('.ripple-effect')) {
      const ripple = document.createElement('div');
      ripple.classList.add('ripple-effect');
      ripple.addEventListener('animationend', () => ripple.remove());
      popupContainer.appendChild(ripple);
    }
  }
});




const graph = () => {
  const countryListItems = getCountryListItems();
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
  // const nav = document.querySelector('nav');
  const graphData = document.querySelector('.graph-box')

  const countryList = document.querySelector('.country-list ul');

  const updateBox = document.querySelector('.update-day');
  const searchBox = document.querySelector('.search-box');

  
  // 화면 전체 높이에서 헤더,일간현황,그래프의 높이를 뺀 값 계산
  const availableHeight = window.innerHeight  - dailyData.offsetHeight - graphData.offsetHeight - 25; // 50은 여유 마진값
  const availableHeightLeft = window.innerHeight - updateBox.offsetHeight - searchBox.offsetHeight - 25;
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
        // 서버로 날짜 전송 (GET 방식)
      fetch(`/worldwide/data?date=${selectedDate}`)
      .then(response => {
          if (!response.ok) throw new Error('서버 요청 실패');
          return response.json(); // JSON 응답을 반환받음
      })
      .then(data => {
          console.log("서버로부터 받은 데이터:", data);
          updateDOM(data); // 받은 데이터를 DOM에 반영
          
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
function updateDOM(data) {
  // 1. 업데이트 날짜
  document.querySelector('.update-day p:nth-child(2)').textContent = `${data.date_reported} 11:00`;

  // 2. 국가 리스트 업데이트
  const countryList = document.querySelector('.country-list ul');
  
  // 3. 국가별 데이터 갱신
  data.records.forEach((record, index) => {
      // 국가별 감염률 찾기
      const countryPercentage = data.country_percentages.find(
          p => p.country === record.country
      );

      // 각 국가 항목 (li)에서 필요한 부분만 갱신
      const listItem = countryList.children[index];

      // 국가명, 감염률, 일간 현황, 누적 현황 갱신
      listItem.querySelector('.country-name strong').textContent = record.country_korean;
      listItem.querySelector('.country-name .country-english').textContent = record.country;
      listItem.querySelector('.infection-rate span').textContent = `${countryPercentage ? countryPercentage.percentage : 0}%`;
      listItem.querySelector('.daily-status span').innerHTML = `<strong>${record.new_cases.toLocaleString()}</strong> | ${record.new_deaths.toLocaleString()}`;
      listItem.querySelector('.cumulative-status span').innerHTML = `<strong>${record.cumulative_cases.toLocaleString()}</strong> | ${record.cumulative_deaths.toLocaleString()}`;
  });
}




document.addEventListener('DOMContentLoaded', function () {


  // 탭 전환 로직
  function setupTabs(tabs, contents) {
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        // 모든 탭과 콘텐츠에서 활성화 제거
        tabs.forEach(t => t.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));

        // 선택된 탭과 해당 콘텐츠에 활성화 추가
        tab.classList.add('active');
        contents[index].classList.add('active');
      });
    });
  }

  // 버튼과 콘텐츠 선택
  const tabButtons = [document.querySelector('.news'), document.querySelector('.test-btn')];
  const tabContents = [document.querySelector('.crw'), document.querySelector('.test')];

  // 탭 설정
  setupTabs(tabButtons, tabContents);

  // 토글 버튼 로직
  function setupToggleButtons() {
    // 모든 토글 버튼 선택
    const toggleButtons = document.querySelectorAll('.toggle-button');
    
    toggleButtons.forEach((toggleButton) => {
      let isRippleActive = false; // 리플 효과가 활성화되었는지 추적하는 변수


      toggleButton.addEventListener('click', () => {
        // data-action 속성을 사용하여 각 버튼의 동작을 다르게 설정
        const action = toggleButton.dataset.action; // 예: 'dark-mode', 'light-mode', 'custom-action' 등
        
        // 예시로 각 동작을 처리
        if (action === 'toggle-dark-light') {
          // 다크 모드 / 라이트 모드 전환
          document.body.classList.toggle('dark-mode');
          document.body.classList.toggle('light-mode');

        } else if (action === 'toggle-mouse-action') {
          if (!isRippleActive) {
            // 리플 효과 활성화
            $('body').ripples({
              dropRadius: 50,
              perturbance: 0.04
            });
            isRippleActive = true; // 리플 효과 활성화 상태로 변경
          } else {
            // 리플 효과 비활성화
            $('body').ripples('destroy'); // 리플 효과 제거
            isRippleActive = false; // 리플 효과 비활성화 상태로 변경
          }
         
        } else if (action === 'toggle-cursor-action') {
          toggleCursorEffect();

        } else if (action === 'toggle-btn-action'){
          
        }
        
        // 각 버튼에 대해서 추가적인 동작을 더 추가할 수 있음
        toggleButton.classList.toggle('open');
      });
    });
  }

  // 토글 버튼 설정
  setupToggleButtons();
});

// 개별 파티클을 처리하는 클래스
class PointerParticle {
  constructor(spread, speed, component) {
    const { ctx, pointer, hue } = component;

    // 파티클의 기본 속성 초기화
    this.ctx = ctx;  // 캔버스의 2D 컨텍스트
    this.x = pointer.x;  // 마우스 X 좌표
    this.y = pointer.y;  // 마우스 Y 좌표
    this.mx = pointer.mx * 0.1;  // 마우스 이동 X 속도 (감쇠)
    this.my = pointer.my * 0.1;  // 마우스 이동 Y 속도 (감쇠)
    this.size = Math.random() + 1;  // 랜덤 크기 설정
    this.decay = 0.01;  // 파티클 크기 감소값
    this.speed = speed * 0.08;  // 속도 설정
    this.spread = spread * this.speed;  // 확산 정도
    this.spreadX = (Math.random() - 0.5) * this.spread - this.mx;  // X 방향으로의 확산
    this.spreadY = (Math.random() - 0.5) * this.spread - this.my;  // Y 방향으로의 확산
    this.color = `hsl(${hue}deg 90% 60%)`;  // 색상 설정 (HSL)
  }

  // 파티클을 그리는 메소드
  draw() {
    this.ctx.fillStyle = this.color;  // 색상 설정
    this.ctx.beginPath();  // 경로 시작
    this.ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);  // 원을 그리기
    this.ctx.fill();  // 채우기
  }

  // 파티클의 크기를 감소시키는 메소드
  collapse() {
    this.size -= this.decay;  // 크기 감소
  }

  // 파티클의 이동 경로를 설정하는 메소드
  trail() {
    this.x += this.spreadX * this.size;  // X 방향으로 이동
    this.y += this.spreadY * this.size;  // Y 방향으로 이동
  }

  // 파티클을 업데이트하는 메소드 (그리기, 이동, 크기 감소)
  update() {
    this.draw();  // 파티클 그리기
    this.trail();  // 파티클 이동
    this.collapse();  // 파티클 크기 감소
  }
}

// PointerParticles 컴포넌트 클래스 (커스텀 HTML 엘리먼트)
class PointerParticles extends HTMLElement {
  // 커스텀 엘리먼트를 등록하는 메소드
  static register(tag = "pointer-particles") {
    if ("customElements" in window) {
      customElements.define(tag, this);
    }
  }

  // CSS 스타일 (shadow DOM에서 사용할 스타일)
  static css = `
    :host {
      display: grid;
      width: 100%;
      height: 100%;
      pointer-events: none;  // 마우스 이벤트를 캔버스로 전달
    }
  `;

  // 생성자에서 초기 설정
  constructor() {
    super();

    // 초기화할 속성들
    this.canvas;
    this.ctx;
    this.fps = 60;  // FPS (초당 프레임 수)
    this.msPerFrame = 1000 / this.fps;  // 한 프레임에 소요되는 시간
    this.timePrevious;
    this.particles = [];  // 생성된 파티클을 저장할 배열
    this.pointer = { x: 0, y: 0, mx: 0, my: 0 };  // 마우스 좌표 및 이동 속도
    this.hue = 0;  // 색상
  }

  // 컴포넌트가 DOM에 연결되었을 때 호출되는 메소드
  connectedCallback() {
    const canvas = document.createElement("canvas");  // 캔버스 생성
    const sheet = new CSSStyleSheet();  // 스타일 시트 생성

    this.shadowroot = this.attachShadow({ mode: "open" });  // shadow DOM을 열어서 스타일을 적용
    sheet.replaceSync(PointerParticles.css);  // CSS 적용
    this.shadowroot.adoptedStyleSheets = [sheet];  // 스타일 시트를 shadow DOM에 적용
    this.shadowroot.append(canvas);  // 캔버스 추가

    this.canvas = this.shadowroot.querySelector("canvas");  // 캔버스를 가져오기
    this.ctx = this.canvas.getContext("2d");  // 2D 렌더링 컨텍스트 가져오기
    // 부모 요소가 있을 때만 setCanvasDimensions을 호출
    if (this.parentNode) {
      this.setCanvasDimensions();  // 캔버스 크기 설정
    } else {
      // 부모 요소가 없을 때 처리 (예: 일시적인 대기 후 재시도)
      this.observeParentNode();  // 부모 요소가 추가되면 크기 설정
    }
    this.setupEvents();  // 이벤트 설정
    this.timePrevious = performance.now();  // 현재 시간 기록
    this.animateParticles();  // 애니메이션 시작
  }
  setCanvasDimensions() {
    // 부모 요소가 있을 때만 getBoundingClientRect를 호출
    const rect = this.parentNode ? this.parentNode.getBoundingClientRect() : { width: 0, height: 0 };
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }
  observeParentNode() {
    const observer = new MutationObserver(() => {
      if (this.parentNode) {
        this.setCanvasDimensions();  // 부모 노드가 추가되면 크기 설정
        observer.disconnect();  // 부모 노드가 설정되면 관찰 종료
      }
    });
  
    // 부모 노드가 추가되는 변화를 관찰
    observer.observe(this, { childList: true, subtree: true });
  }


  // 파티클 생성하는 메소드
  createParticles(event, { count, speed, spread }) {
    this.setPointerValues(event);  // 마우스 좌표 및 속도 설정

    // 지정된 수의 파티클 생성
    for (let i = 0; i < count; i++) {
      this.particles.push(new PointerParticle(spread, speed, this));  // 새로운 파티클 생성
    }
  }

  // 마우스 좌표 및 속도 설정하는 메소드
  setPointerValues(event) {
    this.pointer.x = event.x - this.offsetLeft;  // 마우스 X 좌표
    this.pointer.y = event.y - this.offsetTop;  // 마우스 Y 좌표
    this.pointer.mx = event.movementX;  // 마우스 X 이동 속도
    this.pointer.my = event.movementY;  // 마우스 Y 이동 속도
  }

  // 마우스 이벤트 설정 (클릭, 이동 등)
  setupEvents() {
    const parent = this.parentNode;  // 부모 요소

    parent.addEventListener("click", (event) => {
      this.createParticles(event, {
        count: 300,  // 생성할 파티클 수
        speed: Math.random() + 1,  // 파티클 속도 (랜덤)
        spread: Math.random() + 50  // 파티클 확산 범위 (랜덤)
      });
    });

    // 마우스 이동 이벤트
    parent.addEventListener("pointermove", (event) => {
      this.createParticles(event, {
        count: 20,  // 생성할 파티클 수
        speed: this.getPointerVelocity(event),  // 파티클 속도
        spread: 1  // 파티클 확산 범위
      });
    });

    // 윈도우 크기 변경 시 캔버스 크기 조정
    window.addEventListener("resize", () => this.setCanvasDimensions());
  }

  // 마우스 속도 계산하는 메소드
  getPointerVelocity(event) {
    const a = event.movementX;  // X 방향 이동량
    const b = event.movementY;  // Y 방향 이동량
    const c = Math.floor(Math.sqrt(a * a + b * b));  // 속도 계산 (Pythagorean theorem)

    return c;  // 속도 반환
  }

  // 파티클들을 처리하는 메소드 (업데이트)
  handleParticles() {
    for (let i = 0; i < this.particles.length; i++) {
      this.particles[i].update();  // 각 파티클 업데이트

      // 크기가 0.1 이하인 파티클은 삭제
      if (this.particles[i].size <= 0.1) {
        this.particles.splice(i, 1);  // 배열에서 파티클 제거
        i--;  // 인덱스 조정
      }
    }
  }

  // 캔버스 크기 설정
  setCanvasDimensions() {
    const rect = this.parentNode.getBoundingClientRect();  // 부모 요소의 크기 계산

    this.canvas.width = rect.width;  // 캔버스 너비 설정
    this.canvas.height = rect.height;  // 캔버스 높이 설정
  }

  // 파티클 애니메이션 메소드
  animateParticles() {
    requestAnimationFrame(() => this.animateParticles());  // 다음 프레임 요청

    const timeNow = performance.now();  // 현재 시간
    const timePassed = timeNow - this.timePrevious;  // 이전 시간과의 차이

    if (timePassed < this.msPerFrame) return;  // 프레임 시간보다 빠르면 종료

    const excessTime = timePassed % this.msPerFrame;  // 초과 시간 계산
    this.timePrevious = timeNow - excessTime;  // 이전 시간 갱신

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);  // 캔버스 클리어
    this.hue = this.hue > 360 ? 0 : (this.hue += 3);  // 색상 변경

    this.handleParticles();  // 파티클 처리
  }
}

// // PointerParticles 컴포넌트를 등록
// PointerParticles.register();
// PointerParticles 컴포넌트를 등록
PointerParticles.register();  // 이 부분을 추가하세요.

// 마우스 커서 효과 활성화 함수
function toggleCursorEffect() {
  const existingParticles = document.querySelector('pointer-particles');

  if (existingParticles) {
    // 이미 존재하면, 효과를 비활성화 (삭제)
    existingParticles.remove();
  } else {
    // PointerParticles 커스텀 엘리먼트를 생성
    const particlesElement = document.createElement('pointer-particles');
    
    // particlesElement의 스타일 추가
    particlesElement.style.position = 'absolute';
    particlesElement.style.top = '0';
    particlesElement.style.left = '0';
    particlesElement.style.width = '100%';
    particlesElement.style.height = '100%';
    particlesElement.style.pointerEvents = 'none';  // 마우스 이벤트를 캔버스로 전달
    
    document.body.appendChild(particlesElement); // body에 추가
  }
}
