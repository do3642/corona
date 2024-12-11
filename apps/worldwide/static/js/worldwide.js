
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
      '.new-recovered',
      '.new-recovered-change',
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
    { selector: '.new-recovered', value: 0, change: 0 },
    { selector: '.new-deaths', value: data.new_deaths, change: data.new_deaths_change },
    { selector: '.total-cases', value: data.total_cases, change: data.total_cases_change },
    { selector: '.total-recovered', value: data.total_recovered, change: data.total_recovered_change },
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
  const isPositiveOrZero = number >= 0;

  element.textContent = `(${Math.abs(number).toLocaleString()}${isPositiveOrZero ? ' ▲' : ' ▼'})`;
  element.classList.toggle('plus', isPositiveOrZero);
  element.classList.toggle('minus', !isPositiveOrZero);
}




